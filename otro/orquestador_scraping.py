import pandas as pd
import os
import contextlib
import io

# Importar funciones de scraping
from scraptoP import procesar_y_guardar_todas_ligas
from scriptlab1 import procesar_y_guardar_champions

# Ejecuta el scraping y muestra solo el contenido de los CSV

def ejecutar_proceso_completo():
    # Scrapear todas las ligas sin imprimir mensajes internos
    buf_all = io.StringIO()
    with contextlib.redirect_stdout(buf_all):
        procesar_y_guardar_todas_ligas()

    # Leer y mostrar datos de todas las ligas
    df_all = pd.read_csv("cuotas_todas_ligas.csv")
    print(df_all.to_string(index=False))

    # Scrapear Champions League sin imprimir mensajes internos
    buf_champs = io.StringIO()
    with contextlib.redirect_stdout(buf_champs):
        procesar_y_guardar_champions()

    # Leer y mostrar datos de Champions League
    df_champs = pd.read_csv("cuotas_champions_league.csv")
    print(df_champs.to_string(index=False))

if __name__ == "__main__":
    ejecutar_proceso_completo()
