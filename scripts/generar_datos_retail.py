import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker('es_CO')
np.random.seed(42)
random.seed(42)

def generar_datos_retail(num_clientes=300, num_ventas=2500):
    # 1. TABLA DE CLIENTES
    ciudades = ['Lima', 'Arequipa', 'Trujillo', 'Chiclayo', 'Piura', 'Cuzco']
    segmentos = ['Corporativo', 'Consumo Final', 'PYME']
    
    clientes = []
    for i in range(1, num_clientes + 1):
        cliente_id = f"CLI-{1000 + i}"
        nombre = fake.name()
        ciudad = random.choice(ciudades)
        segmento = random.choice(segmentos)
        fecha_registro = fake.date_between(start_date='-2y', end_date='-1y')
        clientes.append({
            'Cliente_ID': cliente_id,
            'Nombre': nombre,
            'Ciudad': ciudad,
            'Segmento_Cliente': segmento,
            'Fecha_Registro': fecha_registro
        })
    
    df_clientes = pd.DataFrame(clientes)
    
    # 2. TABLA DE VENTAS
    categorias_prod = ['Laptops & Equipos', 'Accesorios TI', 'Licencias Software', 'Redes & Conectividad', 'Monitores']
    canales = ['Web E-Commerce', 'Venta Directa B2B', 'Retail Presencial']
    
    ventas = []
    fecha_inicio = datetime(2025, 1, 1)
    
    for i in range(1, num_ventas + 1):
        venta_id = f"VEN-{10000 + i}"
        cliente = random.choice(clientes)['Cliente_ID']
        # Distribuir ventas a lo largo del tiempo hasta mediados de 2026
        dias_random = random.randint(0, 560)
        fecha_venta = fecha_inicio + timedelta(days=dias_random)
        
        categoria = random.choice(categorias_prod)
        canal = random.choice(canales)
        
        # Precios y costos según categoría
        if categoria == 'Laptops & Equipos':
            monto = round(random.uniform(800, 2500), 2)
            costo = round(monto * random.uniform(0.70, 0.85), 2)
        elif categoria == 'Licencias Software':
            monto = round(random.uniform(100, 600), 2)
            costo = round(monto * random.uniform(0.20, 0.40), 2)
        else:
            monto = round(random.uniform(30, 400), 2)
            costo = round(monto * random.uniform(0.50, 0.70), 2)
            
        ventas.append({
            'Venta_ID': venta_id,
            'Cliente_ID': cliente,
            'Fecha_Venta': fecha_venta.strftime("%Y-%m-%d"),
            'Categoria': categoria,
            'Canal_Venta': canal,
            'Monto_Total_USD': monto,
            'Costo_Total_USD': costo
        })
        
    df_ventas = pd.DataFrame(ventas)
    
    # 3. TABLA DE LOGÍSTICA
    logistica = []
    for index, row in df_ventas.iterrows():
        fecha_v = datetime.strptime(row['Fecha_Venta'], "%Y-%m-%d")
        dias_prometidos = random.randint(2, 5)
        fecha_prometida = fecha_v + timedelta(days=dias_prometidos)
        
        # Simulamos un 15% de envíos demorados
        dias_reales = dias_prometidos + (random.randint(1, 4) if random.random() < 0.15 else random.randint(-1, 0))
        fecha_entrega = fecha_v + timedelta(days=max(1, dias_reales))
        
        estado = 'Entregado a Tiempo' if fecha_entrega <= fecha_prometida else 'Atrasado'
        
        logistica.append({
            'Venta_ID': row['Venta_ID'],
            'Fecha_Prometida': fecha_prometida.strftime("%Y-%m-%d"),
            'Fecha_Entrega_Real': fecha_entrega.strftime("%Y-%m-%d"),
            'Estado_Envio': estado
        })
        
    df_logistica = pd.DataFrame(logistica)
    
    # Guardar CSVs
    df_clientes.to_csv('retail-sales-rfm-analytics/clientes_raw.csv', index=False, encoding='utf-8-sig')
    df_ventas.to_csv('retail-sales-rfm-analytics/ventas_raw.csv', index=False, encoding='utf-8-sig')
    df_logistica.to_csv('retail-sales-rfm-analytics/logistica_raw.csv', index=False, encoding='utf-8-sig')
    
    print("✅ Datasets comerciales creados exitosamente: 'clientes_raw.csv', 'ventas_raw.csv', 'logistica_raw.csv'")

if __name__ == "__main__":
    generar_datos_retail()