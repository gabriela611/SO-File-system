import os
import shutil
import time
from src.cow_file_manager.cow_file_manager import GestorArchivos

# Configuración de benchmark
TEST_DIR = "benchmark_data"
TEST_FILE = "benchmark_file.bin"
TEST_PATH = os.path.join(TEST_DIR, TEST_FILE)

def preparar_archivo():
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR, exist_ok=True)
    gestor = GestorArchivos(TEST_PATH)
    gestor.create()
    return gestor

def benchmark_escritura(gestor, tamano_mb):
    data = os.urandom(tamano_mb * 1024 * 1024)  # Datos aleatorios
    start = time.perf_counter()
    gestor.write(data)
    end = time.perf_counter()
    tiempo = end - start
    velocidad = tamano_mb / tiempo
    print(f"📝 Escritura de {tamano_mb} MB: {tiempo:.4f} s ({velocidad:.2f} MB/s)")
    return tiempo

def benchmark_lectura(gestor):
    start = time.perf_counter()
    gestor.read()
    end = time.perf_counter()
    tiempo = end - start
    print(f"📖 Lectura última versión: {tiempo:.4f} s")
    return tiempo

def main():
    tamanos_mb = [1, 5, 10]  # Tamaños en MB
    for tamano in tamanos_mb:
        print(f"\n🚀 Benchmark para {tamano} MB")
        gestor = preparar_archivo()
        benchmark_escritura(gestor, tamano)
        benchmark_lectura(gestor)
        gestor.close()

    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    print("\n✅ Benchmark finalizado.")

if __name__ == "__main__":
    main()
