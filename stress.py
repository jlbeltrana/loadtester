import asyncio
import aiohttp
import time
import csv
from rich.live import Live
from rich.table import Table
from rich.console import Console

def obtener_entrada(mensaje, tipo=int):
    while True:
        try:
            valor = tipo(input(mensaje).strip())
            if tipo == int and valor <= 0:
                raise ValueError("El valor debe ser mayor a 0.")
            return valor
        except ValueError as e:
            console.print(f"[red]Entrada inválida:[/red] {e}")

console = Console()

url = input("🌐 Ingresa la URL a testear (ej: https://page.com/api): ").strip()
TOTAL_REQUESTS = obtener_entrada("🔢 Total de requests (ej: 1000): ")
CONCURRENT_TASKS = obtener_entrada("⚙️  Nivel de concurrencia (ej: 100): ")

metrics = {
    "success": 0,
    "errors": 0,
    "response_times": [],
}

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
    except aiohttp.ClientError as e:
        metrics["errors"] += 1
        console.print(f"[red]Error en la request {i}: {e}[/red]")
    except asyncio.TimeoutError:
        metrics["errors"] += 1
        console.print(f"[red]Timeout en la request {i}[/red]")

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

def guardar_resultados_csv():
    with open("resultados.csv", "w", newline="") as csvfile:
        fieldnames = ["Métrica", "Valor"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        total = metrics["success"] + metrics["errors"]
        avg_time = sum(metrics["response_times"]) / len(metrics["response_times"]) if metrics["response_times"] else 0
        writer.writerow({"Métrica": "Requests Totales", "Valor": total})
        writer.writerow({"Métrica": "Exitosos", "Valor": metrics["success"]})
        writer.writerow({"Métrica": "Errores", "Valor": metrics["errors"]})
        writer.writerow({"Métrica": "Tiempo Promedio", "Valor": f"{avg_time:.3f}s"})

async def main():
    queue = asyncio.Queue()
    for i in range(TOTAL_REQUESTS):
        queue.put_nowait(i)

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        tasks = [asyncio.create_task(worker(queue, session)) for _ in range(CONCURRENT_TASKS)]
        
        # Actualizar tabla en paralelo mientras los workers corren
        with Live(generar_tabla(), refresh_per_second=2) as live:
            while any(not t.done() for t in tasks):
                live.update(generar_tabla())
                await asyncio.sleep(0.5)
            await asyncio.gather(*tasks)
            live.update(generar_tabla())  # Actual final

    guardar_resultados_csv()
    console.print("[green]Resultados guardados en 'resultados.csv'[/green]")

if __name__ == "__main__":
    asyncio.run(main())
