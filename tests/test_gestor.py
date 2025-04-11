import os
import shutil
import pytest
from src.cow_file_manager.cow_file_manager import GestorArchivos

# Configuración de test
TEST_DIR = "test_lavacamu_data"
TEST_FILE = "testfile.bin"
TEST_PATH = os.path.join(TEST_DIR, TEST_FILE)

@pytest.fixture
def gestor():
    # Antes de cada test: preparar entorno limpio
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR, exist_ok=True)

    g = GestorArchivos(TEST_PATH)
    yield g

    # Después de cada test: limpiar entorno
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

def test_create_file(gestor):
    gestor.create()
    assert os.path.exists(gestor.ruta_archivo)
    assert os.path.exists(gestor.inodo_path)
    assert os.path.exists(gestor.versiones_dir)

def test_write_and_version(gestor):
    gestor.create()
    gestor.write("Hola mundo!")
    assert len(gestor.inodo["versiones"]) == 1

def test_read_latest_version(gestor):
    gestor.create()
    gestor.write("Lectura de prueba")
    gestor.read()
    assert gestor.current_version == 0

def test_list_versions(gestor, capsys):
    gestor.create()
    gestor.write("Versión uno")
    gestor.listar_versiones()
    captured = capsys.readouterr()
    assert "Versión actual activa" in captured.out

def test_memory_usage(gestor, capsys):
    gestor.create()
    gestor.write("Datos para medir memoria")
    gestor.mostrar_uso_memoria()
    captured = capsys.readouterr()
    assert "Uso de memoria" in captured.out

def test_collect_orphan_blocks(gestor, capsys):
    gestor.create()
    gestor.write("Version uno")
    gestor.write("Version dos")

    # Eliminar la primera versión para simular bloques huérfanos
    gestor.inodo["versiones"] = gestor.inodo["versiones"][1:]
    gestor._guardar_inodo()

    gestor.recolectar_bloques_huerfanos()
    captured = capsys.readouterr()
    assert "bloques huérfanos" in captured.out

def test_close_file(gestor):
    gestor.create()
    gestor.write("Cerrar test")
    gestor.close()
    assert gestor.ruta_archivo is None
    assert gestor.nombre_archivo is None
    assert gestor.inodo is None
    assert gestor.current_version == -1