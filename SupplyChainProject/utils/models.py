import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

class MLModelLoader:
    """
    Carga y maneja los modelos de Machine Learning
    
    Características:
    - Carga automática de modelos desde la carpeta 'models/'
    - Fallback a simulación si no hay modelos
    - Identificación de factores de riesgo
    - Información detallada del estado de los modelos
    """
    
    def __init__(self):
        self.models_dir = "models/"
        self.classifier = None
        self.cluster = None
        self.scaler = None
        self.is_loaded = False
        self.model_status = {
            'classifier': False,
            'cluster': False,
            'scaler': False
        }
        self.last_prediction = None
        self.prediction_history = []
    
    def load_models(self):
        """
        Carga los modelos desde archivos.
        Si no encuentra un modelo, usa simulación como fallback.
        """
        try:
            # 1. Cargar modelo de clasificación (Andrés)
            classifier_path = f"{self.models_dir}classifier.pkl"
            if os.path.exists(classifier_path):
                try:
                    self.classifier = joblib.load(classifier_path)
                    self.model_status['classifier'] = True
                    st.sidebar.success("✅ Modelo de clasificación cargado (Andrés)")
                except Exception as e:
                    st.sidebar.warning(f"⚠️ Error al cargar classifier.pkl: {e}")
            else:
                st.sidebar.info("ℹ️ Modelo de clasificación no encontrado. Usando simulación.")
                st.sidebar.info("   → Coloca 'classifier.pkl' en la carpeta 'models/'")
            
            # 2. Cargar modelo de clustering (Mika)
            cluster_path = f"{self.models_dir}cluster.pkl"
            if os.path.exists(cluster_path):
                try:
                    self.cluster = joblib.load(cluster_path)
                    self.model_status['cluster'] = True
                    st.sidebar.success("✅ Modelo de clustering cargado (Mika)")
                except Exception as e:
                    st.sidebar.warning(f"⚠️ Error al cargar cluster.pkl: {e}")
            else:
                st.sidebar.info("ℹ️ Modelo de clustering no encontrado. Usando simulación.")
                st.sidebar.info("   → Coloca 'cluster.pkl' en la carpeta 'models/'")
            
            # 3. Cargar escalador (opcional)
            scaler_path = f"{self.models_dir}scaler.pkl"
            if os.path.exists(scaler_path):
                try:
                    self.scaler = joblib.load(scaler_path)
                    self.model_status['scaler'] = True
                    st.sidebar.success("✅ Escalador cargado")
                except Exception as e:
                    st.sidebar.warning(f"⚠️ Error al cargar scaler.pkl: {e}")
            
            # Determinar si hay al menos un modelo cargado
            self.is_loaded = self.model_status['classifier'] or self.model_status['cluster']
            
            if self.is_loaded:
                st.sidebar.success("🎯 Modelos ML listos para usar")
            else:
                st.sidebar.info("🔄 Usando modo simulación (sin modelos ML)")
            
            return True
            
        except Exception as e:
            st.sidebar.error(f"❌ Error general al cargar modelos: {e}")
            self.is_loaded = False
            return False
    
    def predict_delay(self, features):
        """
        Predice la probabilidad de retraso de un pedido
        
        Args:
            features (dict): Diccionario con las características del pedido
            
        Returns:
            dict: {
                'probability': float (0-100),
                'risk_level': str,
                'risk_color': str,
                'risk_factors': list,
                'model_used': str,
                'is_ml': bool
            }
        """
        # SI HAY MODELO DE CLASIFICACIÓN, USARLO
        if self.model_status['classifier'] and self.classifier is not None:
            try:
                # Preparar features para el modelo
                X = self._prepare_features(features)
                
                # Aplicar escalado si existe
                if self.scaler is not None:
                    X = self.scaler.transform(X)
                
                # Hacer predicción
                prob = self.classifier.predict_proba(X)[0][1]  # Probabilidad de clase positiva (retraso)
                prob_percent = prob * 100
                
                # Identificar factores de riesgo reales
                risk_factors = self._identify_risk_factors(features)
                
                # Guardar en historial
                result = {
                    'probability': prob_percent,
                    'risk_level': self._get_risk_level(prob_percent),
                    'risk_color': self._get_risk_color(prob_percent),
                    'risk_factors': risk_factors,
                    'model_used': 'Modelo ML (Andrés)',
                    'is_ml': True
                }
                
                self.last_prediction = result
                self.prediction_history.append(result)
                
                return result
                
            except Exception as e:
                st.error(f"❌ Error en predicción ML: {e}")
                # Si falla, usar simulación
                return self._simulate_prediction(features)
        
        # SI NO HAY MODELO, USAR SIMULACIÓN
        else:
            return self._simulate_prediction(features)
    
    def _prepare_features(self, features):
        """
        PREPARA LAS FEATURES PARA EL MODELO DE CLASIFICACIÓN
        
        🔧 ANDRÉS: MODIFICA ESTA SECCIÓN SEGÚN TU MODELO
        
        Las features deben estar en el MISMO ORDEN que usaste para entrenar.
        """
        
        # ============================================
        # 🔧 ANDRÉS: AJUSTA ESTAS FEATURES
        # ============================================
        
        # Ejemplo con 8 features (¡REEMPLAZAR CON TUS FEATURES!)
        X = np.array([[
            float(features.get('shipping_days', 5)),              # Feature 1
            float(features.get('order_total', 100)),              # Feature 2
            float(features.get('quantity', 1)),                   # Feature 3
            float(features.get('late_delivery_risk', 0)),         # Feature 4
            float(features.get('benefit', 0)),                    # Feature 5
            float(features.get('sales_per_customer', 200)),       # Feature 6
            float(features.get('discount_rate', 0)),              # Feature 7
            float(features.get('profit_ratio', 0)),               # Feature 8
        ]])
        
        return X
    
    def _identify_risk_factors(self, features):
        """
        Identifica factores de riesgo basados en datos reales del pedido
        """
        factors = []
        
        # Factor 1: Tiempo de envío
        shipping = features.get('shipping_days', 5)
        scheduled = features.get('scheduled_days', 4)
        
        if shipping > scheduled * 1.5:
            factors.append({
                'icon': '📦',
                'severity': 'high',
                'message': f'Tiempo de envío: {shipping} días',
                'detail': f'vs {scheduled} días programados ({shipping - scheduled} días extra)'
            })
        elif shipping > scheduled:
            factors.append({
                'icon': '📦',
                'severity': 'medium',
                'message': f'Tiempo de envío: {shipping} días',
                'detail': f'vs {scheduled} días programados (ligeramente superior)'
            })
        
        # Factor 2: Riesgo del sistema
        if features.get('late_delivery_risk', 0) == 1:
            factors.append({
                'icon': '⚠️',
                'severity': 'high',
                'message': 'Riesgo de retraso marcado por el sistema',
                'detail': 'El sistema identificó este pedido con alto riesgo'
            })
        
        # Factor 3: Valor del pedido
        total = features.get('order_total', 100)
        if total > 500:
            factors.append({
                'icon': '💰',
                'severity': 'medium',
                'message': f'Pedido de alto valor (${total:.0f})',
                'detail': 'Requiere atención especial en la logística'
            })
        elif total > 300:
            factors.append({
                'icon': '💰',
                'severity': 'low',
                'message': f'Pedido de valor medio (${total:.0f})',
                'detail': 'Valor moderado'
            })
        
        # Factor 4: Cantidad de productos
        quantity = features.get('quantity', 1)
        if quantity > 5:
            factors.append({
                'icon': '📦',
                'severity': 'medium',
                'message': f'Pedido con {quantity} unidades',
                'detail': 'Mayor complejidad logística'
            })
        
        # Factor 5: Beneficio del pedido
        benefit = features.get('benefit', 0)
        if benefit < 0:
            factors.append({
                'icon': '📉',
                'severity': 'high',
                'message': f'Pedido con pérdida potencial (${benefit:.0f})',
                'detail': 'Pérdida en este pedido'
            })
        
        # Si no hay factores, agregar uno genérico
        if not factors:
            factors.append({
                'icon': '✅',
                'severity': 'low',
                'message': 'Sin factores de riesgo significativos',
                'detail': 'El pedido está en condiciones normales'
            })
        
        return factors
    
    def segment_customer(self, customer_features):
        """
        Segmenta un cliente usando el modelo de clustering
        
        Args:
            customer_features (dict): Diccionario con características del cliente
            
        Returns:
            dict: {
                'segment': int,
                'segment_name': str,
                'description': str,
                'is_ml': bool
            }
        """
        # SI HAY MODELO DE CLUSTERING, USARLO
        if self.model_status['cluster'] and self.cluster is not None:
            try:
                X = self._prepare_cluster_features(customer_features)
                
                if self.scaler is not None:
                    X = self.scaler.transform(X)
                
                segment = self.cluster.predict(X)[0]
                
                return {
                    'segment': segment,
                    'segment_name': self._get_segment_name(segment),
                    'description': self._get_segment_description(segment),
                    'is_ml': True
                }
                
            except Exception as e:
                st.error(f"❌ Error en segmentación: {e}")
                return self._simulate_segment(customer_features)
        
        # SI NO HAY MODELO, USAR SIMULACIÓN
        else:
            return self._simulate_segment(customer_features)
    
    def _prepare_cluster_features(self, customer_features):
        """
        PREPARA LAS FEATURES PARA EL MODELO DE CLUSTERING
        
        🔧 MIKA: MODIFICA ESTA SECCIÓN SEGÚN TU MODELO
        """
        
        # ============================================
        # 🔧 MIKA: AJUSTA ESTAS FEATURES
        # ============================================
        
        X = np.array([[
            float(customer_features.get('total_orders', 0)),      # Feature 1
            float(customer_features.get('total_spent', 0)),       # Feature 2
            float(customer_features.get('delay_rate', 0)),        # Feature 3
            float(customer_features.get('avg_order_value', 0)),   # Feature 4
            float(customer_features.get('category_count', 0)),    # Feature 5
        ]])
        
        return X
    
    def _get_risk_level(self, prob):
        """Obtiene el nivel de riesgo según la probabilidad"""
        if prob >= 70:
            return '🔴 ALTO RIESGO'
        elif prob >= 40:
            return '🟡 RIESGO MODERADO'
        else:
            return '🟢 BAJO RIESGO'
    
    def _get_risk_color(self, prob):
        """Obtiene el color según la probabilidad"""
        if prob >= 70:
            return '#ff6b6b'
        elif prob >= 40:
            return '#ffd93d'
        else:
            return '#4fc3f7'
    
    def _get_segment_name(self, segment):
        """Obtiene el nombre del segmento"""
        # 🔧 MIKA: Personaliza estos nombres según tu modelo
        segment_names = {
            0: '🔵 Cliente Estándar',
            1: '🟢 Cliente Frecuente',
            2: '🟡 Cliente VIP',
            3: '🔴 Cliente de Alto Riesgo',
        }
        return segment_names.get(segment, f'Segmento {segment}')
    
    def _get_segment_description(self, segment):
        """Obtiene la descripción del segmento"""
        # 🔧 MIKA: Personaliza estas descripciones
        descriptions = {
            0: 'Cliente con comportamiento regular',
            1: 'Cliente que compra frecuentemente',
            2: 'Cliente de alto valor y fidelidad',
            3: 'Cliente con alto riesgo de retrasos',
        }
        return descriptions.get(segment, 'Segmento no definido')
    
    def _simulate_prediction(self, features):
        """Predicción simulada (fallback cuando no hay modelo ML)"""
        import random
        prob = random.uniform(0, 100)
        
        # Factores simulados
        risk_factors = [
            {
                'icon': '📍',
                'severity': 'medium',
                'message': 'Región con tasa de retrasos: 32%',
                'detail': 'Basado en datos históricos de la región'
            },
            {
                'icon': '🏷️',
                'severity': 'low',
                'message': 'Categoría con historial de retrasos',
                'detail': 'Basado en análisis de categoría'
            },
            {
                'icon': '🚢',
                'severity': 'low',
                'message': 'Modo de envío estándar',
                'detail': 'Tasa de retrasos: 15% en este modo'
            }
        ]
        
        result = {
            'probability': prob,
            'risk_level': self._get_risk_level(prob),
            'risk_color': self._get_risk_color(prob),
            'risk_factors': risk_factors,
            'model_used': 'Simulación (sin modelo ML)',
            'is_ml': False
        }
        
        self.last_prediction = result
        self.prediction_history.append(result)
        
        return result
    
    def _simulate_segment(self, customer_features):
        """Segmentación simulada (fallback)"""
        import random
        segment = random.randint(0, 3)
        
        return {
            'segment': segment,
            'segment_name': self._get_segment_name(segment),
            'description': self._get_segment_description(segment),
            'is_ml': False
        }
    
    def get_model_status(self):
        """Retorna el estado de los modelos"""
        return {
            'classifier_loaded': self.model_status['classifier'],
            'cluster_loaded': self.model_status['cluster'],
            'scaler_loaded': self.model_status['scaler'],
            'any_loaded': self.is_loaded
        }
    
    def get_model_info(self):
        """Retorna información detallada de los modelos"""
        info = {
            'models_loaded': [],
            'models_missing': [],
            'total_models': 2,
            'loaded_count': 0
        }
        
        if self.model_status['classifier']:
            info['models_loaded'].append('Clasificación (Andrés)')
            info['loaded_count'] += 1
        else:
            info['models_missing'].append('Clasificación (Andrés) → classifier.pkl')
        
        if self.model_status['cluster']:
            info['models_loaded'].append('Clustering (Mika)')
            info['loaded_count'] += 1
        else:
            info['models_missing'].append('Clustering (Mika) → cluster.pkl')
        
        return info
    
    def get_prediction_history(self, limit=10):
        """Obtiene el historial de predicciones"""
        return self.prediction_history[-limit:] if self.prediction_history else []
    
    def get_statistics(self):
        """Obtiene estadísticas de las predicciones"""
        if not self.prediction_history:
            return {
                'total_predictions': 0,
                'avg_probability': 0,
                'high_risk_count': 0,
                'moderate_risk_count': 0,
                'low_risk_count': 0
            }
        
        probs = [p['probability'] for p in self.prediction_history]
        high = sum(1 for p in self.prediction_history if p['probability'] >= 70)
        moderate = sum(1 for p in self.prediction_history if 40 <= p['probability'] < 70)
        low = sum(1 for p in self.prediction_history if p['probability'] < 40)
        
        return {
            'total_predictions': len(self.prediction_history),
            'avg_probability': np.mean(probs),
            'high_risk_count': high,
            'moderate_risk_count': moderate,
            'low_risk_count': low
        }