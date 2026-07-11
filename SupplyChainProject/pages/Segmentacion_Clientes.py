import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Segmentación de Clientes",
    page_icon="👥",
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

st.markdown('<div class="section-title">👥 Segmentación de Clientes</div>', unsafe_allow_html=True)

# Preparar datos de clientes
customer_data = df.groupby('Customer Id').agg({
    'Order Id': 'count',
    'Order Item Total': ['sum', 'mean'],
    'Order Status': lambda x: (x == 'Late delivery').sum()
}).reset_index()
customer_data.columns = ['Customer Id', 'Total Orders', 'Total Spent', 'Avg Order Value', 'Late Deliveries']
customer_data['Delay Rate'] = (customer_data['Late Deliveries'] / customer_data['Total Orders'] * 100).fillna(0)

# Métricas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("👥 Total Clientes", f"{len(customer_data):,}")
with col2:
    st.metric("📦 Promedio Pedidos", f"{customer_data['Total Orders'].mean():.1f}")
with col3:
    high_risk = customer_data[customer_data['Delay Rate'] > 50].shape[0]
    st.metric("⚠️ Clientes Alto Riesgo", f"{high_risk}")
with col4:
    st.metric("💰 Gasto Promedio", f"${customer_data['Total Spent'].mean():,.2f}")

st.divider()

# Scatter plot
st.subheader("🎯 Distribución de Clientes")
fig = px.scatter(
    customer_data.sample(min(500, len(customer_data))),
    x='Total Orders',
    y='Total Spent',
    color='Delay Rate',
    size='Avg Order Value',
    hover_data=['Customer Id'],
    color_continuous_scale='Blues',
    title='Clientes por Comportamiento'
)
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color='#8899bb',
    height=500
)
st.plotly_chart(fig, use_container_width=True)

# Tabla clientes alto riesgo
st.subheader("🔴 Clientes con Mayor Riesgo")
high_risk_customers = customer_data.sort_values('Delay Rate', ascending=False).head(20)
st.dataframe(
    high_risk_customers[['Customer Id', 'Total Orders', 'Delay Rate', 'Total Spent']],
    use_container_width=True,
    hide_index=True,
    column_config={
        "Customer Id": "ID Cliente",
        "Total Orders": "Pedidos",
        "Delay Rate": "Tasa Retraso (%)",
        "Total Spent": "Gasto Total"
    }
)

st.caption(f"📊 Mostrando {len(customer_data):,} clientes | Conectado a: {'MongoDB Atlas' if st.session_state.get('db_connected', False) else 'Datos de muestra'}")