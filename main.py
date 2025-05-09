import asyncio
import aiohttp
import json
import logging

# Configuración de logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class Worker:
    def __init__(self, url, session, nombre):
        self.url = url
        self.session = session
        self.nombre = nombre

    async def obtener_datos(self):
        try:
            async with self.session.get(self.url, timeout=10) as resp:
                texto = await resp.text()
                return self.estandarizar(texto)
        except Exception as e:
            logging.warning(f"[{self.nombre}] Error accediendo a {self.url}: {e}")
            return None

    def estandarizar(self, texto):
        try:
            data = json.loads(texto)

            if self.nombre == "Bitcoin":
                precio = data["price"]
                return {
                    "titulo": "Precio actual del Bitcoin",
                    "fecha": "desconocida",
                    "contenido": f"El precio actual del Bitcoin es {precio} USD."
                }

            elif self.nombre == "Blockchain":
                return {
                    "titulo": "Estadísticas de la red Blockchain",
                    "fecha": "desconocida",
                    "contenido": f"Hash rate: {data.get('hash_rate')} H/s, Transacciones hoy: {data.get('n_tx')}"
                }

            else:
                return {
                    "titulo": "Dato desconocido",
                    "fecha": "desconocida",
                    "contenido": str(data)
                }

        except json.JSONDecodeError:
            logging.error(f"[{self.nombre}] Respuesta no es JSON válido.")
            return None
        except Exception as e:
            logging.error(f"[{self.nombre}] Error al estandarizar datos: {e}")
            return None

async def enviar_al_servidor_central(articulos):
    logging.info(f"Enviando {len(articulos)} artículos al servidor central...")
    for articulo in articulos:
        logging.info(f"Artículo → {articulo['titulo']}: {articulo['contenido']}")

async def main():
    fuentes = [
        ("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", "Bitcoin"),
        ("https://api.blockchain.info/stats", "Blockchain")
    ]

    async with aiohttp.ClientSession() as session:
        workers = [Worker(url, session, nombre) for url, nombre in fuentes]
        tareas = [worker.obtener_datos() for worker in workers]
        resultados = await asyncio.gather(*tareas, return_exceptions=True)

        articulos = [r for r in resultados if isinstance(r, dict)]
        logging.info(f"Se recolectaron {len(articulos)} artículos")

        if articulos:
            await enviar_al_servidor_central(articulos)

if __name__ == "__main__":
    asyncio.run(main())

