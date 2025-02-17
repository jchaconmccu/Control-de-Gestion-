import os
import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st

# Definición de constantes
PK_IMAGEN = {'SEBIGSEGO', 'CTAPIAV', 'DIENIALPU'}
ZONA_TRABAJO = {'Zona Trabajo Licores 02', 'Zona Trabajo Modula'}
ZONA_CHEQUEO = {'ZT-LIC-02', 'ZT-MOD'}
ORDER_EMPRESAS = ["SAEP", "SINERGY", "J. CATALAN Y CIA. LTDA", "IMAGEN", "J. CATALAN Y CIA. LTDA RED BULL"]

# Rutas de archivos
picking_file_path = r"C:\Users\JCHACONM\Desktop\CARGA PICKING\Picking.xls"
check_file_path = r"C:\Users\JCHACONM\Desktop\CARGA PICKING\Pallet chek.xls"

def cargar_excel(ruta_archivo):
    """Carga un archivo Excel, manejando extensiones .xls y .xlsx automáticamente."""
    try:
        extension = ruta_archivo.split('.')[-1].lower()
        engine = 'xlrd' if extension == 'xls' else 'openpyxl'
        return pd.read_excel(ruta_archivo, sheet_name=0, engine=engine)
    except Exception as e:
        raise ValueError(f"Error al cargar el archivo {ruta_archivo}: {e}")

def preparar_dataframes():
    """Carga y preprocesa los dataframes de picking y chequeo."""
    # Cargar archivos
    df_picking = cargar_excel(picking_file_path)
    df_chequeo = cargar_excel(check_file_path)
    
    # Renombrar columnas clave
    df_chequeo.rename(columns={
        'Nombre de grupo de autorizacion': 'empresa', 
        'Id. de usuario de ultima seleccion': 'id usuario'
    }, inplace=True, errors='ignore')
    
    df_picking.rename(columns={
        'Id. de usuario de ultima seleccion': 'id usuario'
    }, inplace=True, errors='ignore')
    
    # Limpiar espacios en columnas clave
    if 'Empresa' in df_picking.columns:
        df_picking['Empresa'] = df_picking['Empresa'].str.strip()
    if 'empresa' in df_chequeo.columns:
        df_chequeo['empresa'] = df_chequeo['empresa'].str.strip()
    
    return df_picking, df_chequeo

def aplicar_transformaciones(df_picking, df_chequeo):
    """Aplica transformaciones específicas a los dataframes."""
    # Transformaciones CAJA PICKEADA
    mask_imagen = (df_picking['Tipo de pedido'] == '3033-IMAGEN VIÑA') & \
                 (df_picking['Empresa'] == 'J. CATALAN Y CIA. LTDA') & \
                 (df_picking['id usuario'].isin(PK_IMAGEN))
    df_picking.loc[mask_imagen, 'Empresa'] = 'IMAGEN'
    
    mask_redBull = (df_picking['Empresa'] == 'J. CATALAN Y CIA. LTDA') & \
                   (df_picking['Zona de Origen'].isin(ZONA_TRABAJO))
    df_picking.loc[mask_redBull, 'Empresa'] = 'J. CATALAN Y CIA. LTDA RED BULL'
    
    # Transformaciones PALLET CHEQUEADO
    mask_chk_imagen = (df_chequeo['Tipo de pedido'] == '3033-IMAGEN VIÑA') & \
                      (df_chequeo['empresa'] == 'J. CATALAN Y CIA. LTDA') & \
                      (df_chequeo['id usuario'].isin(PK_IMAGEN))
    df_chequeo.loc[mask_chk_imagen, 'empresa'] = 'IMAGEN'
    
    # Asegurarse de que la columna 'zona_de_trabajo' existe antes de usarla
    if 'zona_de_trabajo' in df_chequeo.columns:
        mask_chk_redbull = (df_chequeo['empresa'] == 'J. CATALAN Y CIA. LTDA') & \
                           (df_chequeo['zona_de_trabajo'].isin(ZONA_CHEQUEO))
        df_chequeo.loc[mask_chk_redbull, 'empresa'] = 'J. CATALAN Y CIA. LTDA RED BULL'
    elif 'Zona de trabajo' in df_chequeo.columns:  # Comprobación alternativa
        mask_chk_redbull = (df_chequeo['empresa'] == 'J. CATALAN Y CIA. LTDA') & \
                           (df_chequeo['Zona de trabajo'].isin(ZONA_CHEQUEO))
        df_chequeo.loc[mask_chk_redbull, 'empresa'] = 'J. CATALAN Y CIA. LTDA RED BULL'
    
    # Filtrar para que solo aparezcan las empresas en ORDER_EMPRESAS
    df_picking = df_picking[df_picking['Empresa'].isin(ORDER_EMPRESAS)]
    df_chequeo = df_chequeo[df_chequeo['empresa'].isin(ORDER_EMPRESAS)]
    
    return df_picking, df_chequeo

def procesar_picking(df_picking):
    """Procesa el dataframe de picking para calcular rendimientos."""
    # Proceso diferente para usuarios PK_IMAGEN vs resto
    df_imagen = df_picking[df_picking['id usuario'].isin(PK_IMAGEN)]
    df_others = df_picking[~df_picking['id usuario'].isin(PK_IMAGEN)]
    
    # Para usuarios de PK_IMAGEN, solo acumulamos cajas (sin calcular rendimiento)
    cajas_imagen = df_imagen.groupby(['id usuario', 'Empresa', 'Descripcion', 'Fecha Entrega']).agg(
        Cajas=('Cajas', 'sum')
    ).reset_index()
    cajas_imagen['Rendimiento'] = np.nan  # No calculamos rendimiento para PK_IMAGEN
    cajas_imagen['Hora_Inicio_Min'] = pd.NaT
    cajas_imagen['Hora_Termino_Max'] = pd.NaT
    cajas_imagen['Horas Picking'] = np.nan
    
    # Para el resto de usuarios, calculamos rendimiento normalmente
    # Convertir fechas a datetime
    df_others['Hora Inicio'] = pd.to_datetime(df_others['Hora Inicio'], errors='coerce', dayfirst=True)
    df_others['Hora Termino'] = pd.to_datetime(df_others['Hora Termino'], errors='coerce', dayfirst=True)
    
    # Corregir fechas de término
    mask_termino = df_others['Hora Termino'] < df_others['Hora Inicio']
    df_others.loc[mask_termino, 'Hora Termino'] += pd.Timedelta(days=1)
    
    # Agrupar datos
    cajas_others = df_others.groupby(['id usuario', 'Empresa', 'Descripcion', 'Fecha Entrega']).agg(
        Cajas=('Cajas', 'sum'),
        Hora_Inicio_Min=('Hora Inicio', 'min'),
        Hora_Termino_Max=('Hora Termino', 'max')
    ).reset_index()
    
    # Eliminar registros con valores nulos y corregir turnos nocturnos
    valid_others = cajas_others.dropna(subset=['Hora_Inicio_Min', 'Hora_Termino_Max'])
    mask_nocturno = valid_others['Hora_Termino_Max'] < valid_others['Hora_Inicio_Min']
    valid_others.loc[mask_nocturno, 'Hora_Termino_Max'] += pd.Timedelta(days=1)
    
    # Filtrar registros inconsistentes
    valid_others = valid_others[valid_others['Hora_Termino_Max'] >= valid_others['Hora_Inicio_Min']]
    
    # Calcular horas picking y rendimiento
    valid_others['Horas Picking'] = (valid_others['Hora_Termino_Max'] - valid_others['Hora_Inicio_Min']).dt.total_seconds() / 3600
    valid_others = valid_others[(valid_others['Horas Picking'] > 0) & (valid_others['Horas Picking'] < 12)]
    valid_others['Rendimiento'] = valid_others['Cajas'] / valid_others['Horas Picking']
    
    # Filtrar rendimientos anómalos (mayores a 500 o menores que las cajas)
    valid_others = valid_others[valid_others['Rendimiento'] <= 500]
    valid_others = valid_others[valid_others['Rendimiento'] >= 0]
    valid_others = valid_others[valid_others['Rendimiento'] <= valid_others['Cajas']]
    
    # Redondear rendimiento a 2 decimales
    valid_others['Rendimiento'] = valid_others['Rendimiento'].round(2)
    
    # Unir ambos dataframes
    df_valid = pd.concat([valid_others, cajas_imagen], ignore_index=True)
    
    return df_valid

def procesar_chequeo(df_chequeo):
    """Procesa el dataframe de chequeo para calcular errores."""
    # Verificar y manejar las columnas necesarias
    if 'Cantidad de unidades' not in df_chequeo.columns:
        if 'Cantidad' in df_chequeo.columns:
            df_chequeo['Cantidad de unidades'] = df_chequeo['Cantidad']
        else:
            df_chequeo['Cantidad de unidades'] = 0  # Valor predeterminado

    if 'discqty' not in df_chequeo.columns:
        if 'Descuento' in df_chequeo.columns:
            df_chequeo['discqty'] = df_chequeo['Descuento']
        else:
            df_chequeo['discqty'] = 0  # Valor predeterminado

    pallet_grouped = df_chequeo.groupby(['id usuario', 'empresa']).agg(
        Total_Unidades=('Cantidad de unidades', 'sum'),
        Total_Descuento=('discqty', 'sum')
    ).reset_index()
    
    # Calcular porcentaje de error directamente
    pallet_grouped['% Error'] = (pallet_grouped['Total_Descuento'] / pallet_grouped['Total_Unidades']) * 100
    # Manejar casos donde Total_Unidades es cero
    pallet_grouped['% Error'] = pallet_grouped['% Error'].fillna(0).replace([np.inf, -np.inf], 0)
    # Redondear a 2 decimales
    pallet_grouped['% Error'] = pallet_grouped['% Error'].round(2)
    pallet_grouped['Total_Descuento'] = pallet_grouped['Total_Descuento'].round(0).astype(int)
    
    return pallet_grouped

def unir_datos(df_valid, pallet_grouped):
    """Une los dataframes procesados de picking y chequeo."""
    df_final = pd.merge(
        df_valid, pallet_grouped,
        how='inner', 
        left_on=['id usuario', 'Empresa'],
        right_on=['id usuario', 'empresa']
    )
    
    # Renombrar columnas
    df_final.rename(columns={
        'id usuario': 'USUARIO',
        'Total_Descuento': 'Cjs c/ Error',
        'Cajas': 'CAJAS'
    }, inplace=True)
    
    # Seleccionar columnas requeridas
    columnas_requeridas = ['Fecha Entrega', 'USUARIO', 'Empresa', 'Descripcion', 
                          'CAJAS', 'Rendimiento', 'Cjs c/ Error', '% Error']
    
    # Verificar que todas las columnas requeridas existen
    columnas_existentes = [col for col in columnas_requeridas if col in df_final.columns]
    
    # Asegurar que solo tenemos las empresas en ORDER_EMPRESAS
    df_final = df_final[df_final['Empresa'].isin(ORDER_EMPRESAS)]
    
    return df_final[columnas_existentes]
def create_grouped_report(df_final):
    """Genera el reporte agrupado desde un DataFrame."""
    try:
        # Verificar valores únicos en la columna Empresa
        print("Valores únicos en Empresa antes de procesar:")
        print(df_final['Empresa'].unique())
        
        # Limpiar y preparar datos
        df = df_final.copy()
        
        # Filtrar solo las empresas que están en ORDER_EMPRESAS
        df = df[df['Empresa'].isin(ORDER_EMPRESAS)]
        
        # Definir categorías con el orden específico
        df['Empresa'] = pd.Categorical(
            df['Empresa'],
            categories=ORDER_EMPRESAS,
            ordered=True
        )
        
        # Convertir a string antes de concatenar
        df['USUARIO'] = df['USUARIO'].fillna('').astype(str)
        
        # Identificar usuarios PK_IMAGEN
        pk_imagen_mask = df['USUARIO'].isin(PK_IMAGEN)
        
        # Crear fila de totales por empresa (excluyendo PK_IMAGEN del cálculo de rendimiento)
        df_subtotales = df.groupby('Empresa').agg({
            'CAJAS': 'sum',
            'Cjs c/ Error': 'sum'
        }).reset_index()
        
        # Calcular rendimiento promedio por empresa (excluyendo PK_IMAGEN)
        rendimientos_por_empresa = {}
        for empresa in df['Empresa'].unique():
            empresa_df = df[(df['Empresa'] == empresa) & (~pk_imagen_mask)]
            if not empresa_df.empty and pd.notna(empresa_df['Rendimiento']).any():
                rendimientos_por_empresa[empresa] = empresa_df['Rendimiento'].mean()
            else:
                rendimientos_por_empresa[empresa] = np.nan
        
        # Asignar rendimientos al dataframe de subtotales
        df_subtotales['Rendimiento'] = df_subtotales['Empresa'].map(rendimientos_por_empresa)
        
        # Convertir Empresa a string antes de concatenar
        df_subtotales['USUARIO'] = 'Total ' + df_subtotales['Empresa'].astype(str)
        
        # Calcular porcentajes de error
        df_subtotales['% Error'] = (df_subtotales['Cjs c/ Error'] / df_subtotales['CAJAS']) * 100
        df_subtotales['% Error'] = df_subtotales['% Error'].fillna(0).round(2)
        
        # Redondear valores de Rendimiento
        df_subtotales['Rendimiento'] = df_subtotales['Rendimiento'].round(2)
        
        # Calcular totales generales
        total_cajas = df['CAJAS'].sum()
        total_error_cajas = df['Cjs c/ Error'].sum()
        
        # Calcular rendimiento promedio global (excluyendo PK_IMAGEN)
        if (~pk_imagen_mask).any() and pd.notna(df.loc[~pk_imagen_mask, 'Rendimiento']).any():
            rendimiento_promedio = df.loc[~pk_imagen_mask, 'Rendimiento'].mean().round(2)
        else:
            rendimiento_promedio = np.nan
        
        # Crear fila de total general (convertir a string)
        df_total_general = pd.DataFrame({
            'Empresa': ['TOTAL GENERAL'],
            'USUARIO': ['TOTAL GENERAL'],
            'CAJAS': [total_cajas],
            'Rendimiento': [rendimiento_promedio],
            'Cjs c/ Error': [total_error_cajas],
            '% Error': [(total_error_cajas / total_cajas) * 100 if total_cajas > 0 else 0]
        })
        df_total_general['% Error'] = df_total_general['% Error'].round(2)
        
        # Unir y formatear (excluyendo 'Total SIN_ASIGNAR')
        df_final_report = pd.concat([df, df_subtotales, df_total_general],
                                  ignore_index=True)
        
        # Excluir filas no deseadas
        df_final_report = df_final_report[~df_final_report['USUARIO'].isin(['Total SIN_ASIGNAR', 'Total TOTAL GENERAL'])]
        
        # Asegurar que tenemos todas las columnas necesarias antes de ordenar
        required_columns = ['Empresa', 'USUARIO', 'CAJAS', 'Rendimiento', 'Cjs c/ Error', '% Error']
        for col in required_columns:
            if col not in df_final_report.columns:
                df_final_report[col] = np.nan
        
        # Ordenar por empresa según ORDER_EMPRESAS y luego por usuario
        # Modificación: Usar una función lambda más simple que no cause problemas de MultiIndex
        def sorting_key(x):
            result = []
            for val in x:
                if val == 'TOTAL GENERAL':
                    result.append((2, val))
                elif 'Total' in str(val):
                    result.append((1, val))
                else:
                    result.append((0, val))
            return result
        
        df_final_report = df_final_report.sort_values(
            by=['Empresa', 'USUARIO'],
            key=sorting_key
        )
        
        # Calcular estadísticas para el coloreado (excluyendo PK_IMAGEN)
        rendimientos_validos = df.loc[~pk_imagen_mask, 'Rendimiento'].dropna()
        if not rendimientos_validos.empty:
            min_rendimiento = rendimientos_validos.min()
            mediana_rendimiento = rendimientos_validos.median()
            max_rendimiento = rendimientos_validos.max()
        else:
            min_rendimiento = np.nan
            mediana_rendimiento = np.nan
            max_rendimiento = np.nan
        
        return df_final_report, min_rendimiento, mediana_rendimiento, max_rendimiento
        
    except Exception as e:
        print(f"Excepción detallada: {str(e)}")
        import traceback
        traceback.print_exc()
        raise ValueError(f"Error al crear el reporte agrupado: {str(e)}")