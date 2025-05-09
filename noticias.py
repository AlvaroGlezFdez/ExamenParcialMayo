import asyncio
import aiohttp
import json
import logging

# Configuramos los logs para que muestre mensajes con hora, nivel y texto
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Clase Worker: representa una fuente de datos externa
class Worker:
    def __init__(self, url, session, nombre):
        self.url = url            # URL de la API
        self.session = session    # Sesión HTTP compartida (para eficiencia)
        self.nombre = nombre      # Nombre descriptivo de la fuente

    # Método asíncrono que obtiene los datos de la fuente
    async def obtener_datos(self):
        try:
            async with self.session.get(self.url, timeout=10) as resp:
                texto = await resp.text()  # Leemos el texto de la respuesta
                return self.estandarizar(texto)  # Lo pasamos al método que lo formatea
        except Exception as e:
            logging.warning(f"[{self.nombre}] Error accediendo a {self.url}: {e}")
            return None  # Si falla, devolvemos None

    # Método que transforma los datos al formato común (título, fecha, contenido)
    def estandarizar(self, texto):
        try:
            data = json.loads(texto)  # Intentamos convertir el texto en JSON

            # Si la fuente es Binance (Bitcoin)
            if self.nombre == "Bitcoin":
                precio = data["price"]
                return {
                    "titulo": "Precio actual del Bitcoin",
                    "fecha": "desconocida",
                    "contenido": f"El precio actual del Bitcoin es {precio} USD."
                }

            # Si la fuente es Blockchain.info
            elif self.nombre == "Blockchain":
                return {
                    "titulo": "Estadísticas de la red Blockchain",
                    "fecha": "desconocida",
                    "contenido": f"Hash rate: {data.get('hash_rate')} H/s, Transacciones hoy: {data.get('n_tx')}"
                }

            # Si es otra fuente desconocida
            else:
                return {
                    "titulo": "Dato desconocido",
                    "fecha": "desconocida",
                    "contenido": str(data)
                }

        # Si la respuesta no es JSON válido
        except json.JSONDecodeError:
            logging.error(f"[{self.nombre}] Respuesta no es JSON válido.")
            return None

        # Si falla cualquier otra cosa al formatear
        except Exception as e:
            logging.error(f"[{self.nombre}] Error al estandarizar datos: {e}")
            return None

# Simula el envío de artículos a un servidor central (en este caso solo imprime)
async def enviar_al_servidor_central(articulos):
    logging.info(f"Enviando {len(articulos)} artículos al servidor central...")
    for articulo in articulos:
        logging.info(f"Artículo → {articulo['titulo']}: {articulo['contenido']}")

# Función principal que ejecuta todo el flujo
async def main():
    # Lista de fuentes: tuplas con URL y nombre
    fuentes = [
        ("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", "Bitcoin"),
        ("https://api.blockchain.info/stats", "Blockchain")
    ]

    # Creamos una sesión HTTP compartida
    async with aiohttp.ClientSession() as session:
        # Creamos un Worker para cada fuente
        workers = [Worker(url, session, nombre) for url, nombre in fuentes]

        # Lanzamos todas las tareas al mismo tiempo con asyncio.gather
        tareas = [worker.obtener_datos() for worker in workers]
        resultados = await asyncio.gather(*tareas, return_exceptions=True)

        # Filtramos los resultados válidos
        articulos = [r for r in resultados if isinstance(r, dict)]
        logging.info(f"Se recolectaron {len(articulos)} artículos")

        # Enviamos (imprimimos) los artículos recolectados
        if articulos:
            await enviar_al_servidor_central(articulos)

# Ejecutamos la función principal si este archivo es el principal
if __name__ == "__main__":
    asyncio.run(main())


# Al comenzar el desarrollo, intentamos utilizar la API de CoinDesk para obtener el precio actual del Bitcoin, 
# pero se produjo un error relacionado con la resolución del dominio (getaddrinfo failed), probablemente causado 
# por restricciones de red, DNS o bloqueo del dominio en el entorno de ejecución.

# Luego se probó con la API de CoinCap, pero la respuesta no era un JSON válido, lo que provocaba errores de parseo 
# con json.loads(). Por estos motivos, se optó por reemplazar ambas fuentes por la API pública de Binance, 
# que proporciona el precio del Bitcoin en dólares estadounidenses sin necesidad de clave de acceso y con estructura clara.

# También se había considerado usar una API sobre inflación en España (API-Ninjas), pero fue descartada porque requería 
# registro y clave, lo cual complicaba la ejecución directa sin configuraciones externas.

# Por otro lado, se desarrolló una clase llamada Worker para encapsular el comportamiento de cada fuente de datos, 
# lo cual permitió modularizar el sistema, facilitar la concurrencia con asyncio y hacer el sistema fácilmente escalable. 

# La asincronía se gestionó con asyncio y aiohttp, logrando eficiencia en la obtención concurrente de datos sin uso de 
# hilos ni procesos adicionales. Además, el sistema fue diseñado con tolerancia a fallos: si una fuente no responde, 
# las demás continúan funcionando con normalidad.

# De esta forma, se logró construir un sistema distribuido funcional, robusto y adaptado al contexto de un análisis 
# financiero en tiempo real.
