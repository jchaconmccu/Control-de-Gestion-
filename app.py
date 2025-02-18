import streamlit as st
import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from src.visualization import main as run_visualization

# Configuración de autenticación de Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
FOLDER_ID = '1rAACqx1K3-LnammeFuGPsbWV7Tqa7MbL'

def get_drive_service():
    """Configura y retorna el servicio de Google Drive usando secretos de Streamlit."""
    try:
        # Obtener credenciales desde los secretos de Streamlit
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=SCOPES
        )
        
        # Construir el servicio
        service = build('drive', 'v3', credentials=credentials)
        return service
        
    except Exception as e:
        st.error(f"Error al configurar el servicio de Drive: {str(e)}")
        return None

def main():
    st.set_page_config(page_title="Reporte de Picking y Chequeo",
                      layout="wide", page_icon="📊")
    
    try:
        # Ejecutar la visualización principal
        run_visualization()
    except Exception as e:
        st.error(f"Error en la aplicación: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()