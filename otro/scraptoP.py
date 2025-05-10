import requests
import pandas as pd
import time
import os # Para la API Key

# Es mejor obtener la API key de una variable de entorno
API_KEY = os.environ.get('THE_ODDS_API_KEY', '3140160b8ddbab8f063b58b9b1817cc8')

LIGAS_CONFIG = {
    "Liga serie A": "soccer_italy_serie_a",
    "Premier League": "soccer_epl",
    "LaLiga": "soccer_spain_la_liga",
    "Ligue 1": "soccer_france_ligue_one"
}

def obtener_datos_liga(nombre_liga, id_liga, api_key_param):
    print(f"📌 Obteniendo datos de {nombre_liga}...")
    url = f'https://api.the-odds-api.com/v4/sports/{id_liga}/odds/?apiKey={api_key_param}&regions=eu&markets=h2h&oddsFormat=decimal'
    partidos_data = []
    for intento in range(3):
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
                                        'Liga': nombre_liga,
                                        'Equipo 1': cuotas[0]['name'],
                                        'Cuota 1': cuotas[0]['price'],
                                        'Equipo 2': cuotas[1]['name'],
                                        'Cuota 2': cuotas[1]['price'],
                                        'Empate': cuotas[2]['price'],
                                        'Casa de Apuestas': bookie['title'],
                                        'Fecha': evento['commence_time']
                                    }
                                    partidos_data.append(partido)
                return partidos_data # Devuelve los datos en lugar de construir el DataFrame aquí
            else:
                print(f"⚠️ Error al obtener datos de {nombre_liga}: {response.status_code}")
                break # Salir si hay un error de status code
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error de conexión para {nombre_liga}: {e}. Reintentando...")
            time.sleep(5)
    return partidos_data # Devuelve lista vacía si falla

def procesar_y_guardar_todas_ligas(nombre_archivo_csv="cuotas_todas_ligas.csv"):
    todos_los_partidos_acumulados = []
    for nombre_liga, id_liga in LIGAS_CONFIG.items():
        datos_de_liga = obtener_datos_liga(nombre_liga, id_liga, API_KEY)
        if datos_de_liga:
            todos_los_partidos_acumulados.extend(datos_de_liga)

    if not todos_los_partidos_acumulados:
        print("⚠️ No se obtuvieron datos para ninguna liga principal.")
        return False

    df = pd.DataFrame(todos_los_partidos_acumulados)
    df.to_csv(nombre_archivo_csv, index=False)
    print(f"✅ Datos de ligas principales guardados en '{nombre_archivo_csv}'")
    return True

if __name__ == "__main__":
    # Esto es para que puedas ejecutar este script directamente para probarlo
    procesar_y_guardar_todas_ligas()