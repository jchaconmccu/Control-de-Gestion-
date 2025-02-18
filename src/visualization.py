import pandas as pd
import streamlit as st
from .processing import (
    preparar_dataframes,
    aplicar_transformaciones,
    procesar_picking,
    procesar_chequeo,
    unir_datos,
    create_grouped_report,
    PK_IMAGEN
)

def highlight_cells(df, rendimiento_min, rendimiento_mediana, rendimiento_max):
    """Aplica estilos condicionales al dataframe."""
    def apply_styles(row):
        # Verificar si es una fila de total o un usuario de PK_IMAGEN
        is_total_row = "Total" in str(row['USUARIO']) or row['Empresa'] == "TOTAL GENERAL"
        is_pk_imagen = str(row['USUARIO']) in PK_IMAGEN
        
        if is_total_row:
            return ['background-color: rgb(166,166,166); color: black; font-weight: bold'] * len(df.columns)

        # Preparar estilos base para toda la fila
        row_styles = ['color: black'] * len(df.columns)
        
        # Aplicar estilo para usuarios PK_IMAGEN
        if is_pk_imagen:
            rendimiento_idx = df.columns.get_loc('Rendimiento')
            row_styles[rendimiento_idx] = 'background-color: #CCCCCC; color: #777777; font-style: italic'
        elif pd.notna(row['Rendimiento']):
            rendimiento_idx = df.columns.get_loc('Rendimiento')
            if row['Rendimiento'] <= rendimiento_min:
                row_styles[rendimiento_idx] = 'background-color: #FF9999; color: black'
            elif row['Rendimiento'] <= rendimiento_mediana:
                row_styles[rendimiento_idx] = 'background-color: #FFFF99; color: black'
            else:
                row_styles[rendimiento_idx] = 'background-color: #90EE90; color: black'
        
        if pd.notna(row['% Error']):
            error_idx = df.columns.get_loc('% Error')
            if row['% Error'] > 0.05:
                row_styles[error_idx] = 'background-color: #FF9999; color: black'
            else:
                row_styles[error_idx] = 'background-color: #90EE90; color: black'
        
        return row_styles

    return df.style.apply(apply_styles, axis=1).format({
        '% Error': "{:.2f} %",
        'Rendimiento': "{:.2f}",
        'Cjs c/ Error': "{:,.0f}"
    }, na_rep="N/A")

def main():
    """Función principal de visualización."""
    try:
        st.title('Rendimiento de Producción')
        
        # Cargar y procesar datos
        df_picking, df_chequeo = preparar_dataframes()
        
        if df_picking is not None and df_chequeo is not None:
            # Aplicar transformaciones
            df_picking, df_chequeo = aplicar_transformaciones(df_picking, df_chequeo)
            
            # Procesar picking y chequeo
            df_valid = procesar_picking(df_picking)
            pallet_grouped = procesar_chequeo(df_chequeo)
            
            # Unir datos
            df_final = unir_datos(df_valid, pallet_grouped)
            
            # Generar reporte
            df_final_report, min_rendimiento, mediana_rendimiento, max_rendimiento = create_grouped_report(df_final)
            
            # Aplicar estilos
            styled_df = highlight_cells(df_final_report, 
                                      min_rendimiento, 
                                      mediana_rendimiento, 
                                      max_rendimiento)
            
            # Mostrar dataframe con estilos
            st.dataframe(styled_df, height=800)
            
            # Mostrar métricas
            col1, col2, col3 = st.columns(3)
            col1.metric("Rendimiento mínimo", f"{min_rendimiento:.2f}" if not pd.isna(min_rendimiento) else "N/A")
            col2.metric("Rendimiento mediano", f"{mediana_rendimiento:.2f}" if not pd.isna(mediana_rendimiento) else "N/A")
            col3.metric("Rendimiento máximo", f"{max_rendimiento:.2f}" if not pd.isna(max_rendimiento) else "N/A")
        
    except Exception as e:
        st.error(f"Error en la visualización: {str(e)}")
        st.exception(e)