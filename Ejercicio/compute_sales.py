"""
Docstring for compute_sales
"""
from pathlib import Path
import os
import sys
import time
import json
from collections import defaultdict


def leer_archivo(ruta_archivo):
    """Metodo para leer un archivo JSON"""
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, PermissionError, OSError) as e:
        print(f"[ERROR] no puede leer el archivo {ruta_archivo}: {e}")
        return None


def generar_indice_precio(datos_productos):
    """Metodo para generar la lista de indice de precios"""
    price_index = {}

    for item in datos_productos:
        try:
            title = item["title"]
            price = float(item["price"])
            price_index[title] = price
        except (IndexError, ValueError) as e:
            print(f"[WARNING] Producto invalido: {item} -> {e}")

    return price_index


def procesar_ventas(sales, price_index):
    """Metodo para procesar las ventas y sus totales"""
    ventas_totales = defaultdict(float)
    total_suma = 0.0
    total_restar = 0.0
    for record in sales:
        try:
            sale_id = record["SALE_ID"]
            product = record["Product"]
            quantity = float(record["Quantity"])

            if product not in price_index:
                restar = price_index[product] * quantity
                total_restar += restar
                raise ValueError('Producto no encontrado.')

            if quantity <= 0:
                restar = price_index[product] * quantity
                total_restar += (-1) * restar
                raise ValueError('Valor negativo para la cantidad.')

            cost = price_index[product] * quantity
            ventas_totales[sale_id] += cost
            total_suma += cost
        except (IndexError, ValueError) as e:
            print(f"[WARNING] Registro de venta invalido: {record} -> {e}")

    total_suma = total_suma - total_restar
    return ventas_totales, total_suma


def generar_resultado(ventas_totales, total_general, tiempo_ejecucion):
    """Metodo para generar el resultado a imprimir"""
    lines = []
    lines.append("RESUMEN DE VENTAS")
    lines.append("=" * 40)

    for sale_id in sorted(ventas_totales.keys()):
        lines.append(f"Sale ID {sale_id:>3} : ${ventas_totales[sale_id]:,.2f}")

    lines.append("=" * 40)
    lines.append(f"COSTO TOTAL DE VENTAS : ${total_general:,.2f}")
    lines.append(f"TIEMPO DE EJECUCION   : {tiempo_ejecucion:.4f} seconds")

    return "\n".join(lines)


def registrar_resultado(lista_resultados):
    """Metodo para registrar los resultados en un archivo"""
    # Definir la ruta del archivo dentro del contenedor
    # Nota: /app/datos es el volumen que mapearemos
    output_dir = "/app/datos"
    filename = os.path.join(output_dir, "SalesResults.txt")

    # Crear el directorio si no existe
    os.makedirs(output_dir, exist_ok=True)

    # Escribir valores
    with open(filename, "w", encoding="utf-8") as archivo_resultado:
        archivo_resultado.write(f"{lista_resultados}\n")


script_location = Path(__file__).parent
ARCHIVO_PRODUCTOS = 'price_catalogue.json'
ARCHIVO_VENTAS = 'sales_record.json'

file_location = script_location / ARCHIVO_PRODUCTOS
print(file_location)

start_time = time.time()

productos = leer_archivo(file_location)
file_location = script_location / ARCHIVO_VENTAS
print(file_location)
ventas = leer_archivo(file_location)

if productos is None or ventas is None:
    print("[ERROR] Ejecución cancelada debido a errores del archivo.")
    sys.exit(1)

indices_precios = generar_indice_precio(productos)
sales_totals, grand_total = procesar_ventas(ventas, indices_precios)
elapsed_time = time.time() - start_time
RESULTS = generar_resultado(sales_totals, grand_total, elapsed_time)
print("\n" + RESULTS)
registrar_resultado(RESULTS)
