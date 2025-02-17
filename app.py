import streamlit as st
from src.visualization import main as run_visualization

def main():
    st.set_page_config(page_title="Reporte de Picking y Chequeo",
                      layout="wide", page_icon="📊")
    
    try:
        run_visualization()
    except Exception as e:
        st.error(f"Error en la aplicación: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()