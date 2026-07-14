import argparse
import json
import sys
from datetime import date

import joblib
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score, roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

# ================================================================================
# CONFIGURACIÓN INICIAL
# ================================================================================

RANDOM_STATE = 42

# Columnas excluidas por fuga de datos (ver Sección 2 del notebook)
COLUMNAS_FUGA = ["estado_entrega", "tipo_transaccion"]

NUMERICAS_BASE = [
    "dias_envio_real", "dias_envio_prog", "beneficio_pedido", "ventas_cliente",
    "precio_base", "margen_ganancia_item", "cantidad", "ventas", "total_item",
    "ganancia_pedido",
]
NUMERICAS_DERIVADAS = [
    "diferencia_envio", "ratio_envio", "precio_promedio_item", "margen_total",
    "eficiencia_cliente", "riesgo_por_precio",
]
BINARIAS = ["riesgo_retraso", "es_anomalia", "es_outlier", "cumple_plazo"]
NOMINAL_BAJA_CARD = ["modo_envio", "cluster_kmeans"]
# 'cluster_dbscan' se descarta: no está implementado en el pipeline no
# supervisado actual (KMEANSCERCER.py solo calcula KMeans).
NOMINAL_ALTA_CARD = ["categoria", "region_destino"]


# ================================================================================
# CONEXIÓN A SQL SERVER
# ================================================================================

def conectar_sql_server(server: str, database: str) -> object:
    """
    Establece conexión con SQL Server usando autenticación integrada.
    
    Args:
        server: Nombre del servidor SQL (ej. OMEGA-DELL)
        database: Nombre de la base de datos (ej. BD_ML_RELACIONAL)
    
    Returns:
        engine: Objeto de conexión SQLAlchemy
    """
    connection_string = (
        f"mssql+pyodbc://@{server}/{database}"
        "?driver=ODBC+Driver+18+for+SQL+Server"
        "&trusted_connection=yes"
        "&TrustServerCertificate=yes"
    )
    
    engine = create_engine(connection_string)
    return engine


def cargar_datos_desde_sql(engine: object, stored_procedure: str = "sp_DatasetML") -> pd.DataFrame:
    """
    Carga datos desde SQL Server ejecutando un stored procedure.
    
    Args:
        engine: Conexión SQLAlchemy
        stored_procedure: Nombre del stored procedure a ejecutar
    
    Returns:
        DataFrame con los datos cargados
    """
    print(f"Ejecutando stored procedure: {stored_procedure}")
    query = text(f"EXEC {stored_procedure}")
    df = pd.read_sql(query, engine)
    print(f"Datos cargados: {len(df)} registros, {len(df.columns)} columnas")
    return df


# ================================================================================
# FUNCIONES DE PREPROCESAMIENTO
# ================================================================================

def ingenieria_features(df: pd.DataFrame, medianas: dict | None = None):
    """Crea las variables derivadas de la Sección 4 del notebook.

    Si `medianas` es None (modo entrenamiento), las medianas se calculan y se
    devuelven para guardarlas. Si se pasan (modo inferencia), se reutilizan
    las medianas de entrenamiento en vez de recalcularlas.
    """
    df = df.copy()
    calcular_medianas = medianas is None
    if calcular_medianas:
        medianas = {}

    df["diferencia_envio"] = df["dias_envio_real"] - df["dias_envio_prog"]

    ratio = df["dias_envio_real"] / df["dias_envio_prog"].replace(0, np.nan)
    if calcular_medianas:
        medianas["ratio_envio"] = float(ratio.median())
    df["ratio_envio"] = ratio.fillna(medianas["ratio_envio"])

    df["cumple_plazo"] = (df["dias_envio_real"] <= df["dias_envio_prog"]).astype(int)

    precio_prom = df["ventas"] / df["cantidad"].replace(0, np.nan)
    if calcular_medianas:
        medianas["precio_promedio_item"] = float(precio_prom.median())
    df["precio_promedio_item"] = precio_prom.fillna(medianas["precio_promedio_item"])

    margen = df["ganancia_pedido"] / df["ventas"].replace(0, np.nan)
    df["margen_total"] = margen.fillna(0)

    eficiencia = df["ventas_cliente"] / df["cantidad"].replace(0, np.nan)
    if calcular_medianas:
        medianas["eficiencia_cliente"] = float(eficiencia.median())
    df["eficiencia_cliente"] = eficiencia.fillna(medianas["eficiencia_cliente"])

    df["riesgo_por_precio"] = df["riesgo_retraso"].astype(int) * df["precio_base"]

    return df, medianas


def construir_X_y(df: pd.DataFrame):
    """Replica la Sección 5 del notebook y además devuelve los artefactos
    de codificación (frecuencias y categorías) necesarios en producción."""
    feature_cols = (
        NUMERICAS_BASE + NUMERICAS_DERIVADAS + BINARIAS
        + NOMINAL_BAJA_CARD + NOMINAL_ALTA_CARD
    )
    feature_cols = [c for c in feature_cols if c in df.columns]
    faltantes = set(NUMERICAS_BASE + NUMERICAS_DERIVADAS + BINARIAS
                     + NOMINAL_BAJA_CARD + NOMINAL_ALTA_CARD) - set(feature_cols)
    if faltantes:
        print("Columnas faltantes en el dataset y que se omiten:", sorted(faltantes))

    X = df[feature_cols].copy()

    binarias = [c for c in BINARIAS if c in X.columns]
    baja_card = [c for c in NOMINAL_BAJA_CARD if c in X.columns]
    alta_card = [c for c in NOMINAL_ALTA_CARD if c in X.columns]

    # Diagnóstico: cuántos NULL trae cada feature desde SQL Server, antes de
    # imputar nada. Esto es lo que habría señalado directo la causa del
    # TypeError original en vez de tener que adivinarla.
    nulos = X[feature_cols].isna().sum()
    nulos = nulos[nulos > 0]
    if not nulos.empty:
        print("\nAviso: columnas con valores NULL en el dataset de SQL Server:")
        print(nulos.to_string())

    for col in binarias:
        if X[col].isna().any():
            print(f"  -> '{col}': {int(X[col].isna().sum())} NULL se imputan como 0.")
        X[col] = X[col].fillna(0).astype(int)

    # 'cluster_kmeans' puede venir NULL para pedidos que aún no pasaron por
    # una corrida del modelo no supervisado (LEFT JOIN en la vista). Se
    # imputa con -1 ("sin cluster asignado") en vez de descartar la fila.
    if "cluster_kmeans" in baja_card and X["cluster_kmeans"].isna().any():
        n_faltantes = int(X["cluster_kmeans"].isna().sum())
        print(f"  -> 'cluster_kmeans': {n_faltantes} NULL se imputan como -1 (sin cluster).")
        X["cluster_kmeans"] = X["cluster_kmeans"].fillna(-1).astype(int)

    # Guardamos las categorías vistas en train para poder reconstruir las
    # mismas columnas dummy exactamente igual en producción.
    categorias_dummies = {col: sorted(X[col].dropna().unique().tolist()) for col in baja_card}
    X = pd.get_dummies(X, columns=baja_card, drop_first=True)

    frecuencias_categoricas = {}
    for col in alta_card:
        frecuencias = X[col].value_counts(normalize=True)
        frecuencias_categoricas[col] = frecuencias.to_dict()
        X[col] = X[col].map(frecuencias)

    X = X.astype(float)
    y = (df["estado_pedido"] == "COMPLETE").astype(int)

    return X, y, categorias_dummies, frecuencias_categoricas


def evaluar_modelo(modelo, X_tr, y_tr, X_te, y_te):
    modelo.fit(X_tr, y_tr)
    y_pred = modelo.predict(X_te)
    y_proba = modelo.predict_proba(X_te)[:, 1]
    return {
        "modelo": modelo,
        "accuracy": accuracy_score(y_te, y_pred),
        "precision": precision_score(y_te, y_pred),
        "recall": recall_score(y_te, y_pred),
        "f1": f1_score(y_te, y_pred),
        "roc_auc": roc_auc_score(y_te, y_proba),
    }


# ================================================================================
# FUNCIÓN PRINCIPAL
# ================================================================================

def main(server: str = None, database: str = None, csv_path: str = None):
    """
    Función principal que ejecuta el pipeline completo.
    
    Args:
        server: Nombre del servidor SQL (opcional, si se usa conexión SQL)
        database: Nombre de la base de datos (opcional, si se usa conexión SQL)
        csv_path: Ruta al archivo CSV (opcional, si se usa archivo local)
    """
    
    # ----------------------------------------------------------------------------
    # 1. CARGA DE DATOS
    # ----------------------------------------------------------------------------
    
    print("="*80)
    print("MODELO SUPERVISADO - ENTRENAMIENTO")
    print("="*80)
    
    if csv_path:
        # Cargar desde CSV
        df = pd.read_csv(csv_path)
        print(f"Datos cargados: {len(df)} registros, {len(df.columns)} columnas")
        
    elif server and database:
        # Cargar desde SQL Server
        print(f"🔌 Conectando a SQL Server: {server}/{database}")
        engine = conectar_sql_server(server, database)
        df = cargar_datos_desde_sql(engine, "sp_DatasetML")
        
    else:
        # Intento automático con valores por defecto
        print("🔌 Intentando conexión automática a SQL Server...")
        try:
            engine = conectar_sql_server("OMEGA-DELL", "BD_ML_RELACIONAL")
            df = cargar_datos_desde_sql(engine, "sp_DatasetML")
        except Exception as e:
            print(f"Error en conexión SQL: {e}")
            print("Intentando cargar desde CSV por defecto...")
            df = pd.read_csv("DataCoSupplyChain_Limpio.csv")
            print(f"Datos cargados: {len(df)} registros, {len(df.columns)} columnas")
    
    # El SP sp_DatasetML devuelve 'nombre_categoria' (columna real de la tabla
    # Categoria), no 'categoria'. Se renombra aquí para que coincida con
    # NOMINAL_ALTA_CARD y con el mismo criterio usado en KMEANSCERCER.py.
    if "nombre_categoria" in df.columns and "categoria" not in df.columns:
        df = df.rename(columns={"nombre_categoria": "categoria"})

    # 'region_destino' se confirmó en vw_ML_DataCoSupplyChain con ese nombre
    # exacto (columna nativa de la tabla Destino) -> no requiere rename.

    # Verificar que la variable objetivo existe
    if "estado_pedido" not in df.columns:
        raise ValueError("La columna 'estado_pedido' no existe en el dataset.")
    
    # Mostrar distribución del target
    print("\nDistribución del target (estado_pedido):")
    print(df["estado_pedido"].value_counts())
    print(df["estado_pedido"].value_counts(normalize=True).round(3))
    
    # ----------------------------------------------------------------------------
    # 2. PREPROCESAMIENTO
    # ----------------------------------------------------------------------------
    
    print("\n" + "="*80)
    print("PREPROCESAMIENTO DE DATOS")
    print("="*80)
    
    # Eliminar columnas con fuga de datos
    for col in COLUMNAS_FUGA:
        if col in df.columns:
            df = df.drop(columns=[col])
            print(f"Columna eliminada (fuga de datos): {col}")
    
    # Ingeniería de características
    df, medianas = ingenieria_features(df)
    print(f"Variables derivadas creadas: {len(NUMERICAS_DERIVADAS)} nuevas columnas")
    
    # Construir X, y y artefactos de codificación
    X, y, categorias_dummies, frecuencias_categoricas = construir_X_y(df)
    print(f"Dataset final: {X.shape[0]} registros, {X.shape[1]} features")
    
    # ----------------------------------------------------------------------------
    # 3. DIVISIÓN TRAIN/TEST Y ESCALADO
    # ----------------------------------------------------------------------------
    
    print("\n" + "="*80)
    print("DIVISIÓN Y ESCALADO")
    print("="*80)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=RANDOM_STATE, stratify=y
    )
    print(f"Entrenamiento: {len(X_train)} registros")
    print(f"Prueba: {len(X_test)} registros")
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    print("Escalado completado")
    
    # ----------------------------------------------------------------------------
    # 4. ENTRENAMIENTO DE MODELOS
    # ----------------------------------------------------------------------------
    
    print("\n" + "="*80)
    print("ENTRENAMIENTO DE MODELOS")
    print("="*80)
    
    modelos_requieren_escalado = {"Regresión Logística", "SVM", "KNN"}
    peso_positivo = (y_train == 0).sum() / (y_train == 1).sum()
    
    print(f"Peso positivo (scale_pos_weight): {peso_positivo:.4f}")
    
    candidatos = {
        "Regresión Logística": (
            LogisticRegression(max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE),
            X_train_scaled, X_test_scaled,
        ),
        "Árbol de Decisión": (
            DecisionTreeClassifier(max_depth=12, class_weight="balanced", random_state=RANDOM_STATE),
            X_train, X_test,
        ),
        "Random Forest": (
            RandomForestClassifier(n_estimators=200, max_depth=15, class_weight="balanced",
                                    random_state=RANDOM_STATE, n_jobs=-1),
            X_train, X_test,
        ),
        "KNN": (
            KNeighborsClassifier(n_neighbors=15, n_jobs=-1),
            X_train_scaled, X_test_scaled,
        ),
    }
    
    # Intentar agregar XGBoost
    try:
        from xgboost import XGBClassifier
        candidatos["XGBoost"] = (
            XGBClassifier(n_estimators=200, max_depth=6, random_state=RANDOM_STATE,
                          eval_metric="logloss", scale_pos_weight=peso_positivo),
            X_train, X_test,
        )
        print("XGBoost disponible")
    except ModuleNotFoundError:
        print("XGBoost no instalado: se omite ese candidato.")
    
    # Entrenar y evaluar
    resultados = {}
    for nombre, (modelo, X_tr, X_te) in candidatos.items():
        print(f"Entrenando {nombre} ...")
        resultados[nombre] = evaluar_modelo(modelo, X_tr, y_train, X_te, y_test)
    
    # Tabla comparativa
    tabla = pd.DataFrame({
        n: {k: v for k, v in r.items() if k != "modelo"} for n, r in resultados.items()
    }).T.sort_values("f1", ascending=False)
    
    print("\nCOMPARACIÓN DE MODELOS (ordenado por F1):")
    print(tabla.round(4))
    
    # ----------------------------------------------------------------------------
    # 5. SELECCIÓN DEL MEJOR MODELO
    # ----------------------------------------------------------------------------
    
    nombre_mejor = tabla.index[0]
    mejor_modelo = resultados[nombre_mejor]["modelo"]
    requiere_escalado = nombre_mejor in modelos_requieren_escalado
    print(f"\nMEJOR MODELO: {nombre_mejor}")
    print(f"   F1-Score: {tabla.loc[nombre_mejor, 'f1']:.4f}")
    print(f"   ROC-AUC:  {tabla.loc[nombre_mejor, 'roc_auc']:.4f}")
    
    # ----------------------------------------------------------------------------
    # 6. CALIBRACIÓN DE PROBABILIDADES
    # ----------------------------------------------------------------------------
    
    print("\n" + "="*80)
    print("CALIBRACIÓN DE PROBABILIDADES")
    print("="*80)
    
    X_cal_train = X_train_scaled if requiere_escalado else X_train
    modelo_final = CalibratedClassifierCV(mejor_modelo, method="sigmoid", cv=3)
    modelo_final.fit(X_cal_train, y_train)
    print("Modelo calibrado con sigmoid (Platt Scaling)")
    
    # ----------------------------------------------------------------------------
    # 7. GUARDADO DE ARTEFACTOS
    # ----------------------------------------------------------------------------
    
    print("\n" + "="*80)
    print("GUARDADO DE ARTEFACTOS")
    print("="*80)
    
    # Modelo y scaler
    joblib.dump(modelo_final, "modelo_prediccion_envios.pkl")
    joblib.dump(scaler, "scaler_envios.pkl")
    print("modelo_prediccion_envios.pkl")
    print("scaler_envios.pkl")
    
    # Features
    with open("features_modelo.json", "w", encoding="utf-8") as f:
        json.dump(X_train.columns.tolist(), f, indent=2, ensure_ascii=False)
    print("features_modelo.json")
    
    # Frecuencias categóricas
    with open("frecuencias_categoricas.json", "w", encoding="utf-8") as f:
        json.dump(frecuencias_categoricas, f, indent=2, ensure_ascii=False)
    print("frecuencias_categoricas.json")
    
    # Categorías de dummies
    with open("categorias_dummies.json", "w", encoding="utf-8") as f:
        json.dump(categorias_dummies, f, indent=2, ensure_ascii=False)
    print("categorias_dummies.json")
    
    # Medianas de imputación
    with open("medianas_imputacion.json", "w", encoding="utf-8") as f:
        json.dump(medianas, f, indent=2, ensure_ascii=False)
    print("medianas_imputacion.json")
    
    # Metadatos del modelo
    metricas_test = {
        k: round(float(v), 4) for k, v in resultados[nombre_mejor].items() if k != "modelo"
    }
    
    with open("metadata_modelo.json", "w", encoding="utf-8") as f:
        json.dump({
            "modelo": nombre_mejor,
            "requiere_escalado": requiere_escalado,
            "features_leakage_excluidas": COLUMNAS_FUGA,
            "umbral_alerta_recomendado": 0.65,
            "metricas_test": metricas_test,
            "fecha_entrenamiento": date.today().isoformat(),
            "dataset_origen": "SQL Server" if server else "CSV",
            "server": server or "N/A",
            "database": database or "N/A",
        }, f, indent=2, ensure_ascii=False)
    print("metadata_modelo.json")
    
    # ----------------------------------------------------------------------------
    # 8. RESUMEN FINAL
    # ----------------------------------------------------------------------------
    
    print("\n" + "="*80)
    print("RESUMEN FINAL")
    print("="*80)
    print(f"Mejor modelo: {nombre_mejor}")
    print(f"F1-Score: {metricas_test['f1']:.4f}")
    print(f"Accuracy: {metricas_test['accuracy']:.4f}")
    print(f"ROC-AUC: {metricas_test['roc_auc']:.4f}")
    print(f"Precision: {metricas_test['precision']:.4f}")
    print(f"Recall: {metricas_test['recall']:.4f}")
    print("\n7 artefactos guardados en el directorio actual:")
    print("   1. modelo_prediccion_envios.pkl")
    print("   2. scaler_envios.pkl")
    print("   3. features_modelo.json")
    print("   4. frecuencias_categoricas.json")
    print("   5. categorias_dummies.json")
    print("   6. medianas_imputacion.json")
    print("   7. metadata_modelo.json")
    print("\nCopia estos 7 archivos a la misma carpeta que tu app de Streamlit.")
    print("="*80)


# ================================================================================
# PUNTO DE ENTRADA
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Entrena el modelo supervisado y exporta artefactos para producción."
    )
    parser.add_argument(
        "--server", 
        default="OMEGA-DELL",
        help="Nombre del servidor SQL Server (ej. OMEGA-DELL)"
    )
    parser.add_argument(
        "--database", 
        default="BD_ML_RELACIONAL",
        help="Nombre de la base de datos (ej. BD_ML_RELACIONAL)"
    )
    parser.add_argument(
        "--csv", 
        default=None,
        help="Ruta al archivo CSV (si se usa en lugar de SQL Server)"
    )
    
    args = parser.parse_args()
    
    if args.csv:
        main(csv_path=args.csv)
    else:
        main(server=args.server, database=args.database)