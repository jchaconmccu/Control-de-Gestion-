import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuración de la página
st.set_page_config(
    page_title="Balance Scorecard 2024",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("Balance Scorecard 2024")
st.markdown("Análisis de resultados por trimestre y categoría")

# Datos para el BSC
# Resultados trimestrales por categoría (vs PPTO)
resultados_por_categoria = pd.DataFrame({
    'Trimestre': ['Q1', 'Q2', 'Q3', 'Q4'],
    'Rentabilidad': [109.0, 102.3, 102.7, 100.5],
    'Excelencia Op.': [94.2, 118.1, 110.1, 113.1],
    'Sustentabilidad': [101.8, 110.0, 109.6, 118.8],
    'Total': [102.7, 107.8, 106.3, 108.2]
})

# Indicadores destacados
top_indicadores = pd.DataFrame({
    'Indicador': ['Auditoria TPM', 'ANS TCCU', 'Conteo Almacenes', 'Tiempo Estadía', 'Clima'],
    'Valor': [120.0, 120.0, 118.0, 110.0, 107.0],
    'Categoría': ['Sustentabilidad', 'Sustentabilidad', 'Rentabilidad', 'Excelencia Op.', 'Sustentabilidad']
})

# Áreas de oportunidad
areas_oportunidad = pd.DataFrame({
    'Indicador': ['Ajustes Inventario (Q4)', 'Rechazo (Q3)', 'Costo Unitario (Q2)'],
    'Valor': [80.0, 80.0, 90.6],
    'Categoría': ['Rentabilidad', 'Excelencia Op.', 'Rentabilidad']
})

# Distribución de categorías con pesos
distribucion_categorias = pd.DataFrame({
    'Categoría': ['Rentabilidad', 'Excelencia Op.', 'Sustentabilidad'],
    'Peso': [50, 25, 25],
    'Resultado': [103.6, 108.9, 110.1]
})

# Crear columnas para las visualizaciones
col1, col2 = st.columns([1, 2])

# Diapositiva 1: Visión General del BSC
with col1:
    st.subheader("Distribución por Categoría")
    
    # Gráfico de pastel para distribución de categorías
    fig_distribucion = px.pie(
        distribucion_categorias, 
        values='Peso', 
        names='Categoría',
        color='Categoría',
        color_discrete_map={
            'Rentabilidad': '#0088FE',
            'Excelencia Op.': '#00C49F', 
            'Sustentabilidad': '#FFBB28'
        },
        hole=0.3
    )
    
    fig_distribucion.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),
        height=300
    )
    
    st.plotly_chart(fig_distribucion, use_container_width=True)
    
    # Tabla de resultados por categoría
    st.dataframe(
        distribucion_categorias[['Categoría', 'Resultado']].rename(
            columns={'Resultado': 'Resultado vs PPTO (%)'}
        ).set_index('Categoría'),
        use_container_width=True
    )

with col2:
    st.subheader("Resultados Trimestrales vs PPTO (%)")
    
    # Gráfico de líneas para resultados trimestrales
    fig_resultados = px.line(
        resultados_por_categoria, 
        x='Trimestre', 
        y=['Total', 'Rentabilidad', 'Excelencia Op.', 'Sustentabilidad'],
        markers=True,
        line_shape='linear',
        color_discrete_map={
            'Total': '#000000',
            'Rentabilidad': '#0088FE',
            'Excelencia Op.': '#00C49F', 
            'Sustentabilidad': '#FFBB28'
        }
    )
    
    # Añadir una línea horizontal en 100%
    fig_resultados.add_shape(
        type="line",
        x0=-0.5,
        y0=100,
        x1=3.5,
        y1=100,
        line=dict(color="red", width=1, dash="dash"),
    )
    
    fig_resultados.add_annotation(
        x=3.5,
        y=100,
        text="Meta",
        showarrow=False,
        font=dict(color="red"),
        xanchor="left"
    )
    
    # Personalizar el gráfico
    fig_resultados.update_layout(
        xaxis_title="",
        yaxis_title="% vs PPTO",
        legend_title="",
        height=350,
        yaxis=dict(range=[90, 120]),
        hovermode="x unified",
        margin=dict(t=0, b=0, l=0, r=0)
    )
    
    st.plotly_chart(fig_resultados, use_container_width=True)

# Información de resumen
st.info("""
### Resultados Clave:
- **Desempeño global**: 106.3% vs Presupuesto, 99.0% vs Año Anterior
- **Categoría destacada**: Sustentabilidad (110.1%)
- **Tendencia**: Mejora sostenida (+5.5 puntos porcentuales de Q1 a Q4)
""")

# Separador
st.markdown("---")

# Diapositiva 2: Análisis de Indicadores
st.header("Análisis de Indicadores")

col3, col4 = st.columns(2)

with col3:
    st.subheader("Top 5 Indicadores (% vs PPTO)")
    
    # Ordenar indicadores por valor descendente
    top_indicadores_sorted = top_indicadores.sort_values('Valor', ascending=True)
    
    # Gráfico de barras horizontales para top indicadores
    fig_top = px.bar(
        top_indicadores_sorted, 
        x='Valor', 
        y='Indicador',
        color='Categoría',
        color_discrete_map={
            'Rentabilidad': '#0088FE',
            'Excelencia Op.': '#00C49F', 
            'Sustentabilidad': '#FFBB28'
        },
        text='Valor',
        orientation='h'
    )
    
    # Añadir una línea vertical en 100%
    fig_top.add_shape(
        type="line",
        x0=100,
        y0=-0.5,
        x1=100,
        y1=4.5,
        line=dict(color="red", width=1, dash="dash"),
    )
    
    # Personalizar el gráfico
    fig_top.update_layout(
        xaxis_title="% vs PPTO",
        yaxis_title="",
        xaxis=dict(range=[90, 125]),
        margin=dict(t=0, b=0, l=0, r=20),
        height=300
    )
    
    fig_top.update_traces(
        texttemplate='%{text:.1f}%', 
        textposition='outside'
    )
    
    st.plotly_chart(fig_top, use_container_width=True)

with col4:
    st.subheader("Áreas de Oportunidad (% vs PPTO)")
    
    # Ordenar áreas de oportunidad por valor ascendente
    areas_oportunidad_sorted = areas_oportunidad.sort_values('Valor', ascending=False)
    
    # Gráfico de barras horizontales para áreas de oportunidad
    fig_areas = px.bar(
        areas_oportunidad_sorted, 
        x='Valor', 
        y='Indicador',
        color='Categoría',
        color_discrete_map={
            'Rentabilidad': '#0088FE',
            'Excelencia Op.': '#00C49F'
        },
        text='Valor',
        orientation='h'
    )
    
    # Añadir una línea vertical en 100%
    fig_areas.add_shape(
        type="line",
        x0=100,
        y0=-0.5,
        x1=100,
        y1=2.5,
        line=dict(color="red", width=1, dash="dash"),
    )
    
    # Personalizar el gráfico
    fig_areas.update_layout(
        xaxis_title="% vs PPTO",
        yaxis_title="",
        xaxis=dict(range=[70, 105]),
        margin=dict(t=0, b=0, l=0, r=20),
        height=300
    )
    
    fig_areas.update_traces(
        texttemplate='%{text:.1f}%', 
        textposition='outside'
    )
    
    st.plotly_chart(fig_areas, use_container_width=True)

# Análisis por categoría
st.subheader("Resumen por Categoría:")

col5, col6, col7 = st.columns(3)

with col5:
    st.markdown("""
    ### Rentabilidad (103.6%)
    - **Fortalezas**: Conteo Almacenes, Vencimientos
    - **Áreas de mejora**: Costo Unitario, Ajustes Inventario
    - **Tendencia**: Estable con ligera baja en Q4
    """)

with col6:
    st.markdown("""
    ### Excelencia Op. (108.9%)
    - **Fortalezas**: Tiempo Estadía, Faltante
    - **Áreas de mejora**: Rechazo (Q3)
    - **Tendencia**: Volátil con recuperación
    """)

with col7:
    st.markdown("""
    ### Sustentabilidad (110.1%)
    - **Fortalezas**: Auditoria TPM, ANS TCCU, Clima
    - **Áreas de mejora**: Seguridad (variable)
    - **Tendencia**: Positiva constante
    """)

# Plan de acción
st.warning("""
### Plan de Acción 2025:
1. **Rentabilidad**: Implementar programa de eficiencia en costos unitarios y mejorar control de inventarios
2. **Excelencia Operacional**: Analizar causas de rechazo y mantener mejoras en tiempo de estadía
3. **Sustentabilidad**: Expandir prácticas exitosas de TPM a otras áreas
""")