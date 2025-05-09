# ExamenParcialMayo

# Sistema de Adquisición de Datos Económicos en Tiempo Real

## ¿Qué hace este programa?

Este programa obtiene información económica en tiempo real desde dos fuentes públicas:

- Precio actual del Bitcoin (en USD) desde la API de Binance.
- Estadísticas de la red Blockchain, como hash rate y número de transacciones, desde Blockchain.info.

Utiliza programación asíncrona con asyncio y aiohttp para consultar ambas fuentes al mismo tiempo sin bloquear la ejecución.

---

## ¿Cómo funciona?

- Se define una clase Worker, que representa cada fuente de datos.
- Cada Worker descarga la información y la transforma a un formato común (título, fecha y contenido).
- Se ejecutan todos los Worker a la vez usando asyncio.gather().
- Una vez recolectados los datos, se imprimen por consola simulando el envío a un servidor.


