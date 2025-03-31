# 🧪 LoadTester

Herramienta interactiva de carga HTTP escrita en Python, ideal para testear APIs y visualizar métricas en tiempo real directamente desde la terminal con ayuda de `rich`.

---

## 🚀 ¿Qué hace?

Este contenedor ejecuta un script en Python que:

- Solicita:
  - La URL del servicio a testear.
  - La cantidad total de requests.
  - El nivel de concurrencia.
- Envía múltiples requests usando `aiohttp` de forma asíncrona.
- Muestra en consola:
  - Total de requests enviados.
  - Éxitos y errores.
  - Tiempo promedio de respuesta.
- Todo se actualiza dinámicamente gracias a `rich`.

---

## 🐳 Uso con Docker

Podés ejecutarlo directamente sin necesidad de clonar el repo:

```bash
sudo docker run --pull always -it --rm jlbeltrana/loadtester:latest

## Ejemplo interactivo

🌐 Ingresa la URL a testear (ej: https://page.com/api): https://api.midominio.com/health
🔢 Total de requests (ej: 1000): 500
⚙️  Nivel de concurrencia (ej: 100): 50

## Construir localmente

docker build -t loadtester .
docker run -it --rm loadtester
