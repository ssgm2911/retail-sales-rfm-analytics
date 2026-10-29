import pandas as pd
import numpy as np
from datetime import datetime

def procesar_rfm_y_ventas():
    # 1. Cargar Datasets
    print("📥 Cargando archivos CSV...")
    df_clientes = pd.read_csv('retail-sales-rfm-analytics/clientes_raw.csv')
    df_ventas = pd.read_csv('retail-sales-rfm-analytics/ventas_raw.csv')
    df_logistica = pd.read_csv('retail-sales-rfm-analytics/logistica_raw.csv')
    
    # Convertir fechas
    df_ventas['Fecha_Venta'] = pd.to_datetime(df_ventas['Fecha_Venta'])
    df_logistica['Fecha_Prometida'] = pd.to_datetime(df_logistica['Fecha_Prometida'])
    df_logistica['Fecha_Entrega_Real'] = pd.to_datetime(df_logistica['Fecha_Entrega_Real'])
    
    # 2. Análisis Exploratorio (EDA) Rápido
    print("\n--- 📊 RESUMEN EJECUTIVO (EDA) ---")
    total_ventas_usd = df_ventas['Monto_Total_USD'].sum()
    ganancia_total_usd = (df_ventas['Monto_Total_USD'] - df_ventas['Costo_Total_USD']).sum()
    ticket_promedio = df_ventas['Monto_Total_USD'].mean()
    
    print(f"💰 Ventas Totales: ${total_ventas_usd:,.2f} USD")
    print(f"📈 Ganancia Bruta: ${ganancia_total_usd:,.2f} USD")
    print(f"🛒 Ticket Promedio: ${ticket_promedio:,.2f} USD")
    
    # 3. Cálculo de la Segmentación RFM
    # Fecha de referencia para simular el "hoy" de la extracción (un día después de la última venta)
    fecha_maxima = df_ventas['Fecha_Venta'].max() + pd.Timedelta(days=1)
    
    # Agrupar por Cliente
    rfm = df_ventas.groupby('Cliente_ID').agg({
        'Fecha_Venta': lambda x: (fecha_maxima - x.max()).days, # Recencia en días
        'Venta_ID': 'count',                                   # Frecuencia
        'Monto_Total_USD': 'sum'                               # Valor Monetario
    }).reset_index()
    
    rfm.columns = ['Cliente_ID', 'Recencia_Dias', 'Frecuencia_Transacciones', 'Monto_Total_USD']
    
    # Asignar puntuaciones del 1 al 4 (cuartiles)
    rfm['R_Score'] = pd.qcut(rfm['Recencia_Dias'], q=4, labels=[4, 3, 2, 1]) # Inverso: menos días = mejor nota
    rfm['F_Score'] = pd.qcut(rfm['Frecuencia_Transacciones'].rank(method='first'), q=4, labels=[1, 2, 3, 4])
    rfm['M_Score'] = pd.qcut(rfm['Monto_Total_USD'], q=4, labels=[1, 2, 3, 4])
    
    # Convertir a entero para sumar o concatenar
    rfm['RFM_Score_Total'] = rfm['R_Score'].astype(int) + rfm['F_Score'].astype(int) + rfm['M_Score'].astype(int)
    
    # Regla de Negocio para categorizar Segmentos RFM
    def definir_segmento(df):
        if df['RFM_Score_Total'] >= 10:
            return 'Campeones / VIP'
        elif df['RFM_Score_Total'] >= 8:
            return 'Clientes Leales'
        elif df['R_Score'] <= 2 and df['F_Score'] >= 3:
            return 'En Riesgo de Churn'
        elif df['RFM_Score_Total'] <= 5:
            return 'Clientes Dormidos / Perdidos'
        else:
            return 'Clientes Promedio'

    rfm['Segmento_RFM'] = rfm.apply(definir_segmento, axis=1)
    
    # Merge con la información del cliente
    df_clientes_rfm = pd.merge(df_clientes, rfm[['Cliente_ID', 'Recencia_Dias', 'Frecuencia_Transacciones', 'Segmento_RFM']], on='Cliente_ID', how='left')
    
    # 4. Consolidar Ventas + Logística
    df_ventas_full = pd.merge(df_ventas, df_logistica, on='Venta_ID', how='left')
    df_ventas_full['Dias_Demora'] = (df_ventas_full['Fecha_Entrega_Real'] - df_ventas_full['Fecha_Prometida']).dt.days
    df_ventas_full['Ganancia_USD'] = df_ventas_full['Monto_Total_USD'] - df_ventas_full['Costo_Total_USD']
    
    # Exportar archivos limpios procesados
    df_clientes_rfm.to_csv('retail-sales-rfm-analytics/dim_clientes_rfm.csv', index=False, encoding='utf-8-sig')
    df_ventas_full.to_csv('retail-sales-rfm-analytics/fact_ventas_logistica.csv', index=False, encoding='utf-8-sig')
    
    print("\n✅ Procesamiento RFM completado.")
    print("📁 Se han generado 'dim_clientes_rfm.csv' y 'fact_ventas_logistica.csv' listos para Power BI.")

if __name__ == "__main__":
    procesar_rfm_y_ventas()