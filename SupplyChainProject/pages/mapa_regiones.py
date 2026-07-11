# ============================================
# 🌍 PÁGINA: MAPA DE REGIONES
# ============================================

elif current_page == 'Mapa_Regiones':
    st.markdown('<div class="section-title">🌍 Mapa de Entregas por Región</div>', unsafe_allow_html=True)

    # Preparar datos - USANDO COLUMNAS QUE EXISTEN
    columnas_disponibles = df.columns.tolist()
    
    # Verificar qué columnas tenemos
    if 'Country' in columnas_disponibles and 'Region' in columnas_disponibles:
        region_stats = df.groupby(['Country', 'Region']).agg({
            'Order Id': 'count',
            'Order Item Total': 'mean',
            'Order Status': lambda x: (x == 'Late delivery').sum()
        }).reset_index()
        region_stats.columns = ['Country', 'Region', 'Total Orders', 'Avg Order Value', 'Late Deliveries']
    else:
        # Si no tiene 'Country', usar solo 'Region' o la columna que tenga
        col_region = 'Region' if 'Region' in columnas_disponibles else columnas_disponibles[0]
        region_stats = df.groupby([col_region]).agg({
            'Order Id': 'count',
            'Order Item Total': 'mean',
            'Order Status': lambda x: (x == 'Late delivery').sum()
        }).reset_index()
        region_stats.columns = ['Region', 'Total Orders', 'Avg Order Value', 'Late Deliveries']
        region_stats['Country'] = region_stats['Region']  # Para el mapa

    region_stats['Delay Rate'] = (region_stats['Late Deliveries'] / region_stats['Total Orders'] * 100).fillna(0)

    # Si hay muy pocos datos, mostrar mensaje
    if len(region_stats) < 2:
        st.warning("⚠️ No hay suficientes datos de regiones para mostrar el mapa.")
        st.info("💡 Los datos de muestra tienen regiones limitadas. Cuando cargues el dataset real, el mapa se mostrará correctamente.")
        
        # Mostrar datos disponibles
        st.write("📊 Datos disponibles por región:")
        st.dataframe(region_stats, use_container_width=True)
    else:
        # Coordenadas simuladas para países/regiones
        country_coords = {
            'North America': {'lat': 45.0, 'lon': -100.0},
            'Europe': {'lat': 50.0, 'lon': 10.0},
            'Asia': {'lat': 35.0, 'lon': 105.0},
            'South America': {'lat': -15.0, 'lon': -60.0},
            'Africa': {'lat': 0.0, 'lon': 20.0},
            'Oceania': {'lat': -25.0, 'lon': 135.0},
            'USA': {'lat': 39.8283, 'lon': -98.5795},
            'UK': {'lat': 55.3781, 'lon': -3.4360},
            'Germany': {'lat': 51.1657, 'lon': 10.4515},
            'France': {'lat': 46.6034, 'lon': 1.8883},
            'Japan': {'lat': 36.2048, 'lon': 138.2529},
            'Brazil': {'lat': -14.2350, 'lon': -51.9253},
            'Australia': {'lat': -25.2744, 'lon': 133.7751},
            'India': {'lat': 20.5937, 'lon': 78.9629},
            'China': {'lat': 35.8617, 'lon': 104.1954},
            'Mexico': {'lat': 23.6345, 'lon': -102.5528},
            'Canada': {'lat': 56.1304, 'lon': -106.3468},
            'Spain': {'lat': 40.4637, 'lon': -3.7492},
            'Italy': {'lat': 41.8719, 'lon': 12.5674},
            'South Africa': {'lat': -30.5595, 'lon': 22.9375},
        }

        # Asignar coordenadas
        region_stats['Lat'] = region_stats['Country'].map(lambda x: country_coords.get(x, {'lat': 0})['lat'] if isinstance(x, str) else 0)
        region_stats['Lon'] = region_stats['Country'].map(lambda x: country_coords.get(x, {'lon': 0})['lon'] if isinstance(x, str) else 0)
        
        # Si no hay coordenadas, usar valores por defecto
        if region_stats['Lat'].sum() == 0:
            region_stats['Lat'] = 30.0
            region_stats['Lon'] = 0.0

        # Mapa
        st.subheader("🗺️ Mapa de Riesgo de Retrasos")
        fig = px.scatter_geo(
            region_stats,
            lat='Lat',
            lon='Lon',
            text='Country',
            size='Total Orders',
            color='Delay Rate',
            hover_data=['Region', 'Total Orders', 'Avg Order Value'],
            color_continuous_scale='Blues',
            title='Riesgo de Retrasos por Región'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#8899bb',
            height=500,
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type='natural earth'
            )
        )
        st.plotly_chart(fig, use_container_width=True)

        # Tabla
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🔴 Mayor Riesgo")
            top_risk = region_stats.sort_values('Delay Rate', ascending=False).head(10)
            st.dataframe(
                top_risk[['Country', 'Region', 'Total Orders', 'Delay Rate']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Country": "País/Región",
                    "Region": "Región",
                    "Total Orders": "Pedidos",
                    "Delay Rate": "Tasa Retraso (%)"
                }
            )

        with col2:
            st.subheader("🟢 Menor Riesgo")
            low_risk = region_stats.sort_values('Delay Rate', ascending=True).head(10)
            st.dataframe(
                low_risk[['Country', 'Region', 'Total Orders', 'Delay Rate']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Country": "País/Región",
                    "Region": "Región",
                    "Total Orders": "Pedidos",
                    "Delay Rate": "Tasa Retraso (%)"
                }
            )