"""
paginas/inicio.py
====================
Página "Inicio": hero, panel de arquitectura híbrida, stat de total de
pedidos, filtros, KPIs dinámicos y gráficas de tendencia.
"""

import streamlit as st

from datos import (
    cargar_datos_dashboard,
    calcular_kpis,
    formatear_moneda,
    grafica_estado_pedidos,
    grafica_tendencia_ventas,
    grafica_top_paises,
)

_ICONO_SQL = (
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<ellipse cx="12" cy="5" rx="8" ry="3"/>'
    '<path d="M4 5v6c0 1.66 3.58 3 8 3s8-1.34 8-3V5"/>'
    '<path d="M4 11v6c0 1.66 3.58 3 8 3s8-1.34 8-3v-6"/></svg>'
)
_ICONO_MONGO = (
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M12 2C8 4 6 8 6 13c0 4 2.5 7 6 9 3.5-2 6-5 6-9 0-5-2-9-6-11z"/>'
    '<path d="M12 22V13"/></svg>'
)


def render() -> None:
    # --- Hero + panel de arquitectura híbrida ---
    col_hero, col_lateral = st.columns([2.4, 1], gap="large")

    with col_hero:
        st.markdown(
            """
            <p class="gdlm-hero-title">SISTEMA INTELIGENTE PARA PREDICCIÓN DEL ESTADO DE PEDIDOS</p>
            <p class="gdlm-hero-desc">
                Monitoreo operativo de la cadena de suministro: pedidos,
                ventas y desempeño de envíos, con modelos de Machine Learning
                supervisado y no supervisado sobre la misma base relacional.
            </p>
            """,
            unsafe_allow_html=True,
        )

    with col_lateral:
        st.markdown(
            f"""
            <div class="gdlm-arch-panel">
                <div class="gdlm-arch-eyebrow">🗄️ Arquitectura de persistencia híbrida</div>
                <div class="gdlm-engine-row">
                    <div class="gdlm-engine-icon sql">{_ICONO_SQL}</div>
                    <div>
                        <div class="gdlm-engine-name">SQL Server</div>
                        <div class="gdlm-engine-role">Datos estructurados</div>
                    </div>
                    <div class="gdlm-engine-tag"><span class="dot"></span>Activo</div>
                </div>
                <div class="gdlm-engine-row">
                    <div class="gdlm-engine-icon mongo">{_ICONO_MONGO}</div>
                    <div>
                        <div class="gdlm-engine-name">MongoDB</div>
                        <div class="gdlm-engine-role">Datos no estructurados</div>
                    </div>
                    <div class="gdlm-engine-tag"><span class="dot"></span>Activo</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    df = cargar_datos_dashboard()
    fecha_min = df["fecha_pedido"].min().date()
    fecha_max = df["fecha_pedido"].max().date()

    # --- Total de pedidos: stat destacado, SIEMPRE sobre el histórico
    # completo (no se filtra) — separado a propósito de las métricas
    # dinámicas de más abajo. ---
    st.markdown(
        f"""
        <div class="gdlm-total-card">
            <div class="gdlm-total-icon">📦</div>
            <div>
                <div class="gdlm-total-label">Pedidos registrados en el sistema</div>
                <div class="gdlm-total-value">{len(df):,}</div>
                <div class="gdlm-total-caption">Histórico completo · {fecha_min:%b %Y} — {fecha_max:%b %Y}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Filtros ---
    st.markdown('<div class="gdlm-section-label">Filtros</div>', unsafe_allow_html=True)
    with st.container(border=True):
        col_f1, col_f2, col_f3, col_f4 = st.columns([1.2, 1.2, 1, 1], gap="medium")

        with col_f1:
            fecha_inicio = st.date_input("Desde", value=fecha_min, min_value=fecha_min, max_value=fecha_max)
        with col_f2:
            fecha_fin = st.date_input("Hasta", value=fecha_max, min_value=fecha_min, max_value=fecha_max)
        with col_f3:
            paises = ["Todos"] + sorted(df["pais_destino"].dropna().unique().tolist())
            pais_sel = st.selectbox("País destino", paises)
        with col_f4:
            categorias = ["Todas"] + sorted(df["nombre_categoria"].dropna().unique().tolist())
            categoria_sel = st.selectbox("Categoría", categorias)

    # --- Aplicar filtros ---
    df_filtrado = df[
        (df["fecha_pedido"].dt.date >= fecha_inicio) & (df["fecha_pedido"].dt.date <= fecha_fin)
    ]
    if pais_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["pais_destino"] == pais_sel]
    if categoria_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["nombre_categoria"] == categoria_sel]

    kpis = calcular_kpis(df_filtrado)

    # --- Encabezado de métricas dinámicas + última actualización ---
    col_label, col_refresh = st.columns([4, 1])
    with col_label:
        st.markdown('<div class="gdlm-section-label">Métricas según filtros</div>', unsafe_allow_html=True)
    with col_refresh:
        if st.button("🔄 Actualizar datos", key="btn_refrescar", use_container_width=True):
            cargar_datos_dashboard.clear()
            st.rerun()

    # --- Tarjetas de KPI dinámicas ---
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(
            f"""<div class="gdlm-kpi-card">
                <div class="gdlm-kpi-icon">💰</div>
                <div class="gdlm-kpi-label">Ventas Totales</div>
                <div class="gdlm-kpi-value">{formatear_moneda(kpis['ventas_totales'])}</div>
                <div class="gdlm-kpi-caption">{len(df_filtrado):,} pedidos en el rango filtrado</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""<div class="gdlm-kpi-card">
                <div class="gdlm-kpi-icon">📈</div>
                <div class="gdlm-kpi-label">Ganancia Total</div>
                <div class="gdlm-kpi-value">{formatear_moneda(kpis['ganancia_total'])}</div>
                <div class="gdlm-kpi-caption">Margen sobre ventas filtradas</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""<div class="gdlm-kpi-card">
                <div class="gdlm-kpi-icon">🚚</div>
                <div class="gdlm-kpi-label">Tiempo Prom. Envío</div>
                <div class="gdlm-kpi-value">{kpis['tiempo_promedio_envio']} <span style="font-size:0.9rem;">días</span></div>
                <div class="gdlm-kpi-caption">Desde pedido hasta despacho</div>
            </div>""",
            unsafe_allow_html=True,
        )

    # --- Gráficas ligeras (respetan los mismos filtros que los KPIs) ---
    st.markdown('<div class="gdlm-section-label">Tendencias</div>', unsafe_allow_html=True)

    if df_filtrado.empty:
        st.info("No hay datos para los filtros seleccionados.")
    else:
        g1, g2, g3 = st.columns(3, gap="medium")

        with g1:
            with st.container(key="chart_card_estado"):
                st.markdown('<div class="gdlm-chart-title">Estado de pedidos</div>', unsafe_allow_html=True)
                st.plotly_chart(
                    grafica_estado_pedidos(kpis),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )

        with g2:
            with st.container(key="chart_card_tendencia"):
                st.markdown('<div class="gdlm-chart-title">Tendencia de ventas</div>', unsafe_allow_html=True)
                st.plotly_chart(
                    grafica_tendencia_ventas(df_filtrado),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )

        with g3:
            with st.container(key="chart_card_paises"):
                st.markdown('<div class="gdlm-chart-title">Top 5 países por ventas</div>', unsafe_allow_html=True)
                st.plotly_chart(
                    grafica_top_paises(df_filtrado),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
