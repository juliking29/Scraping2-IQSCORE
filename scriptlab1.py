import requests
import pandas as pd
import os # Para la API Key

API_KEY = os.environ.get('THE_ODDS_API_KEY', '3140160b8ddbab8f063b58b9b1817cc8')

def obtener_datos_champions(api_key_param):
    print(f"📌 Obteniendo datos de Champions League...")
    url = f'https://api.the-odds-api.com/v4/sports/soccer_uefa_champs_league/odds/?apiKey={api_key_param}&regions=eu&markets=h2h&oddsFormat=decimal'
    partidos_data = []
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for evento in data:
                for bookie in evento['bookmakers']:
                    for market in bookie['markets']:
                        if market['key'] == 'h2h':
                            cuotas = market['outcomes']
                            if len(cuotas) == 3:
                                partido = {
                                    # 'Liga': 'Champions League', # El uploader puede manejar esto
                                    'Equipo 1': cuotas[0]['name'],
                                    'Cuota 1': cuotas[0]['price'],
                                    'Equipo 2': cuotas[1]['name'],
                                    'Cuota 2': cuotas[1]['price'],
                                    'Empate': cuotas[2]['price'],
                                    'Casa de Apuestas': bookie['title'],
                                    'Fecha': evento['commence_time']
                                }
                                partidos_data.append(partido)
            return partidos_data
        else:
            print(f'⚠️ Error al obtener datos de Champions: {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error de conexión para Champions League: {e}.")
    return partidos_data

def procesar_y_guardar_champions(nombre_archivo_csv="cuotas_champions_league.csv"):
    datos_champions = obtener_datos_champions(API_KEY)

    if not datos_champions:
        print("⚠️ No se obtuvieron datos para Champions League.")
        return False

    df = pd.DataFrame(datos_champions)
    df.to_csv(nombre_archivo_csv, index=False)
    print(f"✅ Datos de Champions League guardados en '{nombre_archivo_csv}'")
    return True

if __name__ == "__main__":
    procesar_y_guardar_champions()