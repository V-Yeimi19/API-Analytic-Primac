import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from s3_data_manager import s3_manager
import logging

logger = logging.getLogger(__name__)

class CrossMicroserviceAnalytics:
    """Análisis cruzado entre microservicios usando datos de S3 - Versión Simplificada"""
    
    def __init__(self):
        self.s3_manager = s3_manager
    
    def get_customer_policy_profile(self) -> Dict[str, Any]:
        """
        [CROSS 1] JOIN entre MySQL (usuarios/clientes) y PostgreSQL (pólizas)
        Análisis del perfil de clientes y sus pólizas
        """
        try:
            # Cargar datos
            users_df = self.s3_manager.get_mysql_data('users')
            clients_df = self.s3_manager.get_mysql_data('clients')
            policies_df = self.s3_manager.get_postgresql_data('policies')
            
            # JOIN usuarios con clientes
            if 'id' in users_df.columns and 'user_id' in clients_df.columns:
                user_client_df = pd.merge(users_df, clients_df, left_on='id', right_on='user_id', how='inner', suffixes=('_user', '_client'))
            else:
                return {"error": "Cannot join users and clients - missing key columns"}
            
            # JOIN con pólizas usando customer_id
            if 'user_id' in user_client_df.columns and 'customer_id' in policies_df.columns:
                full_profile = pd.merge(user_client_df, policies_df, left_on='user_id', right_on='customer_id', how='left', suffixes=('', '_policy'))
            else:
                return {"error": "Cannot join clients with policies - missing customer_id"}
            
            # Análisis del perfil completo
            total_customers = len(user_client_df)
            customers_with_policies = len(full_profile[full_profile['policy_number'].notna()])
            
            # Análisis demográfico con pólizas
            demographic_analysis = {}
            
            # Por estado y pólizas
            if 'state' in full_profile.columns:
                state_policy_analysis = full_profile.groupby('state').agg({
                    'policy_number': ['count', 'nunique'],
                    'premium': ['sum', 'mean'],
                    'sum_insured': ['sum', 'mean']
                }).round(2)
                
                state_policy_analysis.columns = ['_'.join(col).strip() for col in state_policy_analysis.columns.values]
                demographic_analysis['by_state'] = state_policy_analysis.to_dict('index')
            
            # Por edad y pólizas
            if 'birth_date' in full_profile.columns:
                full_profile['birth_date'] = pd.to_datetime(full_profile['birth_date'])
                full_profile['age'] = (datetime.now() - full_profile['birth_date']).dt.days // 365
                
                # Grupos de edad
                bins = [0, 25, 35, 45, 55, 65, 100]
                labels = ['<25', '25-34', '35-44', '45-54', '55-64', '65+']
                full_profile['age_group'] = pd.cut(full_profile['age'], bins=bins, labels=labels, include_lowest=True)
                
                age_policy_analysis = full_profile.groupby('age_group').agg({
                    'policy_number': ['count', 'nunique'],
                    'premium': ['sum', 'mean'],
                    'age': 'mean'
                }).round(2)
                
                age_policy_analysis.columns = ['_'.join(col).strip() for col in age_policy_analysis.columns.values]
                demographic_analysis['by_age_group'] = {str(k): v for k, v in age_policy_analysis.to_dict('index').items()}
            
            # Análisis de valor de cliente
            customer_value = {}
            if 'premium' in full_profile.columns:
                customer_premiums = full_profile.groupby('user_id')['premium'].sum()
                customer_value = {
                    "high_value_customers": len(customer_premiums[customer_premiums > customer_premiums.quantile(0.8)]),
                    "medium_value_customers": len(customer_premiums[(customer_premiums > customer_premiums.quantile(0.4)) & (customer_premiums <= customer_premiums.quantile(0.8))]),
                    "low_value_customers": len(customer_premiums[customer_premiums <= customer_premiums.quantile(0.4)]),
                    "avg_customer_value": round(customer_premiums.mean(), 2),
                    "top_10_customers": customer_premiums.nlargest(10).to_dict()
                }
            
            # Resumen ejecutivo
            summary = {
                "total_customers": total_customers,
                "customers_with_policies": customers_with_policies,
                "penetration_rate": round((customers_with_policies / total_customers) * 100, 2) if total_customers > 0 else 0,
                "total_policies": len(full_profile[full_profile['policy_number'].notna()]),
                "total_premium_volume": round(full_profile['premium'].sum(), 2) if 'premium' in full_profile.columns else 0,
                "avg_policies_per_customer": round(len(full_profile[full_profile['policy_number'].notna()]) / customers_with_policies, 2) if customers_with_policies > 0 else 0
            }
            
            return {
                "summary": summary,
                "demographic_analysis": demographic_analysis,
                "customer_value_analysis": customer_value,
                "data_sources": {
                    "mysql_tables": ["users", "clients"],
                    "postgresql_tables": ["policies"],
                    "join_keys": ["user_id -> customer_id"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error in customer policy profile analysis: {e}")
            raise Exception(f"Error analyzing customer policy profiles: {str(e)}")
    
    def get_agent_performance_across_systems(self) -> Dict[str, Any]:
        """
        [CROSS 2] JOIN entre MySQL (agentes) y PostgreSQL (pólizas) para analizar rendimiento de agentes
        """
        try:
            # Cargar datos
            agents_df = self.s3_manager.get_mysql_data('agents')
            policies_df = self.s3_manager.get_postgresql_data('policies')
            products_df = self.s3_manager.get_postgresql_data('products')
            
            # JOIN agentes con pólizas
            if 'code' in agents_df.columns and 'agent_id' in policies_df.columns:
                agent_policies = pd.merge(agents_df, policies_df, left_on='code', right_on='agent_id', how='left', suffixes=('_agent', '_policy'))
            else:
                return {"error": "Cannot join agents with policies - missing key columns"}
            
            # JOIN con productos para obtener información adicional
            if 'product_id' in agent_policies.columns and 'code' in products_df.columns:
                full_agent_data = pd.merge(agent_policies, products_df, left_on='product_id', right_on='code', how='left', suffixes=('', '_product'))
            else:
                full_agent_data = agent_policies  # Sin información de producto
            
            # Análisis de rendimiento por agente
            agent_performance = full_agent_data.groupby(['code_agent', 'first_name', 'last_name', 'is_active']).agg({
                'policy_number': 'count',
                'premium': ['sum', 'mean'],
                'sum_insured': ['sum', 'mean'],
                'product_id': 'nunique'
            }).round(2)
            
            agent_performance.columns = ['_'.join(col).strip() for col in agent_performance.columns.values]
            agent_performance = agent_performance.reset_index()
            
            # Filtrar solo agentes con pólizas
            active_agents = agent_performance[agent_performance['policy_number_count'] > 0]
            
            # Ranking de agentes
            if len(active_agents) > 0:
                top_agents_by_volume = active_agents.nlargest(10, 'policy_number_count')[
                    ['code_agent', 'first_name', 'last_name', 'policy_number_count', 'premium_sum']
                ].to_dict('records')
                
                top_agents_by_premium = active_agents.nlargest(10, 'premium_sum')[
                    ['code_agent', 'first_name', 'last_name', 'premium_sum', 'policy_number_count']
                ].to_dict('records')
                
                # Análisis de diversificación (agentes que venden más tipos de productos)
                top_diversified_agents = active_agents.nlargest(10, 'product_id_nunique')[
                    ['code_agent', 'first_name', 'last_name', 'product_id_nunique', 'policy_number_count']
                ].to_dict('records')
            else:
                top_agents_by_volume = []
                top_agents_by_premium = []
                top_diversified_agents = []
            
            # Resumen ejecutivo
            total_agents = len(agents_df)
            active_agents_count = len(agents_df[agents_df['is_active'] == True]) if 'is_active' in agents_df.columns else total_agents
            agents_with_sales = len(active_agents)
            
            summary = {
                "total_agents": total_agents,
                "active_agents": active_agents_count,
                "agents_with_sales": agents_with_sales,
                "sales_penetration": round((agents_with_sales / active_agents_count) * 100, 2) if active_agents_count > 0 else 0,
                "total_policies_sold": int(active_agents['policy_number_count'].sum()) if len(active_agents) > 0 else 0,
                "total_premium_generated": round(active_agents['premium_sum'].sum(), 2) if len(active_agents) > 0 else 0,
                "avg_policies_per_agent": round(active_agents['policy_number_count'].mean(), 2) if len(active_agents) > 0 else 0
            }
            
            return {
                "summary": summary,
                "top_performers": {
                    "by_volume": top_agents_by_volume,
                    "by_premium": top_agents_by_premium,
                    "by_diversification": top_diversified_agents
                },
                "data_sources": {
                    "mysql_tables": ["agents"],
                    "postgresql_tables": ["policies", "products"],
                    "join_keys": ["agent.code -> policy.agent_id"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error in agent performance analysis: {e}")
            raise Exception(f"Error analyzing agent performance: {str(e)}")
    
    def get_claims_vs_policies_analysis(self) -> Dict[str, Any]:
        """
        [CROSS 3] JOIN entre PostgreSQL (pólizas) y Cassandra (reclamos) para análisis de siniestralidad
        """
        try:
            # Cargar datos
            policies_df = self.s3_manager.get_postgresql_data('policies')
            claims_df = self.s3_manager.get_cassandra_data('reclamos')
            products_df = self.s3_manager.get_postgresql_data('products')
            
            # Preparar datos de pólizas con productos
            if 'product_id' in policies_df.columns and 'code' in products_df.columns:
                policies_with_products = pd.merge(policies_df, products_df, left_on='product_id', right_on='code', how='left', suffixes=('_policy', '_product'))
            else:
                policies_with_products = policies_df
            
            # JOIN pólizas con reclamos (asumiendo que hay un campo policy_id en reclamos)
            if 'id' in policies_df.columns:
                # Si hay policy_id en claims
                if 'policy_id' in claims_df.columns:
                    claims_policies = pd.merge(policies_with_products, claims_df, left_on='id', right_on='policy_id', how='left', suffixes=('_policy', '_claim'))
                # Si hay policy_number en claims
                elif 'policy_number' in claims_df.columns:
                    claims_policies = pd.merge(policies_with_products, claims_df, on='policy_number', how='left', suffixes=('_policy', '_claim'))
                else:
                    # Análisis separado si no hay conexión directa
                    return self._analyze_separate_claims_policies(policies_with_products, claims_df)
            else:
                return self._analyze_separate_claims_policies(policies_with_products, claims_df)
            
            # Análisis de siniestralidad
            total_policies = len(policies_with_products)
            policies_with_claims = len(claims_policies[claims_policies['estado'].notna()]) if 'estado' in claims_policies.columns else 0
            
            # Tasa de siniestralidad
            claim_rate = round((policies_with_claims / total_policies) * 100, 2) if total_policies > 0 else 0
            
            # Análisis por producto
            product_analysis = {}
            if 'name_product' in claims_policies.columns and 'estado' in claims_policies.columns:
                product_claims = claims_policies.groupby('name_product').agg({
                    'policy_number_policy': 'count',  # Total de pólizas
                    'estado': lambda x: x.notna().sum(),  # Pólizas con reclamos
                    'monto': ['sum', 'mean', 'count'] if 'monto' in claims_policies.columns else 'count'
                }).round(2)
                
                product_claims.columns = ['_'.join(col).strip() for col in product_claims.columns.values]
                product_analysis = product_claims.to_dict('index')
            
            # Análisis de montos si están disponibles
            financial_analysis = {}
            if 'monto' in claims_policies.columns and 'premium' in claims_policies.columns:
                total_claims_amount = claims_policies['monto'].sum()
                total_premiums = claims_policies['premium'].sum()
                
                financial_analysis = {
                    "total_claims_amount": round(total_claims_amount, 2),
                    "total_premiums": round(total_premiums, 2),
                    "loss_ratio": round((total_claims_amount / total_premiums) * 100, 2) if total_premiums > 0 else 0,
                    "avg_claim_amount": round(claims_policies[claims_policies['monto'].notna()]['monto'].mean(), 2)
                }
            
            return {
                "summary": {
                    "total_policies": total_policies,
                    "policies_with_claims": policies_with_claims,
                    "claim_rate_percentage": claim_rate,
                    "total_claims": len(claims_df)
                },
                "product_analysis": product_analysis,
                "financial_analysis": financial_analysis,
                "data_sources": {
                    "postgresql_tables": ["policies", "products"],
                    "cassandra_tables": ["reclamos"],
                    "join_approach": "policy_id or policy_number matching"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in claims vs policies analysis: {e}")
            raise Exception(f"Error analyzing claims vs policies: {str(e)}")
    
    def _analyze_separate_claims_policies(self, policies_df: pd.DataFrame, claims_df: pd.DataFrame) -> Dict[str, Any]:
        """Análisis separado cuando no hay JOIN directo disponible"""
        
        # Análisis general
        total_policies = len(policies_df)
        total_claims = len(claims_df)
        
        # Análisis temporal paralelo
        temporal_comparison = {}
        
        if 'created_at' in policies_df.columns:
            policies_df['created_at'] = pd.to_datetime(policies_df['created_at'])
            policies_df['month_year'] = policies_df['created_at'].dt.to_period('M')
            monthly_policies = policies_df.groupby('month_year').size()
            temporal_comparison['monthly_policies'] = {str(k): v for k, v in monthly_policies.tail(12).items()}
        
        if 'fecha_reclamo' in claims_df.columns:
            claims_df['fecha_reclamo'] = pd.to_datetime(claims_df['fecha_reclamo'])
            claims_df['month_year'] = claims_df['fecha_reclamo'].dt.to_period('M')
            monthly_claims = claims_df.groupby('month_year').size()
            temporal_comparison['monthly_claims'] = {str(k): v for k, v in monthly_claims.tail(12).items()}
        
        # Análisis de estados de reclamos
        claims_analysis = {}
        if 'estado' in claims_df.columns:
            claims_analysis['claims_by_status'] = claims_df['estado'].value_counts().to_dict()
        
        if 'monto' in claims_df.columns:
            claims_analysis['total_claims_amount'] = round(claims_df['monto'].sum(), 2)
            claims_analysis['avg_claim_amount'] = round(claims_df['monto'].mean(), 2)
        
        return {
            "summary": {
                "total_policies": total_policies,
                "total_claims": total_claims,
                "note": "Analysis performed separately - no direct JOIN possible"
            },
            "temporal_comparison": temporal_comparison,
            "claims_analysis": claims_analysis,
            "data_sources": {
                "postgresql_tables": ["policies"],
                "cassandra_tables": ["reclamos"],
                "join_approach": "separate analysis"
            }
        }

# Instancia global
cross_analytics = CrossMicroserviceAnalytics()
