import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import hashlib

def format_currency(value):
    """Formatea un valor como moneda"""
    try:
        return f"${value:,.2f}"
    except:
        return "$0.00"

def get_emoji_by_status(status):
    """Obtiene un emoji según el estado"""
    emoji_map = {
        'On Time': '✅',
        'Late delivery': '⚠️',
        'Shipped': '📦',
        'Cancelled': '❌',
        'Processing': '🔄',
        'Delivered': '📬'
    }
    return emoji_map.get(status, '📌')

def get_color_by_delay_rate(rate):
    """Obtiene un color según la tasa de retraso"""
    if rate < 10:
        return '#4ecdc4'
    elif rate < 30:
        return '#ffd93d'
    elif rate < 50:
        return '#ff922b'
    else:
        return '#ff6b6b'

def load_custom_css():
    try:
        with open('assets/css/style.css', 'r') as f:
            css = f.read()
        st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        default_css = """
        .main {
            background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 100%);
        }
        .stApp {
            background: transparent;
        }
        """
        st.markdown(f'<style>{default_css}</style>', unsafe_allow_html=True)

def generate_sample_data(n=1000):
    """Genera datos de muestra para pruebas"""
    np.random.seed(42)
    
    categories = ['Electronics', 'Clothing', 'Sports', 'Books', 'Home', 'Beauty']
    statuses = ['On Time', 'Late delivery', 'Shipped', 'Processing', 'Cancelled']
    regions = ['North America', 'Europe', 'Asia', 'South America', 'Africa', 'Oceania']
    countries = ['USA', 'UK', 'Germany', 'France', 'Japan', 'Brazil', 'Australia', 'India']
    markets = ['Domestic', 'International', 'Regional']
    shipping_modes = ['Standard', 'Express', 'Same Day', 'Next Day']
    sales_channels = ['Online', 'Retail', 'Wholesale']
    customer_segments = ['Consumer', 'Corporate', 'Home Office']
    
    data = []
    start_date = datetime(2023, 1, 1)
    
    for i in range(n):
        order_date = start_date + timedelta(days=random.randint(0, 365))
        status = random.choice(statuses)
        shipping_days = np.random.normal(5, 2)
        scheduled_days = np.random.normal(3, 1)
        
        data.append({
            'Order Id': f'ORD-{i+1:05d}',
            'Order Date': order_date,
            'Ship Date': order_date + timedelta(days=random.randint(1, 10)),
            'Customer Id': f'CUST-{random.randint(1000, 9999)}',
            'Customer Name': f'Customer {random.randint(100, 999)}',
            'Customer Segment': random.choice(customer_segments),
            'Product Name': f'Product {random.randint(1000, 9999)}',
            'Category Name': random.choice(categories),
            'Market': random.choice(markets),
            'Region': random.choice(regions),
            'Country': random.choice(countries),
            'Order Item Total': round(random.uniform(50, 500), 2),
            'Order Item Quantity': random.randint(1, 10),
            'Sales Channel': random.choice(sales_channels),
            'Shipping Mode': random.choice(shipping_modes),
            'Order Status': status,
            'Days for shipping (real)': round(max(0, shipping_days), 1),
            'Days for shipment (scheduled)': round(max(0, scheduled_days), 1)
        })
    
    return pd.DataFrame(data)

def hash_password(password):
    """Hashea una contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verifica una contraseña"""
    return hash_password(password) == hashed

def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'filtered_df' not in st.session_state:
        st.session_state.filtered_df = None
    if 'filters' not in st.session_state:
        st.session_state.filters = {}
    if 'db_connected' not in st.session_state:
        st.session_state.db_connected = False

def format_datetime(dt):
    """Formatea una fecha/hora"""
    if isinstance(dt, pd.Timestamp):
        dt = dt.to_pydatetime()
    if isinstance(dt, datetime):
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    return str(dt)

def calculate_delay_stats(df):
    """Calcula estadísticas de retrasos"""
    total = len(df)
    late = df[df['Order Status'] == 'Late delivery'].shape[0]
    on_time = df[df['Order Status'] == 'On Time'].shape[0]
    
    return {
        'total': total,
        'late': late,
        'on_time': on_time,
        'delay_rate': (late / total * 100) if total > 0 else 0,
        'on_time_rate': (on_time / total * 100) if total > 0 else 0
    }

def filter_dataframe(df, filters):
    """Aplica filtros a un DataFrame"""
    filtered_df = df.copy()
    
    for col, value in filters.items():
        if value and col in filtered_df.columns:
            if isinstance(value, list) and value:
                filtered_df = filtered_df[filtered_df[col].isin(value)]
            elif isinstance(value, tuple) and len(value) == 2:
                filtered_df = filtered_df[(filtered_df[col] >= value[0]) & (filtered_df[col] <= value[1])]
            elif isinstance(value, (int, float, str)):
                filtered_df = filtered_df[filtered_df[col] == value]
    
    return filtered_df