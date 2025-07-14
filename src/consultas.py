import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def polizas():
    # Leer los datos
    df = pd.read_excel("./src/data/polizas.xlsx")

    # Procesamiento de datos
    ingreso_por_tipo_vivienda = df.groupby('Tipo de vivienda')['Ingreso'].mean().reset_index()
    ingreso_por_tipo_vivienda = ingreso_por_tipo_vivienda.round(2)
    json_data = ingreso_por_tipo_vivienda.to_json(orient='records', indent=4)
    ingreso_por_tipo_vivienda.rename(columns={'Ingreso': 'Ingreso Promedio'}, inplace=True)

    llm_prompt = f"""Realiza un análisis financiero avanzado de los tipos de vivienda asegurados con los siguientes datos:

ANÁLISIS REQUERIDO:
- Distribución de riesgo (proporción de cada tipo en el portfolio)
- Rentabilidad por tipología (ingreso promedio)
- Segmentación estratégica (oportunidades y alertas)
- Recomendaciones accionables de pricing y diversificación

FORMATO DE SALIDA:
- Resumen ejecutivo: 3-5 líneas
- Análisis detallado: por sección con visualizaciones sugeridas
- Tabla comparativa: KPIs clave

CONTEXTO:
Datos de un insurer europeo con exposición residencial en zonas urbanas/suburbanas

DATOS:
{json_data}"""

    # Ordenar los datos
    df_plot = ingreso_por_tipo_vivienda.sort_values('Ingreso Promedio', ascending=True)  # Orden ascendente para mejor visualización

    # Configuración del estilo
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(10, 6))

    # Crear el gráfico de barras horizontales
    bars = plt.barh(
        df_plot['Tipo de vivienda'],
        df_plot['Ingreso Promedio'],
        color=plt.cm.viridis(np.linspace(0.2, 0.8, len(df_plot))),
        edgecolor='gray',
        linewidth=0.5
    )

    # Añadir etiquetas de valor
    for bar in bars:
        width = bar.get_width()
        plt.text(
            width + max(df_plot['Ingreso Promedio']) * 0.01,  # Pequeño margen a la derecha
            bar.get_y() + bar.get_height()/2,
            f'{width:.2f}',
            va='center',
            ha='left',
            fontsize=9
        )

    # Personalizar el gráfico
    plt.title('Ingreso Promedio por Tipo de Vivienda', pad=20, fontsize=14, fontweight='bold')
    plt.xlabel('Ingreso Promedio (€)', labelpad=10)
    plt.ylabel('Tipo de Vivienda', labelpad=10)
    plt.xlim(0, max(df_plot['Ingreso Promedio']) * 1.15)  # Dejar espacio para las etiquetas
    plt.tight_layout()

    # Guardar el gráfico como PNG
    plt.savefig('./src/data/polizas_image.png', dpi=300, bbox_inches='tight')
    
    # Cerrar la figura para liberar memoria
    plt.close()

    return llm_prompt


def siniestros():
    # 1. Cargar datos
    df = pd.read_excel("./src/data/siniestros.xlsx")
    
    # 2. Calcular coste total por provincia (Top 10)
    top_provincias = (
        df.groupby('Provincia')['Coste Total']
        .sum()
        .nlargest(10)
        .reset_index()
        .sort_values('Coste Total', ascending=True)  # Orden ascendente para mejor visualización
    )
    
    # 3. Convertir a JSON
    json_data = top_provincias.to_json(orient='records', indent=4)

    llm_prompt = f"""🌍 Analiza la siniestralidad por provincia con los siguientes datos. Me interesa saber:

- 🔥 Dónde hay más costes totales y medios
- 🧭 Qué provincias sorprenden por su riesgo
- 💡 Recomendaciones básicas de pricing y exposición

Incluye:

- Un mini resumen (3 frases)
- 3 hallazgos clave con emojis
- Una tabla o lista que clasifique provincias según riesgo

Contexto: aseguradora con riesgos climáticos y daños por agua en España

DATOS:
    {json_data}"""

    # 4. Crear gráfico
    plt.figure(figsize=(10, 6))
    bars = plt.barh(
        top_provincias['Provincia'],
        top_provincias['Coste Total'],
        color='#1f77b4',  # Azul estándar
        alpha=0.7
    )
    
    # Añadir etiquetas de valor
    for bar in bars:
        width = bar.get_width()
        plt.text(
            width + (max(top_provincias['Coste Total']) * 0.01),
            bar.get_y() + bar.get_height()/2,
            f'€{width:,.0f}',
            va='center',
            ha='left',
            fontsize=9
        )
    
    # Personalización
    plt.title('Top 10 Provincias con Mayor Coste de Siniestros', pad=15, fontweight='bold')
    plt.xlabel('Coste Total (€)')
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    
    # 5. Guardar gráfico
    plt.savefig('./src/data/siniestros_image.png', dpi=120, bbox_inches='tight')
    plt.close()
    
    return llm_prompt