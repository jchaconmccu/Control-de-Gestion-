import pandas as pd
import numpy as np
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# Definición de constantes
PK_IMAGEN = {'SEBIGSEGO', 'CTAPIAV', 'DIENIALPU'}
ZONA_TRABAJO = {'Zona Trabajo Licores 02', 'Zona Trabajo Modula'}
ZONA_CHEQUEO = {'ZT-LIC-02', 'ZT-MOD'}
ORDER_EMPRESAS = ["SAEP", "SINERGY", "J. CATALAN Y CIA. LTDA", "IMAGEN", "J. CATALAN Y CIA. LTDA RED BULL"]
FOLDER_ID = '1rAACqx1K3-LnammeFuGPsbWV7Tqa7MbL'

def get_drive_service():
    """Configura y retorna el servicio de Google Drive."""
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )
    return build('drive', 'v3', credentials=credentials)

def download_excel_from_drive(service, filename):
    """Descarga un archivo Excel desde Google Drive."""
    try:
        results = service.files().list(
            q=f"name contains '{filename}' and '{FOLDER_ID}' in parents",
            pageSize=1,
            fields="files(id, name)"
        ).execute()
        files = results.get('files', [])
        
        if not files:
            raise FileNotFoundError(f"No se encontró el archivo {filename}")
            
        file_id = files[0]['id']
        
        request = service.files().get_media(fileId=file_id)
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            
        file_content.seek(0)
        return file_content
    except Exception as e:
        st.error(f"Error al descargar {filename}: {str(e)}")
        return None

@st.cache_data
def preparar_dataframes():
    """Carga y preprocesa los dataframes de picking y chequeo."""
    try:
        service = get_drive_service()
        
        picking_content = download_excel_from_drive(service, "Picking.xls")
        chequeo_content = download_excel_from_drive(service, "Pallet chek.xls")
        
        if picking_content is None or chequeo_content is None:
            raise ValueError("No se pudieron descargar los archivos necesarios")
        
        df_picking = pd.read_excel(picking_content)
        df_chequeo = pd.read_excel(chequeo_content)
        
        # Renombrar columnas
        df_chequeo.rename(columns={
            'Nombre de grupo de autorizacion': 'empresa',
            'Id. de usuario de ultima seleccion': 'id usuario'
        }, inplace=True, errors='ignore')
        
        df_picking.rename(columns={
            'Id. de usuario de ultima seleccion': 'id usuario'
        }, inplace=True, errors='ignore')
        
        # Limpiar espacios
        if 'Empresa' in df_picking.columns:
            df_picking['Empresa'] = df_picking['Empresa'].str.strip()
        if 'empresa' in df_chequeo.columns:
            df_chequeo['empresa'] = df_chequeo['empresa'].str.strip()
            
        return df_picking, df_chequeo
    except Exception as e:
        st.error(f"Error en preparar_dataframes: {str(e)}")
        return None, None

def aplicar_transformaciones(df_picking, df_chequeo):
    """Aplica transformaciones específicas a los dataframes."""
    try:
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
        
        if 'zona_de_trabajo' in df_chequeo.columns:
            mask_chk_redbull = (df_chequeo['empresa'] == 'J. CATALAN Y CIA. LTDA') & \
                              (df_chequeo['zona_de_trabajo'].isin(ZONA_CHEQUEO))
            df_chequeo.loc[mask_chk_redbull, 'empresa'] = 'J. CATALAN Y CIA. LTDA RED BULL'
        elif 'Zona de trabajo' in df_chequeo.columns:
            mask_chk_redbull = (df_chequeo['empresa'] == 'J. CATALAN Y CIA. LTDA') & \
                              (df_chequeo['Zona de trabajo'].isin(ZONA_CHEQUEO))
            df_chequeo.loc[mask_chk_redbull, 'empresa'] = 'J. CATALAN Y CIA. LTDA RED BULL'
        
        # Filtrar empresas
        df_picking = df_picking[df_picking['Empresa'].isin(ORDER_EMPRESAS)]
        df_chequeo = df_chequeo[df_chequeo['empresa'].isin(ORDER_EMPRESAS)]
        
        return df_picking, df_chequeo
    except Exception as e:
        st.error(f"Error en aplicar_transformaciones: {str(e)}")
        return None, None

def procesar_picking(df_picking):
    """Procesa el dataframe de picking para calcular rendimientos."""
    try:
       
 


        # Crear una copia profunda para evitar SettingWithCopyWarning
        df_picking = df_picking.copy()
        
        # Procesar fechas antes de dividir el DataFrame
        df_picking['Hora Inicio'] = pd.to_datetime(df_picking['Hora Inicio'], errors='coerce', dayfirst=True)
        df_picking['Hora Termino'] = pd.to_datetime(df_picking['Hora Termino'], errors='coerce', dayfirst=True)
        
        # Dividir el DataFrame
        df_imagen = df_picking[(df_picking["Nivel de carga"] != "LPN") & (df_picking['id usuario'].isin(PK_IMAGEN))].copy()
        df_others = df_picking[(df_picking["Nivel de carga"] != "LPN") & (~df_picking['id usuario'].isin(PK_IMAGEN))].copy()

        # Para usuarios de PK_IMAGEN, solo acumulamos cajas
        cajas_imagen = df_imagen.groupby(['id usuario', 'Empresa', 'Descripcion', 'Fecha Entrega']).agg(
            Cajas=('Cajas', 'sum')
        ).reset_index()
        cajas_imagen['Rendimiento'] = np.nan
        cajas_imagen['Hora_Inicio_Min'] = pd.NaT
        cajas_imagen['Hora_Termino_Max'] = pd.NaT
        cajas_imagen['Horas Picking'] = np.nan
        
        # Corregir fechas de término
        mask_termino = df_others['Hora Termino'] < df_others['Hora Inicio']
        df_others.loc[mask_termino, 'Hora Termino'] += pd.Timedelta(days=1)
        
        # Agrupar datos con observed=True
        cajas_others = df_others.groupby(['id usuario', 'Empresa', 'Descripcion', 'Fecha Entrega'], observed=True).agg(
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
        
        # Filtrar rendimientos anómalos
        valid_others = valid_others[valid_others['Rendimiento'] <= 500]
        valid_others = valid_others[valid_others['Rendimiento'] >= 0]
        valid_others = valid_others[valid_others['Rendimiento'] <= valid_others['Cajas']]
        valid_others['Rendimiento'] = valid_others['Rendimiento'].round(2)
        
        # Unir ambos dataframes
        df_valid = pd.concat([valid_others, cajas_imagen], ignore_index=True)
        
        return df_valid
    except Exception as e:
        st.error(f"Error en procesar_picking: {str(e)}")
        return None

def create_grouped_report(df_final):
    """Genera el reporte agrupado desde un DataFrame."""
    try:
        # Crear una copia profunda del DataFrame
        df = df_final.copy()
        
        # Filtrar empresas y ordenar
        df = df[df['Empresa'].isin(ORDER_EMPRESAS)]
        df['Empresa'] = pd.Categorical(df['Empresa'], categories=ORDER_EMPRESAS, ordered=True)
        
        # Convertir a string antes de agrupar
        df['USUARIO'] = df['USUARIO'].fillna('').astype(str)
        
        # Identificar usuarios PK_IMAGEN
        pk_imagen_mask = df['USUARIO'].isin(PK_IMAGEN)
        
        # Agrupar con observed=True
        df_subtotales = df.groupby('Empresa', observed=True).agg({
            'CAJAS': 'sum',
            'Cjs c/ Error': 'sum'
        }).reset_index()
        
        # [resto del código igual]
        
        return df_final_report, min_rendimiento, mediana_rendimiento, max_rendimiento
        
    except Exception as e:
        st.error(f"Error en create_grouped_report: {str(e)}")
        return None, np.nan, np.nan, np.nan

def procesar_chequeo(df_chequeo):
    """Procesa el dataframe de chequeo para calcular errores."""
    try:
        # Verificar y manejar las columnas necesarias
        if 'Cantidad de unidades' not in df_chequeo.columns:
            if 'Cantidad' in df_chequeo.columns:
                df_chequeo['Cantidad de unidades'] = df_chequeo['Cantidad']
            else:
                df_chequeo['Cantidad de unidades'] = 0

        if 'discqty' not in df_chequeo.columns:
            if 'Descuento' in df_chequeo.columns:
                df_chequeo['discqty'] = df_chequeo['Descuento']
            else:
                df_chequeo['discqty'] = 0

        pallet_grouped = df_chequeo.groupby(['id usuario', 'empresa']).agg(
            Total_Unidades=('Cantidad de unidades', 'sum'),
            Total_Descuento=('discqty', 'sum')
        ).reset_index()
        
        # Calcular porcentaje de error
        pallet_grouped['% Error'] = (pallet_grouped['Total_Descuento'] / pallet_grouped['Total_Unidades']) * 100
        pallet_grouped['% Error'] = pallet_grouped['% Error'].fillna(0).replace([np.inf, -np.inf], 0)
        pallet_grouped['% Error'] = pallet_grouped['% Error'].round(2)
        pallet_grouped['Total_Descuento'] = pallet_grouped['Total_Descuento'].round(0).astype(int)
        
        return pallet_grouped
    except Exception as e:
        st.error(f"Error en procesar_chequeo: {str(e)}")
        return None

def unir_datos(df_valid, pallet_grouped):
    """Une los dataframes procesados de picking y chequeo."""
    try:
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
    except Exception as e:
        st.error(f"Error en unir_datos: {str(e)}")
        return None
    
def create_nivel_carga_summary(df_picking):
    """Crea el resumen de nivel de carga, incluyendo Sub-LPN."""
    try:
        # Asegurarse de que tenemos las columnas necesarias
        if 'Nivel de carga' not in df_picking.columns or 'Fecha Entrega' not in df_picking.columns or 'Cajas' not in df_picking.columns:
            raise ValueError("Columnas necesarias no encontradas en df_picking")
        
        # No filtramos por nivel de carga, queremos incluir todos los niveles incluyendo "Sub-LPN"
        pivot_nivel_carga = pd.pivot_table(
            df_picking,
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
        
        return pivot_nivel_carga
    except Exception as e:
        st.error(f"Error en nivel de carga: {str(e)}")
        print("Error detallado:", str(e))
        print("Columnas disponibles:", df_picking.columns.tolist() if df_picking is not None else "None")
        return pd.DataFrame()

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
        
        # Convertir a string antes de concatenar
        df['USUARIO'] = df['USUARIO'].fillna('').astype(str)
        
        # Identificar usuarios PK_IMAGEN
        pk_imagen_mask = df['USUARIO'].isin(PK_IMAGEN)
        
        # Calcular subtotales por empresa ordenados según ORDER_EMPRESAS
        subtotales = []
        for empresa in ORDER_EMPRESAS:
            empresa_df = df[df['Empresa'] == empresa]
            if not empresa_df.empty:
                # Calcular subtotal
                total_cajas = empresa_df['CAJAS'].sum()
                total_error_cajas = empresa_df['Cjs c/ Error'].sum()
                
                # Calcular rendimiento promedio (excluyendo PK_IMAGEN)
                empresa_no_pk = empresa_df[~empresa_df['USUARIO'].isin(PK_IMAGEN)]
                rendimiento_promedio = np.nan
                if not empresa_no_pk.empty and pd.notna(empresa_no_pk['Rendimiento']).any():
                    rendimiento_promedio = empresa_no_pk['Rendimiento'].mean()
                
                subtotales.append({
                    'Empresa': empresa,
                    'USUARIO': f'Total {empresa}',
                    'CAJAS': total_cajas,
                    'Rendimiento': rendimiento_promedio,
                    'Cjs c/ Error': total_error_cajas,
                    '% Error': (total_error_cajas / total_cajas * 100) if total_cajas > 0 else 0
                })
        
        df_subtotales = pd.DataFrame(subtotales)
        
        # Calcular total general
        total_cajas = df['CAJAS'].sum()
        total_error_cajas = df['Cjs c/ Error'].sum()
        rendimiento_promedio = df[~pk_imagen_mask]['Rendimiento'].mean() if (~pk_imagen_mask).any() else np.nan
        
        df_total_general = pd.DataFrame([{
            'Empresa': 'TOTAL GENERAL',
            'USUARIO': 'TOTAL GENERAL',
            'CAJAS': total_cajas,
            'Rendimiento': rendimiento_promedio,
            'Cjs c/ Error': total_error_cajas,
            '% Error': (total_error_cajas / total_cajas * 100) if total_cajas > 0 else 0
        }])
        
        # Unir todos los dataframes
        df_final_report = pd.concat([df, df_subtotales, df_total_general], ignore_index=True)
        
        # Calcular estadísticas para el coloreado
        rendimientos_validos = df[~pk_imagen_mask]['Rendimiento'].dropna()
        min_rendimiento = rendimientos_validos.min() if not rendimientos_validos.empty else np.nan
        mediana_rendimiento = rendimientos_validos.median() if not rendimientos_validos.empty else np.nan
        max_rendimiento = rendimientos_validos.max() if not rendimientos_validos.empty else np.nan
        
        return df_final_report, min_rendimiento, mediana_rendimiento, max_rendimiento, df_total_general
        
    except Exception as e:
        st.error(f"Error en create_grouped_report: {str(e)}")
        return None, np.nan, np.nan, np.nan