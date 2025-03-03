import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime
import io
import plotly.graph_objects as go

def crear_indicadores_visuales(df_final):
    """Crea indicadores visuales atractivos para el dashboard."""
    try:
        import plotly.graph_objects as go
        import numpy as np
        
        # Extraer valores para los indicadores
        # Excluir filas de totales para calcular el rendimiento promedio
        df_sin_totales = df_final[~df_final['USUARIO'].astype(str).str.contains('Total|TOTAL')]
        
        # Rendimiento promedio (excluyendo valores nulos)
        rendimiento_promedio = df_sin_totales['Rendimiento'].mean() if 'Rendimiento' in df_sin_totales.columns else 0
        if pd.isna(rendimiento_promedio):
            rendimiento_promedio = 0
        
        # Error promedio
        error_promedio = df_sin_totales['% Error'].mean() if '% Error' in df_sin_totales.columns else 0
        if pd.isna(error_promedio):
            error_promedio = 0
        
        # Total de cajas
        total_cajas = df_final['CAJAS'].sum() if 'CAJAS' in df_final.columns else 0
        
        # Establecer metas
        meta_rendimiento = 300  # Ajustar según tus necesidades
        meta_error = 0.05       # 5% como meta de error máximo
        
        # Crear medidor de velocidad para Rendimiento
        fig_rendimiento = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=rendimiento_promedio,
            delta={'reference': meta_rendimiento, 'increasing': {'color': 'green'}, 'decreasing': {'color': 'red'}},
            gauge={
                'axis': {'range': [0, max(meta_rendimiento * 1.5, rendimiento_promedio * 1.2)], 'tickwidth': 1},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, meta_rendimiento * 0.6], 'color': 'red'},
                    {'range': [meta_rendimiento * 0.6, meta_rendimiento * 0.9], 'color': 'yellow'},
                    {'range': [meta_rendimiento * 0.9, meta_rendimiento * 1.5], 'color': 'green'}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': meta_rendimiento
                }
            },
            title={
                'text': "Rendimiento Promedio",
                'font': {'size': 20}
            },
            number={'suffix': " cajas/h", 'font': {'size': 26}}
        ))

        fig_rendimiento.update_layout(
            height=250,
            margin=dict(l=30, r=30, t=50, b=30),
        )
        
        # Crear medidor para % de Error
        fig_error = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=error_promedio,
            delta={'reference': meta_error, 'increasing': {'color': 'red'}, 'decreasing': {'color': 'green'}},
            gauge={
                'axis': {'range': [0, 0.2], 'tickwidth': 1, 'tickformat': '.1%'},
                'bar': {'color': "darkred"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 0.02], 'color': 'green'},
                    {'range': [0.02, 0.05], 'color': 'yellow'},
                    {'range': [0.05, 0.2], 'color': 'red'}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': meta_error
                }
            },
            title={
                'text': "% Error Promedio",
                'font': {'size': 20}
            },
            number={'valueformat': '.2%', 'font': {'size': 26}}
        ))

        fig_error.update_layout(
            height=250,
            margin=dict(l=30, r=30, t=50, b=30),
        )
        
        # Crear indicador numérico para Total de Cajas
        fig_cajas = go.Figure(go.Indicator(
            mode="number+delta",
            value=total_cajas,
            number={'valueformat': ',d', 'font': {'size': 40}},
            title={'text': "Total Cajas", 'font': {'size': 20}},
            domain={'x': [0, 1], 'y': [0, 1]}
        ))

        fig_cajas.update_layout(
            height=200,
            margin=dict(l=30, r=30, t=30, b=30),
        )
        
        # Calcular porcentaje cumplimiento de meta
        if meta_rendimiento > 0:
            cumplimiento = (rendimiento_promedio / meta_rendimiento) * 100
        else:
            cumplimiento = 0
            
        if cumplimiento > 100:
            color_cumplimiento = 'green'
        elif cumplimiento > 80:
            color_cumplimiento = 'orange'
        else:
            color_cumplimiento = 'red'
            
        # Crear barra de progreso para cumplimiento de meta
        fig_cumplimiento = go.Figure(go.Indicator(
            mode="gauge+number",
            value=cumplimiento,
            gauge={
                'axis': {'range': [0, 120], 'tickwidth': 1},
                'bar': {'color': color_cumplimiento},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
            },
            title={
                'text': "Cumplimiento Meta",
                'font': {'size': 20}
            },
            number={'suffix': "%", 'font': {'size': 30}}
        ))

        fig_cumplimiento.update_layout(
            height=200,
            margin=dict(l=30, r=30, t=50, b=30),
        )
        
        return fig_rendimiento, fig_error, fig_cajas, fig_cumplimiento
        
    except Exception as e:
        st.error(f"Error en crear_indicadores_visuales: {str(e)}")
        print(f"Error detallado: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None, None, None
def reorder_columns(df):
    """Reordena las columnas del dataframe según el orden deseado."""
    try:
        # Orden deseado de columnas
        desired_order = ['Empresa', 'USUARIO', 'Descripcion', 'CAJAS', 'Rendimiento', '% Error', 'Cjs c/ Error']
        
        # Verificar qué columnas del orden deseado existen en el dataframe
        existing_columns = [col for col in desired_order if col in df.columns]
        
       
        
        # Crear nuevo orden: primero las columnas en el orden deseado, luego las demás
        new_order = existing_columns
        
        # Reordenar el dataframe
        df_reordered = df[new_order]
        
        return df_reordered
    except Exception as e:
        print(f"Error al reordenar columnas: {str(e)}")
        return df  # Devolver el dataframe original si hay error
def create_descuento_summary(df_chequeo):
    """Crea un resumen de los descuentos (errores) registrados en el chequeo."""
    try:
        # Imprimir columnas disponibles para diagnóstico
        print("\n=== COLUMNAS DISPONIBLES EN DF_CHEQUEO ===")
        for i, col in enumerate(df_chequeo.columns):
            print(f"{i}: '{col}' (tipo: {type(col)}, longitud: {len(str(col))})")
        print("========================================\n")
        
        # Buscar columna de chequeador - usar 'Nombre de usuario' como primera opción
        chequeador_col = None
        if 'Nombre de usuario' in df_chequeo.columns:
            chequeador_col = 'Nombre de usuario'
            print(f"Usando 'Nombre de usuario' como columna de chequeador")
        else:
            # Buscar alternativas si no está la columna específica
            for posible_col in ['Id. de usuario de ultima seleccion', 'chequeador', 'id_chequeador']:
                if posible_col in df_chequeo.columns:
                    chequeador_col = posible_col
                    print(f"Usando '{chequeador_col}' como columna de chequeador")
                    break
            
            # Si aún no encontramos, buscar algo parecido
            if not chequeador_col:
                for col in df_chequeo.columns:
                    col_lower = str(col).lower()
                    if 'usuario' in col_lower and ('ultima' in col_lower or 'seleccion' in col_lower or 'nombre' in col_lower):
                        chequeador_col = col
                        print(f"Encontrada columna alternativa para chequeador: '{chequeador_col}'")
                        break
        
        # Determinar las otras columnas necesarias
        usuario_col = None
        for posible_col in ['id usuario', 'id_usuario', 'Usuario', 'usuario']:
            if posible_col in df_chequeo.columns:
                usuario_col = posible_col
                print(f"Encontrada columna de usuario: '{usuario_col}'")
                break
        
        carga_col = None
        for posible_col in ['Numero de carga', 'numero_carga', 'Carga', 'carga']:
            if posible_col in df_chequeo.columns:
                carga_col = posible_col
                print(f"Encontrada columna de carga: '{carga_col}'")
                break
        
        # Verificar si tenemos la columna de consistencia para filtrar
        if 'consistencia' in df_chequeo.columns:
            df_errores = df_chequeo[df_chequeo['consistencia'] == 'MALO'].copy()
            print(f"Filtrando por consistencia == 'MALO': {len(df_errores)} registros")
        else:
            # Si no tenemos consistencia, usar todo el dataframe o filtrar por discqty > 0
            if 'discqty' in df_chequeo.columns:
                df_errores = df_chequeo[df_chequeo['discqty'] > 0].copy()
                print(f"Filtrando por discqty > 0: {len(df_errores)} registros")
            else:
                df_errores = df_chequeo.copy()
                print(f"Sin filtro, usando todos los registros: {len(df_errores)}")
        
        # Si no tenemos las columnas mínimas necesarias o no hay datos, devolver DataFrame vacío
        if not chequeador_col or not usuario_col or not carga_col or df_errores.empty:
            missing_columns = []
            if not chequeador_col:
                missing_columns.append("columna de chequeador")
            if not usuario_col:
                missing_columns.append("columna de usuario")
            if not carga_col:
                missing_columns.append("columna de número de carga")
            
            if missing_columns:
                st.warning(f"No se pudieron encontrar las siguientes columnas: {', '.join(missing_columns)}")
            
            if df_errores.empty:
                st.info("No hay registros que cumplan los criterios de filtro")
            
            return pd.DataFrame()
        
        # Agrupar por las columnas identificadas
        print(f"Agrupando por: {chequeador_col}, {usuario_col}, {carga_col}")
        if 'discqty' in df_errores.columns:
            # Si existe discqty, sumarlo
            agrupacion = df_errores.groupby([chequeador_col, usuario_col, carga_col])['discqty'].sum().reset_index()
            agrupacion.rename(columns={'discqty': 'Cantidad'}, inplace=True)
        else:
            # De lo contrario, contar registros
            agrupacion = df_errores.groupby([chequeador_col, usuario_col, carga_col]).size().reset_index(name='Cantidad')
        
        # Ordenar por cantidad de errores (mayor a menor)
        agrupacion = agrupacion.sort_values('Cantidad', ascending=False)
        
        # Renombrar columnas para claridad
        agrupacion.rename(columns={
            chequeador_col: 'Chequeador',
            usuario_col: 'Usuario',
            carga_col: 'Numero de carga'
        }, inplace=True)
        
        # Añadir fila de total general
        total_cantidad = agrupacion['Cantidad'].sum()
        total_row = pd.DataFrame({
            'Chequeador': ['TOTAL GENERAL'],
            'Usuario': [''],
            'Numero de carga': [''],
            'Cantidad': [total_cantidad]
        })
        
        # Concatenar el total al final
        resultado_final = pd.concat([agrupacion, total_row], ignore_index=True)
        
        print(f"Resumen creado con {len(resultado_final)-1} registros + total general")
        return resultado_final
    except Exception as e:
        st.error(f"Error en create_descuento_summary: {str(e)}")
        print(f"Error detallado: {str(e)}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()
def format_dataframe(df):
    """Aplica formato a las columnas del dataframe para su visualización."""
    try:
        df_formatted = df.copy()
        
        # Formatear columnas numéricas
        if 'CAJAS' in df_formatted.columns:
            df_formatted['CAJAS'] = df_formatted['CAJAS'].fillna(0).astype(int)
        
        if 'Cjs c/ Error' in df_formatted.columns:
            df_formatted['Cjs c/ Error'] = df_formatted['Cjs c/ Error'].fillna(0).astype(int)
        
        if 'Rendimiento' in df_formatted.columns:
    # Forzar conversión a entero de forma explícita
             df_formatted['Rendimiento'] = df_formatted['Rendimiento'].astype(float).round(0).astype(int)
             
        if '% Error' in df_formatted.columns:
            df_formatted['% Error'] = df_formatted['% Error'].fillna(0).round(2)
        
        return df_formatted
    except Exception as e:
        st.error(f"Error en format_dataframe: {str(e)}")
        return df

def sort_dataframe(df):
    """Ordena el dataframe según criterios específicos."""
    try:
        # Orden definido de empresas
        ORDER_EMPRESAS = ["SAEP", "SINERGY", "J. CATALAN Y CIA. LTDA", "IMAGEN", "J. CATALAN Y CIA. LTDA RED BULL"]
        
        # Crear una copia para no modificar el original
        df_sorted = df.copy()
        
        # Crear un DataFrame para cada tipo de fila (datos normales, subtotales, total general)
        datos_normales = df_sorted[~df_sorted['USUARIO'].astype(str).str.startswith('Total')].copy()
        subtotales = df_sorted[df_sorted['USUARIO'].astype(str).str.startswith('Total ') & 
                              (df_sorted['USUARIO'] != 'TOTAL GENERAL')].copy()
        total_general = df_sorted[df_sorted['USUARIO'] == 'TOTAL GENERAL'].copy()
        
        # Para los datos normales, ordenar por empresa (según ORDER_EMPRESAS) y luego por CAJAS descendente dentro de cada empresa
        result_pieces = []
        
        # Para cada empresa en el orden definido
        for empresa in ORDER_EMPRESAS:
            # Datos de usuarios normales para esta empresa
            empresa_data = datos_normales[datos_normales['Empresa'] == empresa].copy()
            if not empresa_data.empty:
                # Ordenar por CAJAS descendente
                empresa_data = empresa_data.sort_values('CAJAS', ascending=False)
                result_pieces.append(empresa_data)
                
                # Encontrar el subtotal correspondiente a esta empresa
                empresa_subtotal = subtotales[subtotales['Empresa'] == empresa].copy()
                if not empresa_subtotal.empty:
                    result_pieces.append(empresa_subtotal)
        
        # Agregar el total general al final
        if not total_general.empty:
            result_pieces.append(total_general)
        
        # Combinar todos los fragmentos en un solo DataFrame
        if result_pieces:
            df_final = pd.concat(result_pieces, ignore_index=True)
            return df_final
        else:
            return df_sorted
            
    except Exception as e:
        st.error(f"Error en sort_dataframe: {str(e)}")
        print(f"Error detallado en sort_dataframe: {str(e)}")
        import traceback
        traceback.print_exc()
        return df

def highlight_cells(df, min_rendimiento, mediana_rendimiento, max_rendimiento):
    """Aplica formato condicional a las celdas del dataframe según criterios específicos.
    Rendimiento: mínimo en rojo, mediana en amarillo, máximo en verde.
    % Error: > 0.05 en rojo, <= 0.05 en verde.
    """
    try:
        # Si el dataframe está vacío, devolver sin estilo
        if df.empty:
            return df.style
            
        # Verificar y manejar valores NaN o indefinidos
        if pd.isna(min_rendimiento):
            min_rendimiento = 0
        if pd.isna(mediana_rendimiento):
            mediana_rendimiento = 100
        if pd.isna(max_rendimiento):
            max_rendimiento = 200
            
        # Imprimir valores para diagnóstico
        print(f"Valores para formato: min={min_rendimiento}, mediana={mediana_rendimiento}, max={max_rendimiento}")
            
        def rendimiento_color(val):
            """Aplica color al rendimiento según los criterios específicos."""
            if pd.isna(val):
                return ''
                
            # Para un degradado, calculamos dónde está el valor entre el mínimo y máximo
            if val <= min_rendimiento:
                # Rojo para valores cercanos al mínimo
                return 'background-color: #FF6B6B; color: #ffffff; font-weight: bold'
            elif val <= mediana_rendimiento:
                # Amarillo para valores cercanos a la mediana
                ratio = (val - min_rendimiento) / (mediana_rendimiento - min_rendimiento)
                # Degradado de rojo a amarillo
                r = 255
                g = 107 + int(148 * ratio)  # De 107 a 255
                b = 107 + int(20 * ratio)   # De 107 a 127
                return f'background-color: rgb({r},{g},{b}); color: #000000; font-weight: bold'
            else:
                # Verde para valores superiores a la mediana
                ratio = min(1, (val - mediana_rendimiento) / (max_rendimiento - mediana_rendimiento))
                # Degradado de amarillo a verde
                r = 255 - int(155 * ratio)  # De 255 a 100
                g = 255                     # Mantener en 255
                b = 127 - int(127 * ratio)  # De 127 a 0
                return f'background-color: rgb({r},{g},{b}); color: #000000; font-weight: bold'
            
        def error_color(val):
            """Aplica color al % de error: rojo si > 0.05, verde si <= 0.05."""
            if pd.isna(val):
                return ''
            elif val > 0.05:
                return 'background-color: #FF6B6B; color: #ffffff; font-weight: bold'  # Rojo
            else:
                return 'background-color: #98FB98; color: #006400; font-weight: bold'  # Verde
            
        def usuario_color(val):
            """Aplica formato a filas de totales basado en USUARIO."""
            if isinstance(val, str) and ('Total' in val or 'TOTAL' in val):
                return 'font-weight: bold; background-color: #E0E0E0'
            return ''
            
        # Aplicar formatos
        styled = df.style
        
        # Aplicar formato a columnas específicas, evitando filas de totales para rendimiento
        if 'Rendimiento' in df.columns:
            # Crear máscara para excluir filas de totales
            no_totales = ~df['USUARIO'].astype(str).str.contains('Total|TOTAL')
            # Usar .applymap con subset para aplicar solo a las celdas deseadas
            styled = styled.applymap(
                rendimiento_color, 
                subset=pd.IndexSlice[no_totales, ['Rendimiento']]
            )
            
        if '% Error' in df.columns:
            styled = styled.applymap(error_color, subset=['% Error'])
            
        if 'USUARIO' in df.columns:
            styled = styled.applymap(usuario_color, subset=['USUARIO'])
            
        # Formatear todas las columnas numéricas - Asegurar que Rendimiento no tiene decimales
        if 'CAJAS' in df.columns:
            styled = styled.format({'CAJAS': '{:,.0f}'})
        if 'Rendimiento' in df.columns:
            styled = styled.format({'Rendimiento': '{:,.0f}'})  # Sin decimales
        if 'Cjs c/ Error' in df.columns:
            styled = styled.format({'Cjs c/ Error': '{:,.0f}'})
        if '% Error' in df.columns:
            styled = styled.format({'% Error': '{:.2f}%'})
            
        return styled
    except Exception as e:
        st.error(f"Error en highlight_cells: {str(e)}")
        print(f"Error detallado en highlight_cells: {str(e)}")
        import traceback
        traceback.print_exc()
        return df.style  # Devolver un estilo básico sin formateo
    

def create_nivel_carga_summary(df_picking):
    """Crea el resumen de nivel de carga, incluyendo Sub-LPN y LPN."""
    try:
        # Asegurarse de que tenemos las columnas necesarias
        if 'Nivel de carga' not in df_picking.columns or 'Fecha Entrega' not in df_picking.columns or 'Cajas' not in df_picking.columns:
            raise ValueError("Columnas necesarias no encontradas en df_picking")
        
        # Crear una copia para evitar modificaciones no deseadas
        df = df_picking.copy()
        
        # IMPORTANTE: No filtrar por nivel de carga para incluir todos los niveles (LPN, Sub-LPN, etc.)
        # Este es un cambio clave: asegurarse de no filtrar ningún nivel de carga
        
        # Crear tabla pivote
        pivot_nivel_carga = pd.pivot_table(
            df,
            values='Cajas',
            index='Nivel de carga',
            columns='Fecha Entrega',
            aggfunc='sum',
            fill_value=0,
            margins=True,
            margins_name='Total general'
        )
        
        # Ordenar el índice para que "Total general" aparezca al final
        if 'Total general' in pivot_nivel_carga.index:
            new_index = [idx for idx in pivot_nivel_carga.index if idx != 'Total general'] + ['Total general']
            pivot_nivel_carga = pivot_nivel_carga.reindex(new_index)
        
        # Verificar si "LPN" está en el índice
        if 'LPN' not in pivot_nivel_carga.index:
            st.warning("No se encontraron registros con Nivel de carga 'LPN' en los datos")
            print("Niveles de carga disponibles:", df['Nivel de carga'].unique())
        
        return pivot_nivel_carga
    except Exception as e:
        st.error(f"Error en nivel de carga: {str(e)}")
        print("Error detallado:", str(e))
        print("Columnas disponibles:", df_picking.columns.tolist() if df_picking is not None else "None")
        print("Niveles de carga únicos:", df_picking['Nivel de carga'].unique() if df_picking is not None and 'Nivel de carga' in df_picking.columns else "None")
        return pd.DataFrame()
    
def export_to_excel(df_picking, df_chequeo, reporte_principal, nivel_carga, descuento_summary):
    """Exporta los dataframes a un archivo Excel con formato consistente."""
    try:
        import io
        from io import BytesIO
        import xlsxwriter
        
        # Crear un objeto BytesIO para guardar el archivo
        output = BytesIO()
        
        # Limpiar valores NaN e Infinitos antes de escribir
        def clean_dataframe(df):
            if df is None or df.empty:
                return df
            df_clean = df.copy()
            # Reemplazar NaN e Infinitos con valores que Excel pueda manejar
            for col in df_clean.columns:
                if df_clean[col].dtype == 'float64' or df_clean[col].dtype == 'int64':
                    # Reemplazar infinitos con un valor muy grande pero finito
                    df_clean[col] = df_clean[col].replace([float('inf'), float('-inf')], 0)
                    # Reemplazar NaN con ceros
                    df_clean[col] = df_clean[col].fillna(0)
            return df_clean
        
        # Limpiar todos los dataframes
        reporte_principal_clean = clean_dataframe(reporte_principal)
        nivel_carga_clean = clean_dataframe(nivel_carga)
        descuento_summary_clean = clean_dataframe(descuento_summary)
        df_picking_clean = clean_dataframe(df_picking)
        df_chequeo_clean = clean_dataframe(df_chequeo)
        
        # Crear el archivo Excel con xlsxwriter, sin opciones específicas
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Hoja 1: Reporte Principal
            reporte_principal_clean.to_excel(writer, sheet_name='Reporte Principal', index=False)
            
            # Hoja 2: Nivel de Carga
            if nivel_carga_clean is not None and not nivel_carga_clean.empty:
                nivel_carga_clean.to_excel(writer, sheet_name='Nivel de Carga')
            
            # Hoja 3: Descuentos
            if descuento_summary_clean is not None and not descuento_summary_clean.empty:
                descuento_summary_clean.to_excel(writer, sheet_name='Descuentos', index=False)
            
            # Hoja 4: Datos Picking (para referencia)
            if df_picking_clean is not None:
                # Seleccionar columnas relevantes para reducir tamaño
                cols_picking = [col for col in df_picking_clean.columns if col in [
                    'id usuario', 'Empresa', 'Fecha Entrega', 'Nivel de carga',
                    'Hora Inicio', 'Hora Termino', 'Cajas', 'Descripcion'
                ]]
                df_picking_clean[cols_picking].to_excel(writer, sheet_name='Datos Picking', index=False)
            
            # Hoja 5: Datos Chequeo (para referencia)
            if df_chequeo_clean is not None:
                # Seleccionar columnas relevantes para reducir tamaño
                cols_chequeo = [col for col in df_chequeo_clean.columns if col in [
                    'id usuario', 'empresa', 'Tipo de pedido', 'Codigo de Articulo',
                    'Descripcion', 'Cantidad de unidades', 'discqty'
                ]]
                df_chequeo_clean[cols_chequeo].to_excel(writer, sheet_name='Datos Chequeo', index=False)
                
            # Obtener el workbook y worksheets
            workbook = writer.book
            worksheet_principal = writer.sheets['Reporte Principal']
            
            # Definir formatos
            formats = {
                'header': workbook.add_format({
                    'bold': True,
                    'bg_color': '#D0E0F3',
                    'border': 1
                }),
                'total': workbook.add_format({
                    'bold': True,
                    'bg_color': '#E0E0E0',
                    'border': 1
                }),
                # Formatos para degradado de rendimiento
                'rend_min': workbook.add_format({
                    'bg_color': '#FF6B6B',
                    'font_color': '#FFFFFF',  # Cambiado de 'color' a 'font_color'
                    'bold': True,
                    'num_format': '#,##0'
                }),
                'rend_low': workbook.add_format({
                    'bg_color': '#FFB347',
                    'font_color': '#000000',  # Cambiado de 'color' a 'font_color'
                    'bold': True,
                    'num_format': '#,##0'
                }),
                'rend_med': workbook.add_format({
                    'bg_color': '#FFFF99',
                    'font_color': '#000000',  # Cambiado de 'color' a 'font_color'
                    'bold': True,
                    'num_format': '#,##0'
                }),
                'rend_high': workbook.add_format({
                    'bg_color': '#90EE90',
                    'font_color': '#000000',  # Cambiado de 'color' a 'font_color'
                    'bold': True,
                    'num_format': '#,##0'
                }),
                # Formatos para el % de error
                'error_good': workbook.add_format({
                    'bg_color': '#98FB98',
                    'font_color': '#006400',  # Cambiado de 'color' a 'font_color'
                    'bold': True,
                    'num_format': '0.00%'
                }),
                'error_bad': workbook.add_format({
                    'bg_color': '#FF6B6B',
                    'font_color': '#FFFFFF',  # Cambiado de 'color' a 'font_color'
                    'bold': True,
                    'num_format': '0.00%'
                }),
                'number': workbook.add_format({
                    'num_format': '#,##0'
                }),
                'percent': workbook.add_format({
                    'num_format': '0.00%'
                })
            }
            
            # Aplicar formato a encabezados
            for col_num, value in enumerate(reporte_principal_clean.columns.values):
                worksheet_principal.write(0, col_num, value, formats['header'])
            
            # Aplicar formato condicional a las celdas del reporte principal
            usuario_col = None
            rendimiento_col = None
            error_col = None
            cajas_col = None
            
            # Encontrar índices de columnas
            for col_num, col_name in enumerate(reporte_principal_clean.columns):
                if col_name == 'USUARIO':
                    usuario_col = col_num
                elif col_name == 'Rendimiento':
                    rendimiento_col = col_num
                elif col_name == '% Error':
                    error_col = col_num
                elif col_name == 'CAJAS':
                    cajas_col = col_num
            
            # Versión mejorada para aplicar formatos con degradado
            try:
                # Obtener valores de referencia para formato condicional
                min_rendimiento = 0
                mediana_rendimiento = 200
                max_rendimiento = 310  # Meta de rendimiento
                
                if 'Rendimiento' in reporte_principal_clean.columns:
                    rendimientos = reporte_principal_clean['Rendimiento'].dropna()
                    if not rendimientos.empty:
                        min_rendimiento = rendimientos.min()
                        # Usar mediana como punto medio para el degradado
                        mediana_rendimiento = rendimientos.median()
                
                for row_num, row in enumerate(reporte_principal_clean.itertuples(index=False), start=1):
                    # Determinar si es una fila de total
                    is_total = False
                    if usuario_col is not None and row_num < len(reporte_principal_clean) + 1:
                        usuario = str(getattr(row, 'USUARIO', ''))
                        if 'Total' in usuario or 'TOTAL' in usuario:
                            is_total = True
                    
                    for col_num, value in enumerate(row):
                        try:
                            # Usar try para cada celda para evitar errores
                            if pd.isna(value):
                                value = 0
                            
                            if is_total:
                                # Formato para totales
                                worksheet_principal.write(row_num, col_num, value, formats['total'])
                            
                            # Formato degradado para rendimiento (solo para filas que no son totales)
                            elif rendimiento_col is not None and col_num == rendimiento_col and isinstance(value, (int, float)) and not is_total:
                                # Degradado de rendimiento
                                if value < min_rendimiento + (mediana_rendimiento - min_rendimiento) * 0.33:
                                    fmt = formats['rend_min']  # Rojo
                                elif value < min_rendimiento + (mediana_rendimiento - min_rendimiento) * 0.66:
                                    fmt = formats['rend_low']  # Naranja
                                elif value < mediana_rendimiento + (max_rendimiento - mediana_rendimiento) * 0.5:
                                    fmt = formats['rend_med']  # Amarillo
                                else:
                                    fmt = formats['rend_high']  # Verde
                                
                                worksheet_principal.write(row_num, col_num, value, fmt)
                            
                            # Formato para % Error
                            elif error_col is not None and col_num == error_col and isinstance(value, (int, float)):
                                # Formato condicional para % Error
                                if value > 0.05:
                                    worksheet_principal.write(row_num, col_num, value/100, formats['error_bad'])
                                else:
                                    worksheet_principal.write(row_num, col_num, value/100, formats['error_good'])
                            
                            # Formato para CAJAS
                            elif cajas_col is not None and col_num == cajas_col and isinstance(value, (int, float)):
                                worksheet_principal.write(row_num, col_num, value, formats['number'])
                            
                            else:
                                # Formato normal
                                worksheet_principal.write(row_num, col_num, value)
                                
                        except Exception as cell_error:
                            # Si hay error al formatear una celda, escribirla sin formato
                            try:
                                worksheet_principal.write(row_num, col_num, str(value))
                            except:
                                worksheet_principal.write(row_num, col_num, "Error")
                            print(f"Error al formatear celda ({row_num}, {col_num}): {str(cell_error)}")
                
                # Añadir una sección de información sobre la meta
                row_meta = len(reporte_principal_clean) + 3
                
                # Añadir título
                meta_format = workbook.add_format({
                    'bold': True,
                    'font_size': 14,
                    'align': 'center',
                    'valign': 'vcenter',
                    'font_color': 'blue',
                    'border': 1
                })
                
                # Escribir información de la meta
                worksheet_principal.merge_range(row_meta, 0, row_meta, 2, "INFORMACIÓN DE METAS", meta_format)
                
                # Formato para datos de meta
                meta_data_format = workbook.add_format({
                    'bold': True,
                    'align': 'left',
                    'valign': 'vcenter',
                    'font_size': 12
                })
                
                # Valor de meta
                meta_value_format = workbook.add_format({
                    'bold': True,
                    'align': 'center',
                    'valign': 'vcenter',
                    'font_size': 12,
                    'font_color': 'blue',
                    'num_format': '#,##0'
                })
                
                # Escribir meta de rendimiento
                worksheet_principal.write(row_meta + 2, 0, "Meta de Rendimiento:", meta_data_format)
                worksheet_principal.write(row_meta + 2, 1, 310, meta_value_format)
                worksheet_principal.write(row_meta + 2, 2, "cajas/hora", meta_data_format)
                
                # Escribir meta de error
                worksheet_principal.write(row_meta + 3, 0, "Meta de % Error:", meta_data_format)
                worksheet_principal.write(row_meta + 3, 1, 0.0005, workbook.add_format({
                    'bold': True,
                    'align': 'center',
                    'valign': 'vcenter',
                    'font_size': 12,
                    'font_color': 'blue',
                    'num_format': '0.00%'
                }))
                worksheet_principal.write(row_meta + 3, 2, "(menor es mejor)", meta_data_format)
                
                # Añadir leyenda del formato de colores
                worksheet_principal.merge_range(row_meta + 5, 0, row_meta + 5, 2, "LEYENDA DE COLORES", meta_format)
                
                # Leyenda de rendimiento
                worksheet_principal.write(row_meta + 7, 0, "Rendimiento Bajo", formats['rend_min'])
                worksheet_principal.write(row_meta + 8, 0, "Rendimiento Medio-Bajo", formats['rend_low'])
                worksheet_principal.write(row_meta + 9, 0, "Rendimiento Medio", formats['rend_med'])
                worksheet_principal.write(row_meta + 10, 0, "Rendimiento Alto", formats['rend_high'])
                
                # Leyenda de error
                worksheet_principal.write(row_meta + 7, 2, "Error Aceptable", formats['error_good'])
                worksheet_principal.write(row_meta + 8, 2, "Error Elevado", formats['error_bad'])
                
            except Exception as format_error:
                print(f"Error al aplicar formatos: {str(format_error)}")
                import traceback
                traceback.print_exc()
                # Continuar sin aplicar formatos adicionales
            
            # Ajustar anchos de columnas
            worksheet_principal.set_column('A:A', 12)  # Fecha
            worksheet_principal.set_column('B:B', 15)  # Usuario
            worksheet_principal.set_column('C:C', 25)  # Empresa
            worksheet_principal.set_column('D:D', 20)  # Descripción
            worksheet_principal.set_column('E:Z', 12)  # Resto de columnas
        
        # Posicionar el puntero al inicio del archivo
        output.seek(0)
        
        return output
    except Exception as e:
        st.error(f"Error en export_to_excel: {str(e)}")
        print(f"Error detallado en export_to_excel: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def get_formatted_date(date_str):
    """Convierte una fecha en string al formato DD-MM-YYYY."""
    try:
        if isinstance(date_str, pd.Timestamp):
            return date_str.strftime('%d-%m-%Y')
        
        # Intentar diferentes formatos comunes
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y']
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(str(date_str), fmt)
                return parsed_date.strftime('%d-%m-%Y')
            except:
                continue
        
        # Si no se pudo convertir, devolver el string original
        return str(date_str)
    except Exception as e:
        print(f"Error en get_formatted_date: {str(e)}")
        return str(date_str)
