import argparse
import json
import sys
import os
from datetime import date

import joblib
import numpy as np
import pandas as pd
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

# Columnas excluidas por fuga de datos
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
NOMINAL_BAJA_CARD = ["modo_envio", "cluster_kmeans", "cluster_dbscan"]
NOMINAL_ALTA_CARD = ["categoria", "region_destino"]


# ================================================================================
# FUNCIÓN PARA ENCONTRAR EL CSV
# ================================================================================

def encontrar_archivo_csv(nombre_archivo=None):
    """
    Busca el archivo CSV en múltiples ubicaciones.
    
    Args:
        nombre_archivo: Nombre del archivo a buscar (opcional)
    
    Returns:
        str: Ruta completa al archivo encontrado, o None si no se encuentra
    """
    # Lista de posibles rutas donde buscar
    rutas_a_buscar = []
    
    # 1. El directorio actual
    rutas_a_buscar.append(os.getcwd())
    
    # 2. El directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    rutas_a_buscar.append(script_dir)
    
    # 3. Directorio padre del script
    rutas_a_buscar.append(os.path.dirname(script_dir))
    
    # 4. Directorio "PROYECTO" (subir 2 niveles)
    rutas_a_buscar.append(os.path.join(os.path.dirname(script_dir), "PROYECTO"))
    
    # 5. Directorio "BDML" (donde está el script)
    rutas_a_buscar.append(os.path.join(script_dir, "BDML"))
    
    # 6. Directorio "Mi unidad" (usuario)
    usuario = os.environ.get('USERNAME', '')
    if usuario:
        rutas_a_buscar.append(f"G:/Mi unidad/UNACH ANDRES/CUARTO SEMESTRE/Administracion de bases de datos/PROYECTO FINAL/PROYECTO")
        rutas_a_buscar.append(f"C:/Users/{usuario}/Desktop")
        rutas_a_buscar.append(f"C:/Users/{usuario}/Downloads")
    
    # Posibles nombres de archivo
    if nombre_archivo:
        nombres = [nombre_archivo]
    else:
        nombres = [
            "DataCoSupplyChain_Limpio.csv",
            "DataCoSupplyChain.csv",
            "datacolimpio.csv",
            "data.csv",
            "DatasetML.csv",
            "datasetml.csv",
        ]
    
    # Buscar archivo
    for ruta in rutas_a_buscar:
        if not os.path.exists(ruta):
            continue
        for nombre in nombres:
            archivo = os.path.join(ruta, nombre)
            if os.path.exists(archivo):
                print(f"Archivo encontrado: {archivo}")
                return archivo
    
    # Si no se encuentra, listar archivos CSV en el directorio actual
    print("\nArchivos CSV disponibles en el directorio actual:")
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    if csv_files:
        for f in csv_files:
            print(f"   - {f}")
    else:
        print("   (No se encontraron archivos CSV)")
    
    return None


def cargar_datos(csv_path=None):
    """
    Carga datos desde CSV con búsqueda automática si no se encuentra.
    
    Args:
        csv_path: Ruta al archivo CSV (opcional)
    
    Returns:
        DataFrame: Datos cargados
    """
    # Si se especificó ruta y existe, cargar
    if csv_path and os.path.exists(csv_path):
        print(f"Cargando: {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"Datos cargados: {len(df)} registros, {len(df.columns)} columnas")
        return df
    
    # Si se especificó ruta pero no existe
    if csv_path:
        print(f"Archivo no encontrado: {csv_path}")
        print("Buscando alternativas...")
    
    # Buscar archivo automáticamente
    archivo_encontrado = encontrar_archivo_csv(csv_path)
    
    if archivo_encontrado:
        print(f"Cargando: {archivo_encontrado}")
        df = pd.read_csv(archivo_encontrado)
        print(f"Datos cargados: {len(df)} registros, {len(df.columns)} columnas")
        return df
    
    # Si no se encuentra, mostrar error y sugerencias
    print("\nNo se encontró el archivo CSV.")
    print("\nSugerencias:")
    print("   1. Especifica la ruta correcta:")
    print("      python modelosupervisadolocal.py --csv ruta/completa/al/archivo.csv")
    print("   2. Asegúrate de que el archivo esté en el directorio actual")
    print("   3. Verifica el nombre del archivo (DataCoSupplyChain_Limpio.csv)")
    
    # Listar archivos en el directorio actual
    print("\nContenido del directorio actual:")
    for item in os.listdir('.'):
        if os.path.isfile(item):
            size = os.path.getsize(item) / 1024  # KB
            print(f"   - {item} ({size:.1f} KB)")
        else:
            print(f" {item}/")
    
    raise FileNotFoundError("No se encontró el archivo CSV. Verifica la ruta y el nombre del archivo.")


# ================================================================================
# FUNCIONES DE PREPROCESAMIENTO
# ================================================================================

def ingenieria_features(df: pd.DataFrame, medianas: dict | None = None):
    """
    Crea las variables derivadas.
    
    Si `medianas` es None (modo entrenamiento), las medianas se calculan y se
    devuelven para guardarlas. Si se pasan (modo inferencia), se reutilizan
    las medianas de entrenamiento en vez de recalcularlas.
    """
    df = df.copy()
    calcular_medianas = medianas is None
    if calcular_medianas:
        medianas = {}

    # Diferencia entre envío real y programado
    df["diferencia_envio"] = df["dias_envio_real"] - df["dias_envio_prog"]

    # Ratio de envío (evitar división por cero)
    ratio = df["dias_envio_real"] / df["dias_envio_prog"].replace(0, np.nan)
    if calcular_medianas:
        medianas["ratio_envio"] = float(ratio.median())
    df["ratio_envio"] = ratio.fillna(medianas["ratio_envio"])

    # ¿Cumple el plazo?
    df["cumple_plazo"] = (df["dias_envio_real"] <= df["dias_envio_prog"]).astype(int)

    # Precio promedio por item
    precio_prom = df["ventas"] / df["cantidad"].replace(0, np.nan)
    if calcular_medianas:
        medianas["precio_promedio_item"] = float(precio_prom.median())
    df["precio_promedio_item"] = precio_prom.fillna(medianas["precio_promedio_item"])

    # Margen total (evitar división por cero)
    margen = df["ganancia_pedido"] / df["ventas"].replace(0, np.nan)
    df["margen_total"] = margen.fillna(0)

    # Eficiencia del cliente
    eficiencia = df["ventas_cliente"] / df["cantidad"].replace(0, np.nan)
    if calcular_medianas:
        medianas["eficiencia_cliente"] = float(eficiencia.median())
    df["eficiencia_cliente"] = eficiencia.fillna(medianas["eficiencia_cliente"])

    # Interacción riesgo-precio
    df["riesgo_por_precio"] = df["riesgo_retraso"].astype(int) * df["precio_base"]

    return df, medianas


def construir_X_y(df: pd.DataFrame):
    """
    Construye X (features) e y (target) con codificación.
    También devuelve los artefactos necesarios para producción.
    """
    # Seleccionar features
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

    # Separar tipos de columnas
    binarias = [c for c in BINARIAS if c in X.columns]
    baja_card = [c for c in NOMINAL_BAJA_CARD if c in X.columns]
    alta_card = [c for c in NOMINAL_ALTA_CARD if c in X.columns]

    # Codificar binarias
    for col in binarias:
        X[col] = X[col].astype(int)

    # One-Hot Encoding para baja cardinalidad
    categorias_dummies = {col: sorted(X[col].dropna().unique().tolist()) for col in baja_card}
    X = pd.get_dummies(X, columns=baja_card, drop_first=True)

    # Codificación por frecuencia para alta cardinalidad
    frecuencias_categoricas = {}
    for col in alta_card:
        frecuencias = X[col].value_counts(normalize=True)
        frecuencias_categoricas[col] = frecuencias.to_dict()
        X[col] = X[col].map(frecuencias)

    # Convertir a float y crear target
    X = X.astype(float)
    y = (df["estado_pedido"] == "COMPLETE").astype(int)

    return X, y, categorias_dummies, frecuencias_categoricas


def evaluar_modelo(modelo, X_tr, y_tr, X_te, y_te):
    """
    Entrena y evalúa un modelo, retornando métricas.
    """
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

def main(csv_path: str = None):
    """
    Función principal que ejecuta el pipeline completo.
    """
    print("="*80)
    print("MODELO SUPERVISADO - ENTRENAMIENTO")
    print("="*80)
    print(f"Fecha: {date.today().isoformat()}")
    
    # ----------------------------------------------------------------------------
    # 1. CARGA DE DATOS
    # ----------------------------------------------------------------------------
    
    df = cargar_datos(csv_path)
    
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
    print("PREPROCESAMIENTO")
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
    print("GUARDANDO ARTEFACTOS")
    print("="*80)
    
    # 7.1 Modelo y scaler
    joblib.dump(modelo_final, "modelo_prediccion_envios.pkl")
    joblib.dump(scaler, "scaler_envios.pkl")
    print("modelo_prediccion_envios.pkl")
    print("scaler_envios.pkl")
    
    # 7.2 Features
    with open("features_modelo.json", "w", encoding="utf-8") as f:
        json.dump(X_train.columns.tolist(), f, indent=2, ensure_ascii=False)
    print("features_modelo.json")
    
    # 7.3 Frecuencias categóricas
    with open("frecuencias_categoricas.json", "w", encoding="utf-8") as f:
        json.dump(frecuencias_categoricas, f, indent=2, ensure_ascii=False)
    print("frecuencias_categoricas.json")
    
    # 7.4 Categorías de dummies
    with open("categorias_dummies.json", "w", encoding="utf-8") as f:
        json.dump(categorias_dummies, f, indent=2, ensure_ascii=False)
    print("categorias_dummies.json")
    
    # 7.5 Medianas de imputación
    with open("medianas_imputacion.json", "w", encoding="utf-8") as f:
        json.dump(medianas, f, indent=2, ensure_ascii=False)
    print("medianas_imputacion.json")
    
    # 7.6 Metadatos del modelo
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
            "dataset_origen": "CSV Local",
            "archivo_csv": csv_path or "DataCoSupplyChain_Limpio.csv",
        }, f, indent=2, ensure_ascii=False)
    print("metadata_modelo.json")
    
    # ----------------------------------------------------------------------------
    # 8. RESUMEN FINAL
    # ----------------------------------------------------------------------------
    
    print("\n" + "="*80)
    print("✅ ENTRENAMIENTO COMPLETADO")
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
    
    print("\nSiguiente paso:")
    print("   Copia estos 7 archivos a la misma carpeta que tu app de Streamlit.")
    print("   Luego ejecuta: streamlit run app_streamlit.py")
    print("="*80)


# ================================================================================
# PUNTO DE ENTRADA
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Entrena el modelo supervisado y exporta artefactos para producción."
    )
    parser.add_argument(
        "--csv", 
        default=None,
        help="Ruta al archivo CSV (ej: DataCoSupplyChain_Limpio.csv)"
    )
    
    args = parser.parse_args()
    
    try:
        main(csv_path=args.csv)
    except KeyboardInterrupt:
        print("\nEntrenamiento interrumpido por el usuario.")
        sys.exit(0)
    except FileNotFoundError as e:
        print(f"\n{e}")
        print("\nPara especificar la ruta correcta:")
        print("   python modelosupervisadolocal.py --csv ruta/completa/al/archivo.csv")
        sys.exit(1)
    except Exception as e:
        print(f"\nError durante la ejecución: {e}")
        print("\nSugerencias:")
        print("   1. Verifica que el archivo CSV existe y no está corrupto")
        print("   2. Asegúrate de tener instaladas las dependencias:")
        print("      pip install pandas numpy scikit-learn xgboost joblib")
        print("   3. Verifica que las columnas necesarias existen en el archivo")
        import traceback
        traceback.print_exc()
        sys.exit(1)