import pandas as pd
import streamlit as st
from .processing import (
    preparar_dataframes,
    aplicar_transformaciones,
    procesar_picking,
    procesar_chequeo,
    unir_datos,
    create_grouped_report,
    PK_IMAGEN,
    ORDER_EMPRESAS
)

def format_dataframe(df):
    """Da formato al DataFrame para la visualización."""
    # Asegurar nombres de columnas exactos
    column_mapping = {
        'Empresa': 'EMPRESA',
        'empresa': 'EMPRESA',
        'Rendimiento': 'RENDIMIENTO',
        'rendimiento': 'RENDIMIENTO',
        'Cjs c/ Error': 'CJS C/ ERROR',
        '% Error': '% ERROR',
        'Descripcion': 'Descripcion'  # Mantener original
    }
    
    # Renombrar columnas manteniendo el orden deseado
    for old_name, new_name in column_mapping.items():
        if old_name in df.columns:
            df = df.rename(columns={old_name: new_name})
    
    # Ordenar columnas según el orden específico requerido
    desired_columns = [
        'EMPRESA',
        'USUARIO',
        'Descripcion',
        'CAJAS',
        'RENDIMIENTO',
        '% ERROR',
        'CJS C/ ERROR'
    ]
    
    # Seleccionar solo las columnas que existen en el DataFrame
    columns_to_use = [col for col in desired_columns if col in df.columns]
    df = df[columns_to_use]
    
    return df

def sort_dataframe(df):
    """Ordena el DataFrame según los requisitos específicos."""
    df = df.copy()
    
    # Crear columna para ordenar empresas según ORDER_EMPRESAS
    df['empresa_order'] = pd.Categorical(
        df['EMPRESA'],
        categories=ORDER_EMPRESAS,
        ordered=True
    )
    
    # Crear columna para manejar el orden de los totales
    df['row_type'] = 'normal'
    df.loc[df['USUARIO'].str.startswith('Total '), 'row_type'] = 'subtotal'
    df.loc[df['EMPRESA'] == 'TOTAL GENERAL', 'row_type'] = 'total'
    
    # Ordenar el DataFrame
    df_sorted = df.sort_values(
        by=['empresa_order', 'row_type', 'CAJAS'],
        ascending=[True, True, False],
        key=lambda x: pd.Categorical(x, categories=['normal', 'subtotal', 'total'], ordered=True) if x.name == 'row_type' else x
    )
    
    # Eliminar columnas de ordenamiento
    df_sorted = df_sorted.drop(['empresa_order', 'row_type'], axis=1)
    
    return df_sorted

def highlight_cells(df, rendimiento_min, rendimiento_mediana, rendimiento_max):
    """Aplica estilos condicionales al dataframe."""
    def apply_styles(row):
        # Verificar si es una fila de total o un usuario de PK_IMAGEN
        is_total_row = "Total" in str(row['USUARIO']) or row['EMPRESA'] == "TOTAL GENERAL"
        is_pk_imagen = str(row['USUARIO']) in PK_IMAGEN
        
        if is_total_row:
            return ['background-color: rgb(166,166,166); color: black; font-weight: bold'] * len(df.columns)

        # Preparar estilos base para toda la fila
        row_styles = ['color: black'] * len(df.columns)
        
        # Aplicar estilo para usuarios PK_IMAGEN
        if is_pk_imagen:
            rendimiento_idx = df.columns.get_loc('RENDIMIENTO')
            row_styles[rendimiento_idx] = 'background-color: #CCCCCC; color: #777777; font-style: italic'
        elif pd.notna(row['RENDIMIENTO']):
            rendimiento_idx = df.columns.get_loc('RENDIMIENTO')
            if row['RENDIMIENTO'] <= rendimiento_min:
                row_styles[rendimiento_idx] = 'background-color: #FF9999; color: black'
            elif row['RENDIMIENTO'] <= rendimiento_mediana:
                row_styles[rendimiento_idx] = 'background-color: #FFFF99; color: black'
            else:
                row_styles[rendimiento_idx] = 'background-color: #90EE90; color: black'
        
        if pd.notna(row['% ERROR']):
            error_idx = df.columns.get_loc('% ERROR')
            if row['% ERROR'] > 0.05:
                row_styles[error_idx] = 'background-color: #FF9999; color: black'
            else:
                row_styles[error_idx] = 'background-color: #90EE90; color: black'
        
        return row_styles

    # Aplicar formato con nombres exactos de columnas
    return df.style.apply(apply_styles, axis=1).format({
        '% ERROR': "{:.2f} %",
        'RENDIMIENTO': "{:.2f}",
        'CJS C/ ERROR': "{:,.0f}",
        'CAJAS': "{:,.0f}"
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
            
            # Obtener la fecha del reporte
            fecha_reporte = df_final_report['Fecha Entrega'].iloc[0] if 'Fecha Entrega' in df_final_report.columns else None
            
            # Mostrar la fecha en un formato visualmente atractivo
            st.markdown("---")
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.metric("Fecha del Reporte", fecha_reporte)
            st.markdown("---")
            
            # Formatear y ordenar DataFrame
            df_final_report = format_dataframe(df_final_report)
            df_final_report = sort_dataframe(df_final_report)
            
            # Aplicar estilos
            styled_df = highlight_cells(df_final_report, 
                                      min_rendimiento, 
                                      mediana_rendimiento, 
                                      max_rendimiento)
            
            # Mostrar dataframe con estilos
            st.dataframe(styled_df, height=800)
            
            # Mostrar métricas de rendimiento
            st.markdown("### Métricas de Rendimiento")
            col1, col2, col3 = st.columns(3)
            col1.metric("Rendimiento mínimo", f"{min_rendimiento:.2f}" if not pd.isna(min_rendimiento) else "N/A")
            col2.metric("Rendimiento mediano", f"{mediana_rendimiento:.2f}" if not pd.isna(mediana_rendimiento) else "N/A")
            col3.metric("Rendimiento máximo", f"{max_rendimiento:.2f}" if not pd.isna(max_rendimiento) else "N/A")
        
    except Exception as e:
        st.error(f"Error en la visualización: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()





    ###########################################
    import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from .processing import (
    preparar_dataframes,
    aplicar_transformaciones,
    procesar_picking,
    procesar_chequeo,
    unir_datos,
    create_grouped_report,
    PK_IMAGEN,
    ORDER_EMPRESAS
)

def format_dataframe(df):
    """Da formato al DataFrame para la visualización."""
    # Asegurar nombres de columnas exactos
    column_mapping = {
        'Empresa': 'EMPRESA',
        'empresa': 'EMPRESA',
        'Rendimiento': 'RENDIMIENTO',
        'rendimiento': 'RENDIMIENTO',
        'Cjs c/ Error': 'CJS C/ ERROR',
        '% Error': '% ERROR',
        'Descripcion': 'Descripcion'
    }
    
    # Renombrar columnas manteniendo el orden deseado
    for old_name, new_name in column_mapping.items():
        if old_name in df.columns:
            df = df.rename(columns={old_name: new_name})
    
    # Ordenar columnas según el orden específico requerido
    desired_columns = [
        'EMPRESA',
        'USUARIO',
        'Descripcion',
        'CAJAS',
        'RENDIMIENTO',
        '% ERROR',
        'CJS C/ ERROR'
    ]
    
    # Seleccionar solo las columnas que existen en el DataFrame
    columns_to_use = [col for col in desired_columns if col in df.columns]
    df = df[columns_to_use]
    
    return df

def sort_dataframe(df):
    """Ordena el DataFrame según los requisitos específicos."""
    df = df.copy()
    
    # Crear columna para ordenar empresas según ORDER_EMPRESAS
    df['empresa_order'] = pd.Categorical(
        df['EMPRESA'],
        categories=ORDER_EMPRESAS,
        ordered=True
    )
    
    # Crear columna para manejar el orden de los totales
    df['row_type'] = 'normal'
    df.loc[df['USUARIO'].str.startswith('Total '), 'row_type'] = 'subtotal'
    df.loc[df['EMPRESA'] == 'TOTAL GENERAL', 'row_type'] = 'total'
    
    # Ordenar el DataFrame
    df_sorted = df.sort_values(
        by=['empresa_order', 'row_type', 'CAJAS'],
        ascending=[True, True, False],
        key=lambda x: pd.Categorical(x, categories=['normal', 'subtotal', 'total'], ordered=True) if x.name == 'row_type' else x
    )
    
    # Eliminar columnas de ordenamiento
    df_sorted = df_sorted.drop(['empresa_order', 'row_type'], axis=1)
    
    return df_sorted

def highlight_cells(df, rendimiento_min, rendimiento_mediana, rendimiento_max):
    """Aplica estilos condicionales al dataframe."""
    def apply_styles(row):
        is_total_row = "Total" in str(row['USUARIO']) or row['EMPRESA'] == "TOTAL GENERAL"
        is_pk_imagen = str(row['USUARIO']) in PK_IMAGEN
        
        if is_total_row:
            return ['background-color: rgb(166,166,166); color: black; font-weight: bold'] * len(df.columns)

        row_styles = ['color: black'] * len(df.columns)
        
        if is_pk_imagen:
            rendimiento_idx = df.columns.get_loc('RENDIMIENTO')
            row_styles[rendimiento_idx] = 'background-color: #CCCCCC; color: #777777; font-style: italic'
        elif pd.notna(row['RENDIMIENTO']):
            rendimiento_idx = df.columns.get_loc('RENDIMIENTO')
            if row['RENDIMIENTO'] <= rendimiento_min:
                row_styles[rendimiento_idx] = 'background-color: #FF9999; color: black'
            elif row['RENDIMIENTO'] <= rendimiento_mediana:
                row_styles[rendimiento_idx] = 'background-color: #FFFF99; color: black'
            else:
                row_styles[rendimiento_idx] = 'background-color: #90EE90; color: black'
        
        if pd.notna(row['% ERROR']):
            error_idx = df.columns.get_loc('% ERROR')
            if row['% ERROR'] > 0.05:
                row_styles[error_idx] = 'background-color: #FF9999; color: black'
            else:
                row_styles[error_idx] = 'background-color: #90EE90; color: black'
        
        return row_styles

    return df.style.apply(apply_styles, axis=1).format({
        '% ERROR': "{:.2f} %",
        'RENDIMIENTO': "{:.2f}",
        'CJS C/ ERROR': "{:,.0f}",
        'CAJAS': "{:,.0f}"
    }, na_rep="N/A")

def create_nivel_carga_summary(df_picking):
    """Crea el resumen de nivel de carga."""
    pivot_nivel_carga = pd.pivot_table(
        df_picking,
        values='Cajas',
        index='Nivel de carga',
        columns='Fecha Entrega',
        aggfunc='sum',
        fill_value=0
    )
    
    pivot_nivel_carga.loc['Total general'] = pivot_nivel_carga.sum()
    
    return pivot_nivel_carga

def create_descuento_summary(df_chequeo):
    """Crea el resumen de descuentos."""
    df_malo = df_chequeo[df_chequeo['consistencia'] == 'MALO']
    
    pivot_descuento = pd.pivot_table(
        df_malo,
        values='Suma de descuento',
        index=['Chequeador', 'id usuario', 'Numero de carga'],
        columns='consistencia',
        aggfunc='sum',
        fill_value=0
    )
    
    return pivot_descuento
def create_nivel_carga_summary(df_picking):
    """Crea el resumen de nivel de carga."""
    try:
        # Primero, verificar qué columnas están disponibles
        print("Columnas disponibles en df_picking:", df_picking.columns.tolist())
        
        # Crear tabla dinámica con las columnas correctas
        pivot_nivel_carga = pd.pivot_table(
            df_picking,
            values='CAJAS',  # Cambiado de 'Cajas' a 'CAJAS'
            index='EMPRESA',  # Usar EMPRESA como índice si no existe 'Nivel de carga'
            columns='Fecha Entrega',
            aggfunc='sum',
            fill_value=0
        )
        
        # Agregar total general
        pivot_nivel_carga.loc['Total general'] = pivot_nivel_carga.sum()
        
        return pivot_nivel_carga
    except Exception as e:
        st.error(f"Error en create_nivel_carga_summary: {str(e)}")
        print(f"Error detallado: {str(e)}")
        return pd.DataFrame()  # Retornar DataFrame vacío en caso de error

def create_descuento_summary(df_chequeo):
    """Crea el resumen de descuentos."""
    try:
        # Verificar columnas disponibles
        print("Columnas disponibles en df_chequeo:", df_chequeo.columns.tolist())
        
        # Verificar si existe la columna 'consistencia'
        if 'consistencia' not in df_chequeo.columns:
            # Crear la columna consistencia basada en errores
            df_chequeo['consistencia'] = 'BUENO'
            df_chequeo.loc[df_chequeo['CJS C/ ERROR'] > 0, 'consistencia'] = 'MALO'
        
        # Filtrar registros con consistencia 'MALO'
        df_malo = df_chequeo[df_chequeo['consistencia'] == 'MALO'].copy()
        
        # Crear tabla dinámica
        pivot_descuento = pd.pivot_table(
            df_malo,
            values='CJS C/ ERROR',  # Cambiado de 'Suma de descuento' a 'CJS C/ ERROR'
            index=['USUARIO'],  # Ajustar según las columnas disponibles
            columns='consistencia',
            aggfunc='sum',
            fill_value=0
        )
        
        return pivot_descuento
    except Exception as e:
        st.error(f"Error en create_descuento_summary: {str(e)}")
        print(f"Error detallado: {str(e)}")
        return pd.DataFrame()  # Retornar DataFrame vacío en caso de error

def main():
    """Función principal de visualización."""
    try:
        st.title('Rendimiento de Producción')
        
        # Cargar y procesar datos
        df_picking, df_chequeo = preparar_dataframes()
        
        if df_picking is not None and df_chequeo is not None:
            # Aplicar transformaciones primero
            df_picking, df_chequeo = aplicar_transformaciones(df_picking, df_chequeo)
            df_valid = procesar_picking(df_picking)
            pallet_grouped = procesar_chequeo(df_chequeo)
            df_final = unir_datos(df_valid, pallet_grouped)
            
            # Crear tablas dinámicas
            nivel_carga = create_nivel_carga_summary(df_picking)
            descuento_summary = create_descuento_summary(df_final)  # Usar df_final en lugar de df_chequeo
            
            # Mostrar resúmenes en la parte superior
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Nivel de Carga")
                if not nivel_carga.empty:
                    st.dataframe(nivel_carga.style.format("{:,.0f}"))
                else:
                    st.warning("No hay datos disponibles para el nivel de carga")
            
            with col2:
                st.markdown("### Suma de Descuento")
                if not descuento_summary.empty:
                    st.dataframe(descuento_summary.style.format("{:,.0f}"))
                else:
                    st.warning("No hay datos disponibles para el resumen de descuentos")
            
            # Generar reporte principal
            df_final_report, min_rendimiento, mediana_rendimiento, max_rendimiento = create_grouped_report(df_final)
            
            # Formatear y ordenar DataFrame
            df_final_report = format_dataframe(df_final_report)
            df_final_report = sort_dataframe(df_final_report)
            
            # Aplicar estilos
            styled_df = highlight_cells(df_final_report, 
                                      min_rendimiento, 
                                      mediana_rendimiento, 
                                      max_rendimiento)
            
            # Mostrar métricas
            col1, col2, col3 = st.columns(3)
            col1.metric("Rendimiento mínimo", f"{min_rendimiento:.2f}" if not pd.isna(min_rendimiento) else "N/A")
            col2.metric("Rendimiento mediano", f"{mediana_rendimiento:.2f}" if not pd.isna(mediana_rendimiento) else "N/A")
            col3.metric("Rendimiento máximo", f"{max_rendimiento:.2f}" if not pd.isna(max_rendimiento) else "N/A")
            
            # Mostrar tabla principal
            st.markdown("### Reporte Detallado")
            st.dataframe(styled_df, height=800)
        
    except Exception as e:
        st.error(f"Error en la visualización: {str(e)}")
        st.exception(e)
def main():
    """Función principal de visualización."""
    try:
        st.title('Rendimiento de Producción')
        
        # Cargar y procesar datos
        df_picking, df_chequeo = preparar_dataframes()
        
        if df_picking is not None and df_chequeo is not None:
            # Crear tablas dinámicas
            nivel_carga = create_nivel_carga_summary(df_picking)
            descuento_summary = create_descuento_summary(df_chequeo)
            
            # Mostrar resúmenes en la parte superior
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Nivel de Carga")
                st.dataframe(nivel_carga.style.format("{:,.0f}"))
            
            with col2:
                st.markdown("### Suma de Descuento")
                st.dataframe(descuento_summary.style.format("{:,.0f}"))
            
            # Aplicar transformaciones para la tabla principal
            df_picking, df_chequeo = aplicar_transformaciones(df_picking, df_chequeo)
            df_valid = procesar_picking(df_picking)
            pallet_grouped = procesar_chequeo(df_chequeo)
            df_final = unir_datos(df_valid, pallet_grouped)
            
            # Generar reporte principal
            df_final_report, min_rendimiento, mediana_rendimiento, max_rendimiento = create_grouped_report(df_final)
            
            # Formatear y ordenar DataFrame
            df_final_report = format_dataframe(df_final_report)
            df_final_report = sort_dataframe(df_final_report)
            
            # Aplicar estilos
            styled_df = highlight_cells(df_final_report, 
                                      min_rendimiento, 
                                      mediana_rendimiento, 
                                      max_rendimiento)
            
            # Mostrar métricas
            col1, col2, col3 = st.columns(3)
            col1.metric("Rendimiento mínimo", f"{min_rendimiento:.2f}" if not pd.isna(min_rendimiento) else "N/A")
            col2.metric("Rendimiento mediano", f"{mediana_rendimiento:.2f}" if not pd.isna(mediana_rendimiento) else "N/A")
            col3.metric("Rendimiento máximo", f"{max_rendimiento:.2f}" if not pd.isna(max_rendimiento) else "N/A")
            
            # Mostrar tabla principal
            st.markdown("### Reporte Detallado")
            st.dataframe(styled_df, height=800)
        
    except Exception as e:
        st.error(f"Error en la visualización: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()