from bs4 import BeautifulSoup
import requests
import json
import pandas as pd

# Obtener el HTML de la página
url = "https://scores24.live/es/soccer/l-primera-a-clausura/predictions"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Buscar todas las etiquetas <script>
scripts = soup.find_all('script')

# Crear y escribir en el archivo
with open("scripts_extraidos.txt", "w") as archivo:
    for script in scripts:
        archivo.write(script.string if script.string else "Script vacío\n")
        archivo.write("\n") 
# Ruta al archivo JSON
ruta_archivo = "scripts_extraidos.txt"

# Leer contenido del archivo
with open(ruta_archivo, "r", encoding="utf-8") as file:
    contenido = file.read()

# Procesamiento del contenido para extraer JSON válido
contenido_json = contenido.split('JSON.parse("')[1].rstrip('")')
contenido_json = contenido_json.encode().decode('unicode_escape')

# Encontrar los límites exactos del JSON
inicio_json = contenido_json.find('{')
fin_json = contenido_json.rfind('}') + 1
contenido_json = contenido_json[inicio_json:fin_json]

# Convertir a JSON
datos_json = json.loads(contenido_json)

data = json.loads(datos_json["2802543787"]["data"])

# Lista para almacenar los resultados
resultados = []

# Recorrer y extraer información
for trend in data["TrendList"]:
    for grupo in trend["groups"]:
        for tendencia in grupo["trends"]:
            prediccion = tendencia.get("prediction", {})
            for grouped_fact in tendencia["groupedFacts"]:
                for fact in grouped_fact["facts"]:
                    resultados.append({
                        "Título": grouped_fact["title"],
                        "Texto": fact["text"],
                        "Tipo": fact["type"],
                        "Equipo": fact["team"]["name"],
                        "Tipo Predicción": prediccion.get("type", ["N/A"])[0],
                        "Detalle Predicción": prediccion.get("type", ["N/A", "N/A"])[1] if len(prediccion.get("type", [])) > 1 else "N/A",
                        "Cuota": prediccion.get("value", "N/A"),
                       # "Bookmaker": tendencia["bookmaker"]["name"]
                    })

# Convertir resultados en DataFrame
df_resultados = pd.DataFrame(resultados)

# Guardar DataFrame en un archivo CSV
df_resultados.to_csv("resultados_predicciones.csv", index=False, encoding="utf-8")

print("Extracción completada y guardada en 'resultados_predicciones.csv'")
