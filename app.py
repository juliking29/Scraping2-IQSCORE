import os
from flask import Flask, jsonify
import traceback
from dotenv import load_dotenv

# Importa tus funciones de scraping y MongoDB
from scraptoP import procesar_y_guardar_todas_ligas
from scriptlab1 import procesar_y_guardar_champions
from conectionmongodb_p import MongoPartidosUploader

load_dotenv()

app = Flask(__name__)

# Configuración
MONGO_URI = os.environ.get("MONGO_URI")
DB_NAME = "IQscore_DB"
COLLECTION_NAME = "Partidos"

@app.route('/')
def home():
    return "Servicio de scraping y carga a MongoDB"

@app.route('/ejecutar-proceso', methods=['POST'])
def trigger_full_process():
    try:
        # Paso 1: Scraping
        print("Iniciando scraping...")
        procesar_y_guardar_todas_ligas()
        procesar_y_guardar_champions()
        
        # Paso 2: Carga a MongoDB
        print("Cargando a MongoDB...")
        uploader = MongoPartidosUploader(
            uri=MONGO_URI,
            db_name=DB_NAME,
            collection_name=COLLECTION_NAME
        )
        
        uploader.insertar_datos("cuotas_todas_ligas.csv")
        uploader.insertar_datos("cuotas_champions_league.csv", liga="Champions League")
        
        return jsonify({"message": "Proceso completado exitosamente"}), 200
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)