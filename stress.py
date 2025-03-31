import asyncio
import aiohttp
import time
from rich.live import Live
from rich.table import Table
from rich.console import Console

url = input("🌐 Ingresá la URL a testear (ej: https://tuservidor.com/api): ").strip()

# Configuración
TOTAL_REQUESTS = 1000
CONCURRENT_TASKS = 100

metrics = {
    "success": 0,
    "errors": 0,
    "response_times": [],
}

console = Console()

async def fetch(session, i):
    inicio = time.time()
    try:
        async with session.get(url) as response:
            duracion = time.time() - inicio
            if response.status == 200:
                metrics["success"] += 1
            else:
                metrics["errors"] += 1
            metrics["response_times"].append(duracion)
    except Exception:
        metrics["errors"] += 1

async def worker(queue, session):
    while not queue.empty():
        i = await queue.get()
        await fetch(session, i)
        queue.task_done()

def generar_tabla():
    table = Table(title="📊 Simulador de Carga", expand=True)
    table.add_column("Métrica", justify="left", style="cyan")
    table.add_column("Valor", justify="right", style="magenta")

    total = metrics["success"] + metrics["errors"]
    avg_time = sum(metrics["response_times"]) / len(metrics["response_times"]) if metrics["response_times"] else 0
    table.add_row("Requests Totales", str(total))
    table.add_row("Exitosos", str(metrics["success"]))
    table.add_row("Errores", str(metrics["errors"]))
    table.add_row("Tiempo Promedio", f"{avg_time:.3f}s")

    return table

async def main():
    queue = asyncio.Queue()
    for i in range(TOTAL_REQUESTS):
        queue.put_nowait(i)

    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(worker(queue, session)) for _ in range(CONCURRENT_TASKS)]
        
        # Actualizar tabla en paralelo mientras los workers corren
        with Live(generar_tabla(), refresh_per_second=2) as live:
            while any(not t.done() for t in tasks):
                live.update(generar_tabla())
                await asyncio.sleep(0.5)
            await asyncio.gather(*tasks)
            live.update(generar_tabla())  # Actual final

if __name__ == "__main__":
    asyncio.run(main())
