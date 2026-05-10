import sys
import os
import streamlit.web.cli as stcli
import webbrowser
import threading
import time

def abrir_navegador():
    # Espera 3 segundos a que el servidor arranque y abre la pestaña
    time.sleep(3)
    webbrowser.open("http://localhost:8501")

# Apagamos todas las funciones de red y el modo desarrollador
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false" # <-- ESTA ES LA MAGIA PARA EL ERROR

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        directorio = sys._MEIPASS
    else:
        directorio = os.path.dirname(os.path.abspath(__file__))
        
    script_path = os.path.join(directorio, "app.py")
    
    # Arrancamos el temporizador para abrir Chrome
    threading.Thread(target=abrir_navegador, daemon=True).start()
    
    # Le inyectamos los comandos a Streamlit (forzando que el dev mode esté en false)
    sys.argv = [
        "streamlit", "run", script_path, 
        "--server.port=8501", 
        "--global.developmentMode=false"
    ]
    
    # Iniciamos el sistema
    sys.exit(stcli.main())