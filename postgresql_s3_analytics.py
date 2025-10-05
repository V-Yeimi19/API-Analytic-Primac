import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from .s3_data_manager import s3_manager
import logging

logger = logging.getLogger(__name__)

class PostgreSQLAnalytics:
    """Análisis de datos PostgreSQL desde S3 - Versión Simplificada"""
    
    def __init__(self):
        self.s3_manager = s3_manager
    
    def get_product_analysis(self) -> Dict[str, Any]:
        """[GENERAL] Análisis completo de productos"""
        try:
            products_df = self.s3_manager.get_postgresql_data('products')
            
            total_products = len(products_df)
            
            # Productos por tipo
            product_types = products_df['product_type'].value_counts().to_dict() if 'product_type' in products_df.columns else {}
            
            # Análisis de primas base
            premium_stats = {}
            if 'base_premium' in products_df.columns:
                # Filtrar valores no nulos
                valid_premiums = products_df['base_premium'].dropna()
                
                premium_stats = {
                    "average_premium": round(valid_premiums.mean(), 2),
                    "median_premium": round(valid_premiums.median(), 2),
                    "min_premium": round(valid_premiums.min(), 2),
                    "max_premium": round(valid_premiums.max(), 2),
                    "std_premium": round(valid_premiums.std(), 2)
                }
                
                # Rangos de primas
                bins = [0, 100, 500, 1000, 5000, float('inf')]
                labels = ['< 100', '100-499', '500-999', '1000-4999', '5000+']
                products_df['premium_range'] = pd.cut(valid_premiums, bins=bins, labels=labels, include_lowest=True)
                premium_ranges = products_df['premium_range'].value_counts().to_dict()
                premium_stats["premium_distribution"] = {str(k): v for k, v in premium_ranges.items()}
            
            # Análisis de códigos de producto
            code_analysis = {}
            if 'code' in products_df.columns:
                code_analysis = {
                    "unique_codes": products_df['code'].nunique(),
                    "avg_code_length": round(products_df['code'].str.len().mean(), 1),
                    "code_patterns": self._analyze_code_patterns(products_df['code'])
                }
            
            # Análisis de nombres y descripciones
            text_analysis = {}
            if 'name' in products_df.columns:
                text_analysis['avg_name_length'] = round(products_df['name'].str.len().mean(), 1)
                text_analysis['common_words_in_names'] = self._get_common_words(products_df['name'])
            
            if 'description' in products_df.columns:
                valid_descriptions = products_df['description'].dropna()
                if len(valid_descriptions) > 0:
                    text_analysis['avg_description_length'] = round(valid_descriptions.str.len().mean(), 1)
                    text_analysis['products_with_description'] = len(valid_descriptions)
            
            return {
                "total_products": total_products,
                "product_types": product_types,
                "premium_statistics": premium_stats,
                "code_analysis": code_analysis,
                "text_analysis": text_analysis,
                "data_completeness": {
                    "products_with_premium": (~products_df['base_premium'].isnull()).sum() if 'base_premium' in products_df.columns else 0,
                    "products_with_description": (~products_df['description'].isnull()).sum() if 'description' in products_df.columns else 0,
                    "products_with_type": (~products_df['product_type'].isnull()).sum() if 'product_type' in products_df.columns else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error in product analysis: {e}")
            raise Exception(f"Error analyzing products: {str(e)}")
    
    def get_product_profitability_analysis(self) -> Dict[str, Any]:
        """[ESPECÍFICA] Análisis de rentabilidad por producto combinando productos y pólizas"""
        try:
            products_df = self.s3_manager.get_postgresql_data('products')
            policies_df = self.s3_manager.get_postgresql_data('policies')
            
            # Combinar datos de productos y pólizas
            if 'product_id' in policies_df.columns and 'code' in products_df.columns:
                merged_df = pd.merge(policies_df, products_df, left_on='product_id', right_on='code', how='inner')
                
                # Análisis por producto
                product_metrics = merged_df.groupby(['product_id', 'name']).agg({
                    'policy_number': 'count',  # Número de pólizas
                    'premium': ['sum', 'mean'],  # Total y promedio de primas
                    'sum_insured': ['sum', 'mean'],  # Total y promedio asegurado
                    'base_premium': 'first'  # Prima base del producto
                }).round(2)
                
                # Aplanar columnas
                product_metrics.columns = ['_'.join(col).strip() for col in product_metrics.columns.values]
                product_metrics = product_metrics.reset_index()
                
                # Calcular métricas de rentabilidad
                product_metrics['premium_efficiency'] = (
                    product_metrics['premium_mean'] / product_metrics['base_premium_first']
                ).round(2)
                
                product_metrics['total_exposure'] = product_metrics['sum_insured_sum']
                product_metrics['premium_to_exposure_ratio'] = (
                    (product_metrics['premium_sum'] / product_metrics['sum_insured_sum']) * 100
                ).round(2)
                
                # Top productos por diferentes métricas
                top_by_volume = product_metrics.nlargest(10, 'policy_number_count')[
                    ['product_id', 'name', 'policy_number_count', 'premium_sum']
                ].to_dict('records')
                
                top_by_premium = product_metrics.nlargest(10, 'premium_sum')[
                    ['product_id', 'name', 'premium_sum', 'policy_number_count']
                ].to_dict('records')
                
                top_by_efficiency = product_metrics.nlargest(10, 'premium_efficiency')[
                    ['product_id', 'name', 'premium_efficiency', 'premium_mean']
                ].to_dict('records')
                
                # Resumen general
                summary = {
                    "total_products_with_policies": len(product_metrics),
                    "total_policies_analyzed": product_metrics['policy_number_count'].sum(),
                    "total_premium_volume": round(product_metrics['premium_sum'].sum(), 2),
                    "average_policies_per_product": round(product_metrics['policy_number_count'].mean(), 2),
                    "average_premium_efficiency": round(product_metrics['premium_efficiency'].mean(), 2)
                }
                
                return {
                    "summary": summary,
                    "top_products_by_volume": top_by_volume,
                    "top_products_by_premium": top_by_premium,
                    "top_products_by_efficiency": top_by_efficiency,
                    "product_performance_matrix": product_metrics.to_dict('records')[:20]
                }
            else:
                return {"error": "Required columns not found for product profitability analysis"}
            
        except Exception as e:
            logger.error(f"Error in product profitability analysis: {e}")
            raise Exception(f"Error analyzing product profitability: {str(e)}")
    
    def _analyze_code_patterns(self, codes: pd.Series) -> Dict[str, Any]:
        """Analiza patrones en códigos de producto"""
        patterns = {}
        
        # Prefijos comunes
        prefixes = codes.str[:3].value_counts().head(5)
        patterns['common_prefixes'] = prefixes.to_dict()
        
        # Longitudes de código
        lengths = codes.str.len().value_counts()
        patterns['length_distribution'] = lengths.to_dict()
        
        # Patrones numéricos vs alfanuméricos
        numeric_count = codes.str.match(r'^\d+$').sum()
        alpha_count = codes.str.match(r'^[A-Za-z]+$').sum()
        mixed_count = len(codes) - numeric_count - alpha_count
        
        patterns['format_distribution'] = {
            'numeric_only': int(numeric_count),
            'alpha_only': int(alpha_count),
            'mixed': int(mixed_count)
        }
        
        return patterns
    
    def _get_common_words(self, text_series: pd.Series, top_n: int = 10) -> Dict[str, int]:
        """Extrae palabras comunes de una serie de texto"""
        try:
            # Convertir a string y dividir en palabras
            all_words = text_series.dropna().str.lower().str.split().explode()
            
            # Filtrar palabras comunes/conectores
            stop_words = {'de', 'la', 'el', 'en', 'y', 'a', 'que', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'un', 'una'}
            filtered_words = all_words[~all_words.isin(stop_words)]
            
            # Contar palabras
            word_counts = filtered_words.value_counts().head(top_n)
            return word_counts.to_dict()
            
        except Exception:
            return {}

# Instancia global
postgresql_analytics = PostgreSQLAnalytics()
