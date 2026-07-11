import sys
import os
import pandas as pd
import numpy as np

# Agregar la ruta del proyecto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.model_integration import MLModelManager

def test_models():
    """Prueba la carga y uso de los modelos"""
    
    print("=" * 70)
    print("🧪 PRUEBA DE MODELOS ML - SUPPLY CHAIN ANALYTICS")
    print("=" * 70)
    
    # 1. Inicializar gestor
    print("\n📁 Inicializando gestor de modelos...")
    ml = MLModelManager()
    
    # 2. Cargar modelos
    print("\n📤 Cargando modelos...")
    ml.load_models()
    
    # 3. Verificar estado
    status = ml.get_model_status()
    print("\n📊 ESTADO DE LOS MODELOS:")
    print("   " + "-" * 40)
    print(f"   ✅ Clasificación (Andrés): {'✅ CARGADO' if status['classifier_loaded'] else '❌ NO ENCONTRADO'}")
    print(f"   ✅ Clustering (Mika):     {'✅ CARGADO' if status['cluster_loaded'] else '❌ NO ENCONTRADO'}")
    print(f"   ✅ Escalador:             {'✅ CARGADO' if status['scaler_loaded'] else '❌ NO ENCONTRADO'}")
    print("   " + "-" * 40)
    
    # 4. Probar predicción de clasificación
    print("\n🔮 PRUEBA DE PREDICCIÓN (Clasificación - Andrés)")
    print("   " + "-" * 40)
    
    # Datos de ejemplo para predicción
    order_example = {
        'Order Id': 'TEST-001',
        'Days for shipping (real)': 5,
        'Order Item Total': 150.0,
        'Order Item Quantity': 2,
        'Late_delivery_risk': 0,
        'Benefit per order': 45.0,
        'Sales per customer': 300.0,
        'Order Item Discount Rate': 0.05,
        'Order Item Profit Ratio': 0.25,
        'Shipping Mode': 'Standard Class',
        'Order Region': 'Southeast Asia'
    }
    
    print(f"📋 Datos de prueba:")
    print(f"   - Días de envío: {order_example['Days for shipping (real)']}")
    print(f"   - Total del pedido: ${order_example['Order Item Total']}")
    print(f"   - Cantidad: {order_example['Order Item Quantity']}")
    print(f"   - Riesgo del sistema: {order_example['Late_delivery_risk']}")
    
    result = ml.predict_delay(order_example)
    
    print(f"\n📊 RESULTADO:")
    print(f"   - Probabilidad de retraso: {result['probability']:.1f}%")
    print(f"   - Nivel de riesgo: {result['risk_level']}")
    print(f"   - Modelo usado: {result.get('model_used', 'N/A')}")
    
    if result.get('risk_factors'):
        print(f"\n⚠️ FACTORES DE RIESGO IDENTIFICADOS:")
        for factor in result['risk_factors']:
            print(f"   - {factor['message']}")
    
    # 5. Probar segmentación de clientes (clustering)
    print("\n👥 PRUEBA DE SEGMENTACIÓN (Clustering - Mika)")
    print("   " + "-" * 40)
    
    customer_example = {
        'Customer Id': 'CUST-001',
        'Total Orders': 15,
        'Total Spent': 2500.0,
        'Delay Rate': 25.0,
        'Avg Order Value': 166.0,
        'Category Count': 3,
        'Market Count': 2
    }
    
    print(f"📋 Datos del cliente:")
    print(f"   - Total pedidos: {customer_example['Total Orders']}")
    print(f"   - Gasto total: ${customer_example['Total Spent']}")
    print(f"   - Tasa de retraso: {customer_example['Delay Rate']}%")
    print(f"   - Categorías: {customer_example['Category Count']}")
    
    if status['cluster_loaded']:
        segment = ml.segment_customer(customer_example)
        print(f"\n📊 RESULTADO:")
        print(f"   - Segmento asignado: {segment['segment']}")
        print(f"   - Nombre del segmento: {segment['segment_name']}")
        print(f"   - Descripción: {segment['description']}")
    else:
        print("\n⚠️ Modelo de clustering no disponible")
        print("   Mika: Entrena tu modelo y guárdalo como 'models/cluster.pkl'")
    
    # 6. Resumen final
    print("\n" + "=" * 70)
    print("📋 RESUMEN FINAL")
    print("=" * 70)
    
    if status['classifier_loaded']:
        print("✅ Modelo de clasificación (Andrés): FUNCIONANDO")
    else:
        print("❌ Modelo de clasificación (Andrés): PENDIENTE")
        print("   → Entrena tu modelo y guárdalo como 'models/classifier.pkl'")
    
    if status['cluster_loaded']:
        print("✅ Modelo de clustering (Mika): FUNCIONANDO")
    else:
        print("❌ Modelo de clustering (Mika): PENDIENTE")
        print("   → Entrena tu modelo y guárdalo como 'models/cluster.pkl'")
    
    print("\n" + "=" * 70)
    print("✅ Prueba completada")
    print("=" * 70)

if __name__ == "__main__":
    test_models()