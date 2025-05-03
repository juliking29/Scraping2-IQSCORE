import os
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup

# Variables constantes
url = "https://scores24.live/es/soccer/l-spain-laliga/predictions"
CARPETA_TRABAJO = "."  # Cambia a tu carpeta específica si es necesario

# Limpieza inicial: eliminar archivos .txt y .csv
def limpiar_archivos(ruta_carpeta):
    for archivo in os.listdir(ruta_carpeta):
        if archivo.endswith(".txt") or archivo.endswith(".csv"):
            os.remove(os.path.join(ruta_carpeta, archivo))

# Obtener HTML desde URL
def obtener_html(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

# Guardar scripts extraídos del HTML en un archivo
def guardar_scripts(html, ruta_archivo):
    soup = BeautifulSoup(html, 'html.parser')
    scripts = soup.find_all('script')

    with open(ruta_archivo, "w", encoding="utf-8") as archivo:
        for script in scripts:
            archivo.write(script.string if script.string else "Script vacío\n")
            archivo.write("\n")

# Extraer datos JSON válidos desde archivo
def extraer_json_valido(ruta_archivo):
    with open(ruta_archivo, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Buscar la línea que contiene la información relevante
    linea_json = next((line for line in lines if 'window.URQL_DATA=JSON.parse(' in line), None)

    if not linea_json:
        raise ValueError("No se encontró JSON.parse en los datos proporcionados.")

    # Extraer el JSON dentro del JSON.parse(...)
    contenido_json = linea_json.split('JSON.parse("')[1].rstrip('")\n;')
    contenido_json = contenido_json.encode('utf-8').decode('unicode_escape')

    # Ahora sí cargamos el contenido como JSON válido
    json_data = json.loads(contenido_json)

    # Extraer el sub-JSON que contiene 'TournamentPrediction'
    for key, value in json_data.items():
        data = json.loads(value['data'])
        if 'TournamentPrediction' in data:
            return data

    raise ValueError("No se encontró 'TournamentPrediction' en los datos proporcionados.")

# Extraer información del JSON


def extraer_informacion(json_data):
    resultados = []

    # Navegar correctamente el JSON real
    tournament_prediction = json_data.get("TournamentPrediction", {})
    upcoming_matches = tournament_prediction.get("upcoming", {}).get("items", [])

    for match_info in upcoming_matches:
        prediction_type, prediction_detail = match_info.get("prediction", ["N/A", "N/A"])
        prediction_value = match_info.get("predictionValue", "N/A")
        match = match_info.get("match", {})
        match_date = match.get("matchDate", "N/A")
        teams = match.get("teams", [])

        if len(teams) == 2:
            equipo1 = teams[0]["name"]
            equipo2 = teams[1]["name"]
        else:
            equipo1 = equipo2 = "N/A"

        resultados.append({
            "Fecha": match_date,
            "Equipo Local": equipo1,
            "Equipo Visitante": equipo2,
            "Tipo Predicción": prediction_type,
            "Detalle Predicción": prediction_detail,
            "Cuota": prediction_value
        })

    return resultados


# Guardar resultados en CSV
def guardar_resultados(resultados, ruta_csv):
    df = pd.DataFrame(resultados)
    df.to_csv(ruta_csv, index=False, encoding="utf-8")

# Función principal
def main():
    limpiar_archivos(CARPETA_TRABAJO)

    html = obtener_html(url)
    ruta_scripts = os.path.join(CARPETA_TRABAJO, "scripts_extraidos.txt")

    guardar_scripts(html, ruta_scripts)

    json_data = extraer_json_valido(ruta_scripts)
    resultados = extraer_informacion(json_data)

    ruta_csv = os.path.join(CARPETA_TRABAJO, "resultados_predicciones.csv")
    guardar_resultados(resultados, ruta_csv)

    print(f"Extracción completada y guardada en '{ruta_csv}'")

# Ejecución
if __name__ == "__main__":
    main()
