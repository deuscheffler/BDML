import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from utils.models import MLModelLoader

st.set_page_config(
    page_title="Predicción de Retrasos",
    page_icon="🔮",
    layout="wide"
)

if 'filtered_df' not in st.session_state or st.session_state.filtered_df is None:
    st.warning("⚠️ No hay datos disponibles")
    st.stop()

df = st.session_state.filtered_df

# ============================================
# 🤖 INICIALIZAR MODELOS ML
# ============================================

if 'ml_loader' not in st.session_state:
    st.session_state.ml_loader = MLModelLoader()
    st.session_state.ml_loader.load_models()

ml = st.session_state.ml_loader

# ============================================
# 🎨 ESTILOS CSS (Manteniendo el diseño existente)
# ============================================

st.markdown("""
<style>
/* === TÍTULO PRINCIPAL === */
.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    font-weight: 600;
    background: linear-gradient(135deg, #4fc3f7 0%, #00b4d8 60%, #0288d1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}

.section-subtitle {
    color: #8899bb;
    font-size: 0.9rem;
    margin-bottom: 24px;
}

/* === ESTADO DEL MODELO === */
.model-status {
    font-size: 0.8rem;
    padding: 4px 16px;
    border-radius: 20px;
    display: inline-block;
    margin-bottom: 12px;
}
.model-status.loaded {
    background: rgba(78, 205, 196, 0.15);
    color: #4ecdc4;
}
.model-status.simulated {
    background: rgba(255, 217, 61, 0.15);
    color: #ffd93d;
}
.model-status.partial {
    background: rgba(77, 171, 247, 0.15);
    color: #4dabf7;
}

/* === TARJETA DE PREDICCIÓN === */
.prediction-card {
    background: rgba(20, 20, 30, 0.6);
    backdrop-filter: blur(20px);
    border-radius: 16px;
    border: 1px solid rgba(100, 180, 255, 0.08);
    padding: 28px 24px;
    text-align: center;
    transition: all 0.3s ease;
}
.prediction-card:hover {
    border-color: rgba(79, 195, 247, 0.2);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

.prediction-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 3.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #4fc3f7 0%, #00b4d8 60%, #0288d1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.2;
}

.prediction-label {
    font-size: 1.1rem;
    font-weight: 600;
    margin-top: 8px;
}

.prediction-sub {
    color: #8899bb;
    font-size: 0.75rem;
    margin-top: 8px;
}

/* === BARRA DE PROGRESO === */
.progress-container {
    background: rgba(255,255,255,0.05);
    border-radius: 50px;
    height: 8px;
    margin: 12px 0;
    overflow: hidden;
    position: relative;
}
.progress-bar {
    height: 100%;
    border-radius: 50px;
    transition: width 1s ease-in-out;
    background: linear-gradient(90deg, #4fc3f7, #00b4d8, #0288d1);
}

/* === FACTOR DE RIESGO === */
.risk-factor {
    padding: 12px 16px;
    border-radius: 12px;
    margin-bottom: 8px;
    background: rgba(255,255,255,0.02);
    border-left: 3px solid #4fc3f7;
    transition: all 0.3s ease;
}
.risk-factor:hover {
    background: rgba(255,255,255,0.04);
}
.risk-factor.high {
    border-left-color: #ff6b6b;
}
.risk-factor.medium {
    border-left-color: #ffd93d;
}
.risk-factor.low {
    border-left-color: #4fc3f7;
}
.risk-factor .icon {
    font-size: 1.2rem;
    margin-right: 10px;
}
.risk-factor .message {
    font-weight: 500;
}
.risk-factor .detail {
    color: #8899bb;
    font-size: 0.8rem;
    margin-top: 4px;
    padding-left: 34px;
}

/* === TARJETA DE BÚSQUEDA === */
.search-card {
    background: rgba(255,255,255,0.02);
    border-radius: 12px;
    padding: 12px 16px;
    border: 1px solid rgba(100, 180, 255, 0.06);
    margin-bottom: 8px;
    transition: all 0.3s ease;
    cursor: pointer;
}
.search-card:hover {
    background: rgba(79, 195, 247, 0.04);
    border-color: rgba(79, 195, 247, 0.12);
}
.search-card.selected {
    background: rgba(79, 195, 247, 0.06);
    border-color: rgba(79, 195, 247, 0.2);
}

/* === TABS PERSONALIZADOS === */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(255,255,255,0.02);
    border-radius: 12px;
    padding: 4px;
    border: 1px solid rgba(100, 180, 255, 0.06);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 8px 20px;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    color: #8899bb;
    transition: all 0.3s ease;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, rgba(79, 195, 247, 0.15), rgba(0, 180, 216, 0.08));
    color: #4fc3f7;
    border: 1px solid rgba(79, 195, 247, 0.1);
}

/* === FORMULARIO === */
.form-label {
    color: #8899bb;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

.form-section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: #e8edf5;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* === RECOMENDACIONES === */
.recommendation-box {
    border-radius: 12px;
    padding: 16px 20px;
    margin-top: 12px;
    border: 1px solid rgba(100, 180, 255, 0.06);
}
.recommendation-box.high {
    background: rgba(255, 107, 107, 0.06);
    border-color: rgba(255, 107, 107, 0.15);
}
.recommendation-box.medium {
    background: rgba(255, 217, 61, 0.06);
    border-color: rgba(255, 217, 61, 0.15);
}
.recommendation-box.low {
    background: rgba(78, 205, 196, 0.06);
    border-color: rgba(78, 205, 196, 0.15);
}

/* === RESPONSIVE === */
@media (max-width: 768px) {
    .prediction-value {
        font-size: 2.5rem;
    }
}
</style>
""", unsafe_allow_html=True)

# ============================================
# 📊 ENCABEZADO
# ============================================

st.markdown('<div class="section-title">🔮 Centro Inteligente de Predicción</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Analiza pedidos existentes o simula nuevos escenarios para predecir el riesgo de retraso</div>', unsafe_allow_html=True)

# ============================================
# 📊 ESTADO DEL MODELO
# ============================================

has_ml = ml.is_loaded and ml.model_status['classifier']

if has_ml:
    st.markdown('<span class="model-status loaded">✅ Modelo ML cargado - Predicción en tiempo real</span>', unsafe_allow_html=True)
elif ml.is_loaded:
    st.markdown('<span class="model-status partial">🔄 Modelo parcialmente cargado</span>', unsafe_allow_html=True)
else:
    st.markdown('<span class="model-status simulated">⚠️ Modo simulación - Los modelos ML estarán disponibles cuando tus compañeros los entrenen</span>', unsafe_allow_html=True)

st.divider()

# ============================================
# 🎯 FUNCIONES AUXILIARES
# ============================================

def mostrar_resultado(prediction, order_info=None):
    """Muestra los resultados de la predicción con diseño moderno"""
    
    prob = prediction['probability']
    risk_label = prediction['risk_level']
    risk_color = prediction['risk_color']
    is_ml = prediction.get('is_ml', False)
    risk_factors = prediction.get('risk_factors', [])
    model_used = prediction.get('model_used', 'Simulación')
    
    # Determinar nivel para recomendaciones
    risk_level = 'high' if prob >= 70 else 'medium' if prob >= 40 else 'low'
    
    # ============================================
    # TARJETA DE PREDICCIÓN
    # ============================================
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        <div class="prediction-card">
            <div class="prediction-value">{prob:.1f}%</div>
            <div class="prediction-label" style="color: {risk_color};">{risk_label}</div>
            <div class="prediction-sub">
                {'✅ Basado en modelo ML' if is_ml else '⚠️ Basado en simulación'}
            </div>
            <div class="prediction-sub" style="font-size: 0.65rem;">
                {model_used}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Barra de progreso
        st.markdown(f"""
        <div style="margin-top: 12px;">
            <div style="display: flex; justify-content: space-between; color: #8899bb; font-size: 0.8rem;">
                <span>🟢 Bajo</span>
                <span>🟡 Medio</span>
                <span>🔴 Alto</span>
            </div>
            <div class="progress-container">
                <div class="progress-bar" style="width: {prob}%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; color: #8899bb; font-size: 0.7rem; margin-top: 4px;">
                <span>0%</span>
                <span style="color: {risk_color}; font-weight: 600;">{prob:.1f}%</span>
                <span>100%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Información del pedido si existe
        if order_info:
            st.markdown(f"""
            <div style="margin-top: 16px; background: rgba(255,255,255,0.02); border-radius: 10px; padding: 12px; border: 1px solid rgba(100,180,255,0.06);">
                <div style="color: #8899bb; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.5px;">Pedido analizado</div>
                <div style="color: #e8edf5; font-size: 0.9rem; font-weight: 500;">{order_info.get('Order Id', 'N/A')}</div>
                <div style="color: #8899bb; font-size: 0.75rem;">{order_info.get('Product Name', 'N/A')[:30]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # ============================================
    # ⚠️ FACTORES DE RIESGO
    # ============================================
    
    st.markdown("### ⚠️ Factores de Riesgo Identificados")
    
    if risk_factors:
        cols = st.columns(min(3, len(risk_factors)))
        for i, factor in enumerate(risk_factors):
            with cols[i % len(cols)]:
                severity = factor.get('severity', 'low')
                icon = factor.get('icon', '📌')
                message = factor.get('message', '')
                detail = factor.get('detail', '')
                
                st.markdown(f"""
                <div class="risk-factor {severity}">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="icon">{icon}</span>
                        <span class="message">{message}</span>
                    </div>
                    <div class="detail">{detail}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success("✅ No se identificaron factores de riesgo significativos")
    
    # ============================================
    # 💡 RECOMENDACIONES
    # ============================================
    
    st.markdown("### 💡 Recomendaciones")
    
    if prob >= 70:
        st.markdown("""
        <div class="recommendation-box high">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                <span style="font-size: 1.5rem;">🔴</span>
                <span style="font-weight: 600; color: #ff6b6b;">ACCIONES PRIORITARIAS</span>
            </div>
            <div style="color: #b8c6d4; font-size: 0.9rem; line-height: 1.8; padding-left: 8px;">
                • 📞 Contactar al cliente para confirmar disponibilidad<br>
                • 🚢 Considerar cambio en modo de envío (Express o Same Day)<br>
                • 📋 Priorizar este pedido en el proceso logístico<br>
                • 🔍 Monitorear el progreso cada 4 horas
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif prob >= 40:
        st.markdown("""
        <div class="recommendation-box medium">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                <span style="font-size: 1.5rem;">🟡</span>
                <span style="font-weight: 600; color: #ffd93d;">ACCIONES PREVENTIVAS</span>
            </div>
            <div style="color: #b8c6d4; font-size: 0.9rem; line-height: 1.8; padding-left: 8px;">
                • 📊 Monitorear el progreso del envío<br>
                • 🔄 Tener plan de contingencia preparado<br>
                • 📱 Mantener comunicación con el cliente<br>
                • 📋 Documentar el seguimiento
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="recommendation-box low">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                <span style="font-size: 1.5rem;">🟢</span>
                <span style="font-weight: 600; color: #4ecdc4;">MANTENER ESTRATEGIA</span>
            </div>
            <div style="color: #b8c6d4; font-size: 0.9rem; line-height: 1.8; padding-left: 8px;">
                • ✅ Continuar con el proceso normal<br>
                • 📈 Documentar factores de éxito<br>
                • 🎯 Seguir buenas prácticas<br>
                • 📊 Mantener monitoreo estándar
            </div>
        </div>
        """, unsafe_allow_html=True)

def construir_nuevo_pedido(categoria, producto, cantidad, precio, mercado, region, pais, shipping_mode, order_status, customer_segment):
    """Construye el diccionario para el nuevo pedido"""
    return {
        'Category Name': categoria,
        'Product Name': producto,
        'Order Item Quantity': cantidad,
        'Order Item Total': precio,
        'Market': mercado,
        'Order Region': region,
        'Order Country': pais,
        'Shipping Mode': shipping_mode,
        'Order Status': order_status,
        'Customer Segment': customer_segment,
        'Days for shipping (real)': random.uniform(2, 10),
        'Days for shipment (scheduled)': random.uniform(2, 7),
        'Late_delivery_risk': 0,
        'Benefit per order': random.uniform(-20, 100),
        'Sales per customer': random.uniform(50, 500),
        'Order Item Discount Rate': random.uniform(0, 0.2),
        'Order Item Profit Ratio': random.uniform(0, 0.5),
    }

# ============================================
# 📋 PESTAÑAS
# ============================================

tab1, tab2 = st.tabs(["📋 Analizar Pedido Existente", "✨ Simular Nuevo Pedido"])

# ============================================
# 📋 PESTAÑA 1: ANALIZAR PEDIDO EXISTENTE
# ============================================

with tab1:
    st.markdown("### 🔍 Buscar Pedido Existente")
    st.markdown("Selecciona un pedido existente para analizar su riesgo de retraso")
    st.divider()
    
    # ============================================
    # MÉTODOS DE BÚSQUEDA
    # ============================================
    
    search_method = st.radio(
        "Selecciona cómo buscar:",
        ["📦 Por Producto", "🌍 Por País/Región", "🏷️ Por Categoría", "💰 Por Rango de Precio", "🔢 Por ID"],
        horizontal=True,
        key="search_method_existing"
    )
    
    st.divider()
    
    selected_order = None
    selected_order_id = None
    
    # ============================================
    # 📦 BÚSQUEDA POR PRODUCTO
    # ============================================
    
    if search_method == "📦 Por Producto":
        st.markdown("### 📦 Buscar por Producto")
        
        all_products = sorted(df['Product Name'].dropna().unique().tolist())
        search_term = st.text_input("🔎 Escribe el nombre del producto:", placeholder="Ej: Smart watch, Nike, ...", key="search_product")
        
        if search_term:
            filtered_products = [p for p in all_products if search_term.lower() in p.lower()]
            
            if filtered_products:
                st.success(f"✅ {len(filtered_products)} productos encontrados")
                selected_product = st.selectbox("Selecciona un producto:", options=filtered_products[:20], key="select_product")
                
                if selected_product:
                    product_orders = df[df['Product Name'] == selected_product]
                    st.info(f"📊 {len(product_orders)} pedidos encontrados para este producto")
                    
                    for idx, row in product_orders.head(10).iterrows():
                        col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1])
                        with col1:
                            st.write(f"🆔 {row['Order Id']}")
                        with col2:
                            st.write(f"📍 {row.get('Order Country', 'N/A')}")
                        with col3:
                            st.write(f"💰 ${row['Order Item Total']:.2f}")
                        with col4:
                            if st.button(f"Seleccionar", key=f"prod_existing_{row['Order Id']}"):
                                selected_order = row
                                selected_order_id = row['Order Id']
                                st.rerun()
            else:
                st.warning("⚠️ No se encontraron productos con ese nombre")
    
    # ============================================
    # 🌍 BÚSQUEDA POR PAÍS
    # ============================================
    
    elif search_method == "🌍 Por País/Región":
        st.markdown("### 🌍 Buscar por País o Región")
        
        if 'Order Country' in df.columns:
            countries = sorted(df['Order Country'].dropna().unique().tolist())
        elif 'Country' in df.columns:
            countries = sorted(df['Country'].dropna().unique().tolist())
        else:
            countries = ['USA', 'UK', 'Germany', 'France', 'Japan', 'Brazil', 'Australia', 'India', 'China', 'Mexico']
        
        selected_country = st.selectbox("Selecciona un país:", options=countries, key="select_country_existing")
        
        if selected_country:
            if 'Order Country' in df.columns:
                country_df = df[df['Order Country'] == selected_country]
            else:
                country_df = df[df['Country'] == selected_country]
            
            st.success(f"✅ {len(country_df)} pedidos encontrados en {selected_country}")
            
            for idx, row in country_df.head(15).iterrows():
                col1, col2, col3, col4 = st.columns([2, 2, 1.5, 1])
                with col1:
                    st.write(f"🆔 {row['Order Id']}")
                with col2:
                    st.write(f"📦 {row['Product Name'][:20]}...")
                with col3:
                    st.write(f"💰 ${row['Order Item Total']:.2f}")
                with col4:
                    if st.button(f"Seleccionar", key=f"country_existing_{row['Order Id']}"):
                        selected_order = row
                        selected_order_id = row['Order Id']
                        st.rerun()
    
    # ============================================
    # 🏷️ BÚSQUEDA POR CATEGORÍA
    # ============================================
    
    elif search_method == "🏷️ Por Categoría":
        st.markdown("### 🏷️ Buscar por Categoría")
        
        categories = sorted(df['Category Name'].dropna().unique().tolist())
        selected_category = st.selectbox("Selecciona una categoría:", options=categories, key="select_category_existing")
        
        if selected_category:
            category_df = df[df['Category Name'] == selected_category]
            st.success(f"✅ {len(category_df)} pedidos encontrados en {selected_category}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                late_count = category_df[category_df['Order Status'] == 'Late delivery'].shape[0] if 'Order Status' in category_df.columns else 0
                st.metric("⚠️ Retrasos", late_count)
            with col2:
                avg_price = category_df['Order Item Total'].mean()
                st.metric("💰 Precio Promedio", f"${avg_price:.2f}")
            with col3:
                st.metric("📦 Total Pedidos", len(category_df))
            
            for idx, row in category_df.head(15).iterrows():
                col1, col2, col3, col4 = st.columns([2, 2, 1.5, 1])
                with col1:
                    st.write(f"🆔 {row['Order Id']}")
                with col2:
                    st.write(f"📦 {row['Product Name'][:20]}...")
                with col3:
                    st.write(f"💰 ${row['Order Item Total']:.2f}")
                with col4:
                    if st.button(f"Seleccionar", key=f"cat_existing_{row['Order Id']}"):
                        selected_order = row
                        selected_order_id = row['Order Id']
                        st.rerun()
    
    # ============================================
    # 💰 BÚSQUEDA POR PRECIO
    # ============================================
    
    elif search_method == "💰 Por Rango de Precio":
        st.markdown("### 💰 Buscar por Rango de Precio")
        
        min_price = st.number_input("Precio mínimo:", min_value=0, value=50, step=10, key="min_price_existing")
        max_price = st.number_input("Precio máximo:", min_value=0, value=500, step=10, key="max_price_existing")
        
        if min_price < max_price:
            price_df = df[(df['Order Item Total'] >= min_price) & (df['Order Item Total'] <= max_price)]
            st.success(f"✅ {len(price_df)} pedidos encontrados en el rango de ${min_price} - ${max_price}")
            
            for idx, row in price_df.head(15).iterrows():
                col1, col2, col3, col4 = st.columns([2, 2, 1.5, 1])
                with col1:
                    st.write(f"🆔 {row['Order Id']}")
                with col2:
                    st.write(f"📦 {row['Product Name'][:20]}...")
                with col3:
                    st.write(f"💰 ${row['Order Item Total']:.2f}")
                with col4:
                    if st.button(f"Seleccionar", key=f"price_existing_{row['Order Id']}"):
                        selected_order = row
                        selected_order_id = row['Order Id']
                        st.rerun()
    
    # ============================================
    # 🔢 BÚSQUEDA POR ID
    # ============================================
    
    else:
        st.markdown("### 🔢 Buscar por ID")
        
        order_id_input = st.text_input("🔎 Ingresa el ID del pedido:", placeholder="Ej: 75903, 75931, ...", key="id_search_existing")
        
        if order_id_input:
            matching = df[df['Order Id'].astype(str).str.contains(order_id_input, case=False)]
            
            if not matching.empty:
                st.success(f"✅ {len(matching)} pedidos encontrados")
                
                for idx, row in matching.head(15).iterrows():
                    col1, col2, col3, col4 = st.columns([2, 2, 1.5, 1])
                    with col1:
                        st.write(f"🆔 {row['Order Id']}")
                    with col2:
                        st.write(f"📦 {row['Product Name'][:20]}...")
                    with col3:
                        st.write(f"💰 ${row['Order Item Total']:.2f}")
                    with col4:
                        if st.button(f"Seleccionar", key=f"id_existing_{row['Order Id']}"):
                            selected_order = row
                            selected_order_id = row['Order Id']
                            st.rerun()
            else:
                st.warning("⚠️ No se encontraron pedidos con ese ID")
    
    # ============================================
    # 🎯 MOSTRAR PREDICCIÓN (PESTAÑA 1)
    # ============================================
    
    if selected_order is not None:
        st.divider()
        
        with st.spinner("🔄 Analizando pedido..."):
            time.sleep(0.5)
            order_dict = selected_order.to_dict()
            prediction = ml.predict_delay(order_dict)
        
        order_info = {
            'Order Id': selected_order.get('Order Id', 'N/A'),
            'Product Name': selected_order.get('Product Name', 'N/A')
        }
        
        mostrar_resultado(prediction, order_info)
        
        if st.button("🔄 Buscar otro pedido", use_container_width=True, key="btn_search_another"):
            st.rerun()

# ============================================
# ✨ PESTAÑA 2: SIMULAR NUEVO PEDIDO
# ============================================

with tab2:
    st.markdown("### ✨ Simular Nuevo Pedido")
    st.markdown("Crea un escenario personalizado para predecir el riesgo de retraso")
    st.divider()
    
    # ============================================
    # 📦 FORMULARIO - SECCIÓN PRODUCTO
    # ============================================
    
    st.markdown('<div class="form-section-title">📦 Producto</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Categoría
        categorias = sorted(df["Category Name"].dropna().unique().tolist())
        categoria = st.selectbox("Categoría", options=categorias, key="sim_categoria")
    
    with col2:
        # Producto (filtrado por categoría)
        if categoria:
            productos = sorted(df[df["Category Name"] == categoria]["Product Name"].dropna().unique().tolist())
        else:
            productos = sorted(df["Product Name"].dropna().unique().tolist())
        
        if not productos:
            productos = ["No hay productos disponibles"]
        
        producto = st.selectbox("Producto", options=productos, key="sim_producto")
    
    with col3:
        # Cantidad
        cantidad = st.number_input("Cantidad", min_value=1, max_value=20, value=2, step=1, key="sim_cantidad")
    
    with col4:
        # Precio (se sugiere automáticamente)
        if producto and producto != "No hay productos disponibles":
            precio_sugerido = df[df["Product Name"] == producto]["Order Item Total"].mean()
            if pd.isna(precio_sugerido):
                precio_sugerido = 100.0
        else:
            precio_sugerido = 100.0
        
        precio = st.number_input("Precio", min_value=1.0, max_value=2000.0, value=float(precio_sugerido), step=5.0, key="sim_precio")
    
    st.divider()
    
    # ============================================
    # 🌍 SECCIÓN UBICACIÓN
    # ============================================
    
    st.markdown('<div class="form-section-title">🌍 Ubicación</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Mercado
        mercados = sorted(df["Market"].dropna().unique().tolist()) if "Market" in df.columns else ["Domestic", "International"]
        mercado = st.selectbox("Mercado", options=mercados, key="sim_mercado")
    
    with col2:
        # Región
        regiones = sorted(df["Order Region"].dropna().unique().tolist()) if "Order Region" in df.columns else sorted(df["Region"].dropna().unique().tolist())
        region = st.selectbox("Región", options=regiones, key="sim_region")
    
    with col3:
        # País
        if "Order Country" in df.columns:
            paises = sorted(df[df["Order Region"] == region]["Order Country"].dropna().unique().tolist()) if region and "Order Region" in df.columns else sorted(df["Order Country"].dropna().unique().tolist())
        elif "Country" in df.columns:
            paises = sorted(df[df["Region"] == region]["Country"].dropna().unique().tolist()) if region and "Region" in df.columns else sorted(df["Country"].dropna().unique().tolist())
        else:
            paises = ["USA", "UK", "Germany", "France", "Japan", "Brazil", "Australia", "India", "China", "Mexico"]
        
        if not paises:
            paises = ["No hay países disponibles"]
        
        pais = st.selectbox("País", options=paises, key="sim_pais")
    
    st.divider()
    
    # ============================================
    # 🚚 SECCIÓN LOGÍSTICA
    # ============================================
    
    st.markdown('<div class="form-section-title">🚚 Logística</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Modo de envío
        shipping_modes = sorted(df["Shipping Mode"].dropna().unique().tolist()) if "Shipping Mode" in df.columns else ["Standard", "Express", "Same Day"]
        shipping_mode = st.selectbox("Modo de Envío", options=shipping_modes, key="sim_shipping")
    
    with col2:
        # Estado del pedido
        order_statuses = sorted(df["Order Status"].dropna().unique().tolist()) if "Order Status" in df.columns else ["Processing", "Shipped", "Delivered", "Pending"]
        order_status = st.selectbox("Estado del Pedido", options=order_statuses, key="sim_status")
    
    st.divider()
    
    # ============================================
    # 👤 SECCIÓN CLIENTE
    # ============================================
    
    st.markdown('<div class="form-section-title">👤 Cliente</div>', unsafe_allow_html=True)
    
    if "Customer Segment" in df.columns:
        customer_segments = sorted(df["Customer Segment"].dropna().unique().tolist())
    else:
        customer_segments = ["Consumer", "Corporate", "Home Office"]
    
    customer_segment = st.selectbox("Segmento de Cliente", options=customer_segments, key="sim_segment")
    
    st.divider()
    
    # ============================================
    # 🔮 BOTÓN DE PREDICCIÓN
    # ============================================
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        predict_clicked = st.button("🔮 Analizar Riesgo", use_container_width=True, type="primary", key="btn_sim_predict")
    
    # ============================================
    # 🎯 RESULTADO DE SIMULACIÓN
    # ============================================
    
    if predict_clicked:
        # Construir diccionario del nuevo pedido
        nuevo_pedido = {
            'Category Name': categoria,
            'Product Name': producto,
            'Order Item Quantity': cantidad,
            'Order Item Total': precio,
            'Market': mercado,
            'Order Region': region,
            'Order Country': pais,
            'Shipping Mode': shipping_mode,
            'Order Status': order_status,
            'Customer Segment': customer_segment,
            'Days for shipping (real)': random.uniform(2, 10),
            'Days for shipment (scheduled)': random.uniform(2, 7),
            'Late_delivery_risk': 0,
            'Benefit per order': random.uniform(-20, 100),
            'Sales per customer': random.uniform(50, 500),
            'Order Item Discount Rate': random.uniform(0, 0.2),
            'Order Item Profit Ratio': random.uniform(0, 0.5),
        }
        
        with st.spinner("🔄 Analizando escenario..."):
            time.sleep(0.8)
            prediction = ml.predict_delay(nuevo_pedido)
        
        st.divider()
        
        # Mostrar resumen del escenario
        st.markdown("### 📋 Resumen del Escenario Simulado")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📦 Producto", producto[:20] + "..." if len(producto) > 20 else producto)
        with col2:
            st.metric("📍 Ubicación", f"{pais}")
        with col3:
            st.metric("📦 Cantidad", cantidad)
        with col4:
            st.metric("💰 Precio", f"${precio:.2f}")
        
        st.divider()
        
        # Mostrar resultado
        order_info = {
            'Order Id': '🆕 SIMULADO',
            'Product Name': producto
        }
        
        mostrar_resultado(prediction, order_info)

# ============================================
# 📊 FOOTER
# ============================================

st.divider()
st.caption("🔮 Los resultados son orientativos. La decisión final debe considerar otros factores.")