import os
import os
from flask import Flask, jsonify, request
import traceback
from dotenv import load_dotenv # Importa la librería

load_dotenv() # Carga las variables del archivo .env al entorno

# Importar tus clases y funciones
from conectionmongodb_p import MongoPartidosUploader
# ... (el resto de tu app.py sigue igual)

app = Flask(__name__)

# --- Configuración ---
# Es MUY recomendable que configures MONGO_URI y THE_ODDS_API_KEY como variables de entorno en Railway.

# Para MONGO_URI:
# En Railway, ve a tu servicio -> Variables -> Nueva Variable
# Key: MONGO_URI
# Value: mongodb+srv://julichavez06admin:AESPA17king@mongodb101.jlpx2.mongodb.net/IQscore_DB?retryWrites=true&w=majority&appName=MongoDB101
MONGO_URI_FROM_ENV = os.environ.get("MONGO_URI")
DB_NAME = "IQscore_DB"  # Puedes mantenerlos o también hacerlos variables de entorno
COLLECTION_NAME = "Partidos"

# Para THE_ODDS_API_KEY:
# Esta ya la manejas con os.environ.get en tus scripts scraptoP.py y scriptlab1.py,
# así que solo asegúrate de que la variable de entorno THE_ODDS_API_KEY esté definida en Railway.
# Key: THE_ODDS_API_KEY
# Value: tu_api_key_de_the_odds_api (ej. 3140160b8ddbab8f063b58b9b1817cc8)

# --- Rutas de la Aplicación ---

@app.route('/')
def home():
    return "Servicio de scraping y carga a MongoDB. Usa el endpoint POST /ejecutar-proceso para iniciar."

@app.route('/ejecutar-proceso', methods=['POST'])
def trigger_full_process():
    if not MONGO_URI_FROM_ENV:
        print("Error: La variable de entorno MONGO_URI no está configurada.")
        return jsonify({"error": "Configuración del servidor incompleta: MONGO_URI no definida."}), 500

    try:
        # Paso 1: Ejecutar el scraping para generar los archivos CSV.
        # La función ejecutar_proceso_completo() ya se encarga de:
        # 1. Llamar a procesar_y_guardar_todas_ligas() (que crea "cuotas_todas_ligas.csv").
        # 2. Llamar a procesar_y_guardar_champions() (que crea "cuotas_champions_league.csv").
        # Las impresiones dentro de estas funciones irán a los logs de Railway.
        print("Iniciando proceso de scraping...")
        ejecutar_proceso_completo()
        print("Proceso de scraping completado. Archivos CSV deberían estar generados.")

        # Nombres de los archivos CSV generados
        csv_todas_ligas = "cuotas_todas_ligas.csv"
        csv_champions = "cuotas_champions_league.csv"

        # Verificar que los archivos CSV existen antes de continuar
        if not os.path.exists(csv_todas_ligas):
            error_msg = f"Error crítico: El archivo {csv_todas_ligas} no fue encontrado después del scraping."
            print(error_msg)
            return jsonify({"error": error_msg}), 500
        
        if not os.path.exists(csv_champions):
            error_msg = f"Error crítico: El archivo {csv_champions} no fue encontrado después del scraping."
            print(error_msg)
            return jsonify({"error": error_msg}), 500

        # Paso 2: Cargar los datos de los CSV a MongoDB.
        print("Iniciando carga a MongoDB...")
        uploader = MongoPartidosUploader(
            uri=MONGO_URI_FROM_ENV, # Usar la URI desde la variable de entorno
            db_name=DB_NAME,
            collection_name=COLLECTION_NAME
        )
        
        uploader.insertar_datos(csv_todas_ligas)
        uploader.insertar_datos(csv_champions, liga="Champions League")
        print("Carga a MongoDB completada.")
        
        return jsonify({"message": "Proceso completo de scraping y carga a MongoDB finalizado exitosamente."}), 200
    
    except Exception as e:
        # Imprimir el error completo y el stack trace a los logs para depuración
        error_message = f"Ocurrió un error en el servidor durante /ejecutar-proceso: {str(e)}"
        print(error_message)
        traceback.print_exc() 
        return jsonify({"error": error_message}), 500

# --- Bloque para Ejecución ---
if __name__ == '__main__':
    # Railway usará Gunicorn, por lo que este bloque __main__ es principalmente para desarrollo local.
    # Railway te asignará un puerto a través de la variable de entorno PORT.
    port = int(os.environ.get("PORT", 8080)) # Usar 8080 como default para local si PORT no está seteado
    # debug=True es útil para desarrollo, pero desactívalo o quítalo para producción con Gunicorn.
    app.run(host='0.0.0.0', port=port, debug=True)