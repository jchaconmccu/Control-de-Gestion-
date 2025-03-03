import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# Configuración
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
FOLDER_ID = '1rAACqx1K3-LnammeFuGPsbWV7Tqa7MbL'

def test_drive_connection():
    """Prueba la conexión con Google Drive y lista los archivos."""
    st.title("Prueba de Conexión Google Drive")
    
    # Mostrar información de la configuración
    st.write("### Configuración:")
    st.write(f"- FOLDER_ID: {FOLDER_ID}")
    st.write(f"- SCOPES: {SCOPES}")
    
    # Verificar secretos
    st.write("### Verificando secretos:")
    if "gcp_service_account" in st.secrets:
        st.success("✅ Secretos de GCP encontrados")
        st.write("Claves disponibles:")
        for key in st.secrets["gcp_service_account"].keys():
            st.write(f"- {key}")
    else:
        st.error("❌ No se encontraron los secretos de GCP")
        return

    # Crear credenciales
    st.write("### Creando credenciales...")
    try:
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=SCOPES
        )
        st.success("✅ Credenciales creadas correctamente")
    except Exception as e:
        st.error(f"❌ Error al crear credenciales: {str(e)}")
        st.exception(e)
        return

    # Construir servicio
    st.write("### Construyendo servicio de Drive...")
    try:
        service = build('drive', 'v3', credentials=credentials)
        st.success("✅ Servicio de Drive construido correctamente")
    except Exception as e:
        st.error(f"❌ Error al construir servicio: {str(e)}")
        st.exception(e)
        return

    # Listar archivos
    st.write("### Listando archivos en la carpeta...")
    try:
        results = service.files().list(
            q=f"'{FOLDER_ID}' in parents",
            pageSize=10,
            fields="files(id, name, mimeType)"
        ).execute()
        files = results.get('files', [])

        if not files:
            st.warning("No se encontraron archivos en la carpeta")
        else:
            st.success(f"✅ Se encontraron {len(files)} archivos")
            st.write("Archivos encontrados:")
            for file in files:
                st.write(f"- {file['name']} ({file['mimeType']})")

            # Botón para probar descarga
            excel_files = [f for f in files if 'excel' in f['mimeType'] or f['name'].endswith(('.xls', '.xlsx'))]
            if excel_files and st.button("Probar descarga del primer Excel"):
                file = excel_files[0]
                try:
                    request = service.files().get_media(fileId=file['id'])
                    file_content = io.BytesIO()
                    downloader = MediaIoBaseDownload(file_content, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                    st.success(f"✅ Archivo {file['name']} descargado correctamente")
                except Exception as e:
                    st.error(f"❌ Error al descargar el archivo: {str(e)}")
                    st.exception(e)

    except Exception as e:
        st.error(f"❌ Error al listar archivos: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    test_drive_connection()