import pandas as pd
import numpy as np
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import io

# Definición de constantes
PK_IMAGEN = {'SEBIGSEGO', 'CTAPIAV', 'DIENIALPU'}
ZONA_TRABAJO = {'Zona Trabajo Licores 02', 'Zona Trabajo Modula'}
ZONA_CHEQUEO = {'ZT-LIC-02', 'ZT-MOD'}
ORDER_EMPRESAS = ["SAEP", "SINERGY", "J. CATALAN Y CIA. LTDA", "IMAGEN", "J. CATALAN Y CIA. LTDA RED BULL"]
FOLDER_ID = '1rAACqx1K3-LnammeFuGPsbWV7Tqa7MbL'

def get_drive_service():
    """Configura y retorna el servicio de Google Drive usando los secretos de Streamlit."""
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

@st.cache_data
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
        
        # Verificar que los DataFrames no estén vacíos
        if df_picking.empty or df_chequeo.empty:
            raise ValueError("Los archivos están vacíos")
        
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

# El resto de las funciones (aplicar_transformaciones, procesar_picking, etc.) permanecen igual