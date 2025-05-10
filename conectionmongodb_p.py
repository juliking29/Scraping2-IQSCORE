from pymongo import MongoClient
import pandas as pd

class MongoPartidosUploader:
    def __init__(self, uri, db_name, collection_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insertar_datos(self, csv_file, liga=None):
        df = pd.read_csv(csv_file)

        # Renombrar columnas para que coincidan con el validador de MongoDB
        df = df.rename(columns={
            'Liga': 'liga',
            'Equipo 1': 'equipo_1',
            'Cuota 1': 'cuota_1',
            'Equipo 2': 'equipo_2',
            'Cuota 2': 'cuota_2',
            'Empate': 'empate',
            'Casa de Apuestas': 'casa_de_apuestas',
            'Fecha': 'fecha'
        })

        # Convertir la columna 'fecha' a datetime
        df['fecha'] = pd.to_datetime(df['fecha'])

        # Si se pasa el parámetro liga, sobrescribe la columna
        if liga:
            df['liga'] = liga

        # Convertir a diccionario
        datos = df.to_dict(orient="records")

        # Insertar en MongoDB
        self.collection.insert_many(datos)
        print(f"Datos de {csv_file} insertados en MongoDB.")

if __name__ == "__main__":
    uploader = MongoPartidosUploader(
        uri="mongodb+srv://julichavez06admin:AESPA17king@mongodb101.jlpx2.mongodb.net/IQscore_DB?retryWrites=true&w=majority&appName=MongoDB101",
        db_name="IQscore_DB",
        collection_name="Partidos"
    )

    # Insertar partidos de todas las ligas
    uploader.insertar_datos("cuotas_todas_ligas.csv")

    # Insertar partidos de Champions League
    uploader.insertar_datos("cuotas_champions_league.csv", liga="Champions League")

    print("Inserción completada.")