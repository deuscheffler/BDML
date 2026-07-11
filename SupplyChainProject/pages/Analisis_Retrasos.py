import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Análisis de Retrasos",
    page_icon="📈",
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

st.markdown('<div class="section-title">📈 Análisis de Retrasos en Entregas</div>', unsafe_allow_html=True)

# Métricas
col1, col2, col3, col4 = st.columns(4)

total_orders = len(df)
late_orders = df[df['Order Status'] == 'Late delivery'].shape[0]
on_time = df[df['Order Status'] == 'On Time'].shape[0]
avg_delay = df[df['Order Status'] == 'Late delivery']['Days for shipping (real)'].mean() if late_orders > 0 else 0

with col1:
    st.metric("📦 Total Pedidos", f"{total_orders:,}")
with col2:
    st.metric("⚠️ Retrasados", f"{late_orders:,}", delta=f"{late_orders/total_orders*100:.1f}%")
with col3:
    st.metric("✅ A Tiempo", f"{on_time:,}", delta=f"{on_time/total_orders*100:.1f}%")
with col4:
    st.metric("📅 Promedio Retraso", f"{avg_delay:.1f} días")

st.divider()

# Gráficos
col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Retrasos por Región")
    region_delay = df.groupby('Region').apply(
        lambda x: (x['Order Status'] == 'Late delivery').sum() / len(x) * 100
    ).reset_index()
    region_delay.columns = ['Región', 'Tasa Retraso (%)']
    region_delay = region_delay.sort_values('Tasa Retraso (%)', ascending=False)
    
    fig = px.bar(
        region_delay,
        x='Región',
        y='Tasa Retraso (%)',
        color='Tasa Retraso (%)',
        color_continuous_scale='Blues',
        text_auto='.1f'
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#8899bb',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🚢 Retrasos por Modo de Envío")
    shipping_delay = df.groupby('Shipping Mode').apply(
        lambda x: (x['Order Status'] == 'Late delivery').sum() / len(x) * 100
    ).reset_index()
    shipping_delay.columns = ['Modo Envío', 'Tasa Retraso (%)']
    shipping_delay = shipping_delay.sort_values('Tasa Retraso (%)', ascending=False)
    
    fig = px.bar(
        shipping_delay,
        x='Modo Envío',
        y='Tasa Retraso (%)',
        color='Tasa Retraso (%)',
        color_continuous_scale='Blues',
        text_auto='.1f'
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#8899bb',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

# Top productos
st.subheader("📦 Productos con Más Retrasos")
product_delay = df[df['Order Status'] == 'Late delivery']['Product Name'].value_counts().head(10).reset_index()
product_delay.columns = ['Producto', 'Retrasos']

fig = px.bar(
    product_delay,
    x='Retrasos',
    y='Producto',
    orientation='h',
    color='Retrasos',
    color_continuous_scale='Blues',
    text_auto=True
)
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color='#8899bb',
    height=500
)
st.plotly_chart(fig, use_container_width=True)

st.caption(f"📊 Mostrando {len(df):,} registros | Conectado a: {'MongoDB Atlas' if st.session_state.get('db_connected', False) else 'Datos de muestra'}")