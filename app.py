import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
# Importar funciones de procesamiento
from src.processing import (
    preparar_dataframes,
    aplicar_transformaciones,
    procesar_picking,
    procesar_chequeo,
    unir_datos,
    create_grouped_report
    
)

# Importar funciones de visualización
from src.visualization import (
    create_nivel_carga_summary,
    create_descuento_summary,
    format_dataframe,
    sort_dataframe,
    highlight_cells,
    export_to_excel,
    get_formatted_date,
    reorder_columns
)
# Configuración de autenticación de Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
FOLDER_ID = '1rAACqx1K3-LnammeFuGPsbWV7Tqa7MbL'

# Configuración de la página
st.set_page_config(
    page_title="Reporte de Picking y Chequeo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Decorar la página con CSS personalizado
def aplicar_estilo():
    st.markdown("""
    <style>
    .main-header {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #1E88E5 !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        background-color: #f0f2f6;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E88E5 !important;
        color: white !important;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    </style>
    """, unsafe_allow_html=True)

# Función para mostrar página de inicio
def mostrar_inicio():
    st.title("Sistema de Reportes Logísticos")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## Bienvenido al Sistema de Reportes Logísticos
        
        Esta aplicación proporciona herramientas para el análisis y seguimiento de:
        
        * **Rendimiento de Picking y Chequeo**
        * **Seguimiento de Volumen Diario**
        * **Análisis de Descuentos**
        * **Niveles de Carga**
        
        Seleccione una opción del menú lateral para comenzar.
        """)
    
    with col2:
        st.markdown("### Fecha Actual")
        st.info(f"{datetime.now().strftime('%d/%m/%Y')}")
        
        st.markdown("### Accesos Rápidos")
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("📊 Rendimiento"):
                st.session_state.pagina = "Rendimiento de Producción"
                st.rerun()  # Usar st.rerun() en lugar de st.experimental_rerun()
        
        with col_b:
            if st.button("📈 Volumen"):
                st.session_state.pagina = "Seguimiento de Volumen"
                st.rerun()  # Usar st.rerun() en lugar de st.experimental_rerun()

# Función para mostrar configuración
def mostrar_configuracion():
    st.title("Configuración del Sistema")
    
    st.markdown("### Parámetros Generales")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input("Meta de Rendimiento", value=310, step=5)
        st.number_input("Meta de Error (%)", value=0.05, step=0.01, format="%.2f")
    
    with col2:
        st.selectbox("Unidad de Tiempo Predeterminada", ["Diaria", "Semanal", "Mensual"])
        st.checkbox("Actualizar datos automáticamente", value=True)
    
    st.markdown("### Configuración de Google Drive")
    st.text_input("ID de Carpeta en Drive", value=FOLDER_ID)
    
    if st.button("Guardar Configuración"):
        st.success("Configuración guardada correctamente")

# Modificación para recuperar nivel de carga LPN en app.py - Función run_visualization

# Modificación para recuperar nivel de carga LPN en app.py - Función run_visualization

def run_visualization():
    """Visualización principal con gráficos Gauge y métricas."""
    try:
        st.title('Rendimiento de Producción')
        df_picking, df_chequeo = preparar_dataframes()

        if df_picking is not None and df_chequeo is not None:
            df_picking_completo = df_picking.copy()

            # Procesar datos
            df_picking, df_chequeo = aplicar_transformaciones(df_picking, df_chequeo)
            df_valid = procesar_picking(df_picking)
            pallet_grouped = procesar_chequeo(df_chequeo)
            df_final = unir_datos(df_valid, pallet_grouped)
            df_final_report, min_rendimiento, mediana_rendimiento, max_rendimiento, df_total_general = create_grouped_report(df_final)

            # Obtener fecha y KPIs
            fecha_reporte = df_picking['Fecha Entrega'].iloc[0]
            rendimiento_actual = df_final['Rendimiento'].mean()
            error = df_total_general['% Error'].iloc[0] / 100  # Convertir a decimal
            total_cajas = df_final['CAJAS'].sum()

            # Definir metas
            meta_rendimiento = 310
            meta_error = 0.0005  # 0.05% en decimal

            # Configurar colores dinámicos
            color_rendimiento = "red" if rendimiento_actual < meta_rendimiento else "green"
            color_error = "green" if error < meta_error else "red"

            # Gráfico Gauge para Rendimiento
            # Gráfico Gauge para Rendimiento mejorado
            fig_rendimiento = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=rendimiento_actual,
                title={'text': "Rendimiento (cajas/hora)", 'font': {'size': 16, 'family': 'Arial Black'}},
                delta={'reference': meta_rendimiento, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}, 'font': {'size': 14}},
                number={'font': {'size': 30, 'family': 'Arial', 'color': color_rendimiento}, 'valueformat': ',d'},
                gauge={
                    'axis': {'range': [0, 400], 'tickwidth': 2, 'tickfont': {'size': 12}},
                    'bar': {'color': color_rendimiento, 'thickness': 0.6},
                    'steps': [
                        {'range': [0, meta_rendimiento*0.6], 'color': "rgba(255, 99, 99, 0.7)"},  # Rojo más bonito
                        {'range': [meta_rendimiento*0.6, meta_rendimiento*0.9], 'color': "rgba(255, 216, 102, 0.7)"},  # Amarillo
                        {'range': [meta_rendimiento*0.9, 400], 'color': "rgba(144, 238, 144, 0.7)"}  # Verde más bonito
                    ],
                    'threshold': {
                        'line': {'color': "blue", 'width': 5},
                        'thickness': 0.8,
                        'value': meta_rendimiento
                    }
                },
                domain={'x': [0, 1], 'y': [0, 1]}
            ))

            # Añadir anotación para marcar la meta más claramente
            fig_rendimiento.add_annotation(
                x=0.5, y=-0.2,
                text=f"META: {meta_rendimiento} CAJAS/HORA",
                showarrow=False,
                font=dict(size=14, color="blue", family="Arial Black"),
                bordercolor="blue",
                borderwidth=1,
                borderpad=4,
                bgcolor="#f0f2f6",
                opacity=0.9
            )

            # Ajustar layout para mejor visualización
            fig_rendimiento.update_layout(
                height=220,
                margin=dict(t=30, b=50, l=30, r=30),
            )

            # Gráfico Gauge para % de Error con mejor visualización
            fig_error = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=error,
                title={'text': "% de Error", 'font': {'size': 16, 'family': 'Arial Black'}},
                number={'valueformat': ".3%", 'font': {'size': 30, 'family': 'Arial', 'color': color_error}},
                delta={'reference': meta_error, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}, 'font': {'size': 14}},
                gauge={
                    'axis': {'range': [0, 0.00066666666], 'tickformat': ".2%", 'tickwidth': 2, 'tickfont': {'size': 12}},
                    'bar': {'color': color_error, 'thickness': 0.6},
                    'steps': [
                        {'range': [0, meta_error], 'color': "rgba(144, 238, 144, 0.7)"},  # Verde más bonito
                        {'range': [meta_error, 0.01], 'color': "rgba(255, 99, 99, 0.7)"}  # Rojo más bonito
                    ],
                    'threshold': {
                        'line': {'color': "blue", 'width': 5},
                        'thickness': 0.8,
                        'value': meta_error
                    }
                },
                domain={'x': [0, 1], 'y': [0, 1]}
            ))

            # Añadir anotación para marcar la meta más claramente
            fig_error.add_annotation(
                x=0.5, y=-0.2,
                text=f"META: {meta_error:.2%} (MENOR ES MEJOR)",
                showarrow=False,
                font=dict(size=14, color="blue", family="Arial Black"),
                bordercolor="blue",
                borderwidth=1,
                borderpad=4,
                bgcolor="#f0f2f6",
                opacity=0.9
            )

            # Ajustar tamaño y disposición de los indicadores gauge
            fig_rendimiento.update_layout(
                autosize=True,
                height=200,  # Altura fija más pequeña
                margin=dict(t=30, b=80, l=30, r=30),
            )

            fig_error.update_layout(
                autosize=True,
                height=200,  # Altura fija más pequeña
                margin=dict(t=30, b=80, l=30, r=30),
            )

            # Crear columnas con proporciones más adecuadas para los indicadores
            col1, col2, col3, col4 = st.columns([0.75, 1.5, 1.5, 0.75])
            
            col1.metric("Fecha de Reporte", fecha_reporte)
            with col2:
                st.plotly_chart(fig_rendimiento, use_container_width=True)
            with col3:
                st.plotly_chart(fig_error, use_container_width=True)
            col4.metric("Total Cajas", f"{total_cajas:,.0f}")
            # Línea separadora
            st.markdown("---")


            # Crear dos columnas
            col1, col2 = st.columns(2)

            # Definir constantes para cálculo de altura
            row_height = 35  # altura por fila en píxeles
            padding = 40     # margen adicional

            # 1. Reporte Detallado en la columna 1
            with col1:
                st.markdown("### Reporte Detallado")
                df_final_report = reorder_columns(df_final_report)
                df_final_report = format_dataframe(df_final_report)
                df_final_report = sort_dataframe(df_final_report)
               
                # AGREGAR ESTAS LÍNEAS AQUÍ
                # Forzar que Rendimiento sea entero antes de aplicar estilos
               # Forzar que Rendimiento sea entero antes de aplicar estilos
                if 'Rendimiento' in df_final_report.columns:
                    # Primero reemplazar NaN con 0, luego convertir a entero
                    df_final_report['Rendimiento'] = df_final_report['Rendimiento'].fillna(0).astype(float).round(0).astype(int)
                    styled_df = highlight_cells(df_final_report, min_rendimiento, mediana_rendimiento, max_rendimiento)
                    
                    # Calcular altura automáticamente basada en el número de filas
                    row_height = 35  # altura aproximada por fila en píxeles
                    padding = 40     # espacio para encabezados
                    table_height = min(500, len(df_final_report) * row_height + padding)
                    
                    st.dataframe(styled_df, use_container_width=True, height=table_height, hide_index=True)

            # 2. Nivel de Carga y Detalle de Descuentos en la columna 2
            with col2:
                # Nivel de Carga
                st.markdown("### Nivel de Carga")
                nivel_carga = create_nivel_carga_summary(df_picking_completo)
                if not nivel_carga.empty:
                    # Calcular altura para nivel de carga
                    nivel_rows = len(nivel_carga)
                    nivel_height = min(250, nivel_rows * row_height + padding)
                    st.dataframe(nivel_carga.style.format("{:,.0f}"), height=nivel_height)
                
                # Detalle de Descuentos
                st.markdown("### Detalle de Descuentos")
                descuento_summary = create_descuento_summary(df_chequeo)
                if not descuento_summary.empty:
                    # Crear un diccionario de formato que solo aplique a columnas numéricas
                    format_dict = {}
                    for col in descuento_summary.columns:
                        if pd.api.types.is_numeric_dtype(descuento_summary[col]):
                            format_dict[col] = "{:,.0f}"
                    
                    # Calcular altura para detalle de descuentos
                    descuento_rows = len(descuento_summary)
                    descuento_height = min(300, descuento_rows * row_height + padding)
                    
             
                else:
                    st.info("No hay datos de descuentos disponibles.")

            # 5. Botón de descarga
            st.markdown("---")
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                reporte_principal = df_final_report.copy()
                excel_file = export_to_excel(df_picking_completo, df_chequeo, reporte_principal, nivel_carga, descuento_summary)
                if excel_file:
                    filename = f"Picking {get_formatted_date(fecha_reporte)}.xlsx"
                    st.download_button(label="📥 Descargar Reporte Excel", data=excel_file, file_name=filename, mime="application/vnd.ms-excel")
    except Exception as e:
        st.error(f"Error en la visualización: {str(e)}")
        st.exception(e)

def run_app():
    aplicar_estilo()
    
    # Inicializar estado de sesión para la navegación
    if 'pagina' not in st.session_state:
        st.session_state.pagina = "Inicio"
    
    # Configuración de la barra lateral
    with st.sidebar:
        st.image("https://via.placeholder.com/150x80?text=LOGO", use_column_width=True)
        st.markdown("### Sistema de Reportes")
        
        # Menú principal
        opciones_menu = {
            "Inicio": "🏠 Inicio",
            "Rendimiento de Producción": "📦 Rendimiento de Producción",
            "Seguimiento de Volumen": "📈 Seguimiento de Volumen",
            "Configuración": "⚙️ Configuración"
        }
        
        for key, value in opciones_menu.items():
            if st.sidebar.button(value, key=key, 
                                type="primary" if st.session_state.pagina == key else "secondary"):
                st.session_state.pagina = key
                st.rerun()  # Cambiar st.experimental_rerun() por st.rerun()
        
       
    try:
        # Mostrar la página seleccionada
        if st.session_state.pagina == "Inicio":
            mostrar_inicio()
            
        elif st.session_state.pagina == "Rendimiento de Producción":
            run_visualization()  # Llamamos a nuestra propia implementación
            
        elif st.session_state.pagina == "Seguimiento de Volumen":
            # Aquí deberíamos implementar la función de seguimiento de volumen
            st.title("Seguimiento de Volumen Diario")
            st.info("Esta función está en desarrollo")
            
        elif st.session_state.pagina == "Configuración":
            mostrar_configuracion()
            
    except Exception as e:
        st.error(f"Error en la aplicación: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    run_app()