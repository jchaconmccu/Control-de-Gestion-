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
        # Buscar el archivo
        results = service.files().list(
            q=f"name contains '{filename}' and '{FOLDER_ID}' in parents",
            pageSize=1,
            fields="files(id, name)"
        ).execute()
        files = results.get('files', [])
        
        if not files:
            raise FileNotFoundError(f"No se encontró el archivo {filename}")
            
        file_id = files[0]['id']
        
        # Descargar el archivo
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

def preparar_dataframes():
    """Carga y preprocesa los dataframes de picking y chequeo."""
    try:
        service = get_drive_service()
        
        # Descargar archivos
        picking_content = download_excel_from_drive(service, "Picking.xls")
        chequeo_content = download_excel_from_drive(service, "Pallet chek.xls")
        
        if picking_content is None or chequeo_content is None:
            raise ValueError("No se pudieron descargar los archivos necesarios")
        
        # Cargar DataFrames
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
        # ... resto del código de procesar_picking ...
        pass
    except Exception as e:
        st.error(f"Error en procesar_picking: {str(e)}")
        return None

def procesar_chequeo(df_chequeo):
    """Procesa el dataframe de chequeo para calcular errores."""
    try:
        # ... resto del código de procesar_chequeo ...
        pass
    except Exception as e:
        st.error(f"Error en procesar_chequeo: {str(e)}")
        return None

def create_grouped_report(df_final):
    """Genera el reporte agrupado desde un DataFrame."""
    try:
        # ... resto del código de create_grouped_report ...
        pass
    except Exception as e:
        st.error(f"Error en create_grouped_report: {str(e)}")
        return None, None, None, None