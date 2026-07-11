import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard General",
    page_icon="📊",
    layout="wide"
)

if 'filtered_df' not in st.session_state or st.session_state.filtered_df is None:
    st.warning("⚠️ No hay datos disponibles")
    st.stop()

df = st.session_state.filtered_df

st.markdown("""
<style>
.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    font-weight: 600;
    background: linear-gradient(135deg, #4fc3f7 0%, #00b4d8 60%, #0288d1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 24px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">📊 Dashboard General</div>', unsafe_allow_html=True)

# Métricas
col1, col2, col3, col4 = st.columns(4)

total_orders = len(df)
late_orders = df[df['Order Status'] == 'Late delivery'].shape[0]
delay_rate = (late_orders / total_orders * 100) if total_orders > 0 else 0
avg_shipping = df['Days for shipping (real)'].mean()
revenue = df['Order Item Total'].sum()

with col1:
    st.metric("📦 Total Pedidos", f"{total_orders:,}")
with col2:
    st.metric("⚠️ Tasa de Retrasos", f"{delay_rate:.1f}%", delta=f"{late_orders} pedidos")
with col3:
    st.metric("🚚 Promedio Envío", f"{avg_shipping:.1f} días")
with col4:
    st.metric("💰 Ingreso Total", f"${revenue:,.0f}")

st.divider()

# Gráficos
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Distribución de Estados")
    status_dist = df['Order Status'].value_counts().reset_index()
    status_dist.columns = ['Estado', 'Cantidad']
    fig = px.pie(
        status_dist,
        values='Cantidad',
        names='Estado',
        hole=0.4,
        color_discrete_sequence=['#4fc3f7', '#ff6b6b', '#ffd93d', '#8899bb']
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#8899bb',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🏷️ Top Categorías")
    top_categories = df['Category Name'].value_counts().head(6).reset_index()
    top_categories.columns = ['Categoría', 'Cantidad']
    fig = px.bar(
        top_categories,
        x='Categoría',
        y='Cantidad',
        color='Cantidad',
        color_continuous_scale='Blues',
        text_auto=True
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#8899bb',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

# Tendencia
st.subheader("📈 Tendencia de Pedidos")
if 'Order Date' in df.columns:
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    daily_orders = df.groupby(df['Order Date'].dt.date).size().reset_index()
    daily_orders.columns = ['Fecha', 'Cantidad']
    
    fig = px.line(
        daily_orders,
        x='Fecha',
        y='Cantidad',
        title='Pedidos por Día',
        color_discrete_sequence=['#4fc3f7']
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#8899bb',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

st.caption(f"📊 Mostrando {len(df):,} registros | Conectado a: {'MongoDB Atlas' if st.session_state.get('db_connected', False) else 'Datos de muestra'}")