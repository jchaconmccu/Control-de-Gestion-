import streamlit as st
import os
import json
from src.visualization import main as run_visualization
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

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

def initialize_service():
    """Inicializa el servicio de Google Drive y lo guarda en la sesión."""
    if 'drive_service' not in st.session_state:
        try:
            st.session_state.drive_service = get_drive_service()
        except Exception as e:
            st.error(f"No se pudo inicializar el servicio de Google Drive: {str(e)}")
            st.stop()

def main():
    st.set_page_config(page_title="Reporte de Picking y Chequeo",
                      layout="wide", page_icon="📊")
    
    # Inicializar servicio de Drive
    initialize_service()
    
    # Ejecutar la visualización principal
    if 'drive_service' in st.session_state:
        run_visualization()
    else:
        st.warning("No se pudo establecer conexión con Google Drive. Verifica tus credenciales.")

if __name__ == "__main__":
    main()