import os
import shutil
import json
from datetime import datetime
import hashlib
import docx


class GestorArchivos:
    def __init__(self, ruta_archivo):
        self.ruta_archivo = ruta_archivo
        self.nombre_archivo = os.path.basename(ruta_archivo)
        self.directorio_base = "lavacamu_data"
        self.directorio_archivos = os.path.join(self.directorio_base, "archivos")
        self.directorio_versiones_base = os.path.join(self.directorio_base, "versiones")
        self.directorio_inodos = os.path.join(self.directorio_base, "inodos")
        self.directorio_logs = os.path.join(self.directorio_base, "logs")

        self.inodo_path = os.path.join(self.directorio_inodos, f"{self.nombre_archivo}.json")
        # Cada archivo tendrá su propio subdirectorio de bloques (versiones)
        self.versiones_dir = os.path.join(self.directorio_versiones_base, self.nombre_archivo)
        # Guardamos el log de acciones en el directorio de logs
        self.log_path = os.path.join(self.directorio_logs, f"{self.nombre_archivo}.log")

        self._asegurar_estructura()
        self._cargar_o_crear_inodo()
        # Si es la primera vez que se abre, creamos la versión 0
        if not self.inodo["versiones"]:
            self._crear_version0()

    def _asegurar_estructura(self):
        for d in [self.directorio_base, self.directorio_archivos,
                  self.directorio_versiones_base, self.directorio_inodos,
                  self.directorio_logs, self.versiones_dir]:
            os.makedirs(d, exist_ok=True)

    def _cargar_o_crear_inodo(self):
        if os.path.exists(self.inodo_path):
            with open(self.inodo_path, "r", encoding="utf-8") as f:
                self.inodo = json.load(f)
        else:
            self.inodo = {"nombre": self.nombre_archivo, "versiones": []}
            self._guardar_inodo()
        # Si no se ha registrado la versión actual, se asume que es la última versión (o -1 si no hay ninguna)
        if "current_version" not in self.inodo:
            self.inodo["current_version"] = len(self.inodo["versiones"]) - 1
            self._guardar_inodo()
        self.current_version = self.inodo["current_version"]

    def _guardar_inodo(self):
        with open(self.inodo_path, "w", encoding="utf-8") as f:
            json.dump(self.inodo, f, indent=4)

    def _registrar_log(self, mensaje):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {mensaje}\n")

    def _crear_version0(self):
        # La versión 0 es el estado inicial del archivo.
        extension = os.path.splitext(self.ruta_archivo)[-1].lower()
        if extension == ".txt":
            with open(self.ruta_archivo, "r", encoding="utf-8") as f:
                contenido = f.read()
        elif extension == ".docx":
            try:
                doc = docx.Document(self.ruta_archivo)
                contenido = "\n".join([p.text for p in doc.paragraphs])
            except Exception as e:
                print(f"❌ Error leyendo DOCX: {e}")
                contenido = ""
        else:
            contenido = ""
            # Si el archivo no existe, lo creamos vacío.
            with open(self.ruta_archivo, "w", encoding="utf-8") as f:
                f.write("")
        self._guardar_bloque(contenido, version0=True)
        print("✅ Versión 0 creada.")

    def _guardar_bloque(self, modificacion, version0=False):
        bloques = []
        chunk_size = 4096  # Máximo 4KB por bloque
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for i in range(0, len(modificacion), chunk_size):
            parte = modificacion[i:i + chunk_size]
            nombre_bloque = (
                f"{timestamp}_block{i // chunk_size}.txt"
                if not version0 else f"version0_block{i // chunk_size}.txt"
            )
            path_bloque = os.path.join(self.versiones_dir, nombre_bloque)

            with open(path_bloque, "w", encoding="utf-8") as f:
                f.write(parte)

            bloques.append(path_bloque)

        # Cada versión es una lista de bloques
        self.inodo["versiones"].append(bloques)
        self._actualizar_current_version(len(self.inodo["versiones"]) - 1)
        self._guardar_inodo()
        self._registrar_log(f"📦 Guardó versión con {len(bloques)} bloque(s): {bloques}")

    def _actualizar_current_version(self, new_index):
        self.inodo["current_version"] = new_index
        self.current_version = new_index
        self._guardar_inodo()

    def escribir(self, contenido):
        if not os.path.exists(self.ruta_archivo):
            print("⚠️ El archivo no existe.")
            return

        extension = os.path.splitext(self.ruta_archivo)[-1].lower()
        try:
            if extension == ".txt":
                with open(self.ruta_archivo, "a", encoding="utf-8") as f:
                    f.write(contenido + "\n")
            elif extension == ".docx":
                doc = docx.Document(self.ruta_archivo)
                doc.add_paragraph(contenido)
                doc.save(self.ruta_archivo)
            else:
                print("⚠️ Formato no soportado para escritura.")
                return
            print("✍️ Contenido escrito con éxito.")
            self._registrar_log("✍️ Escribió nuevo contenido.")
            # Guardamos el bloque de la modificación (con salto de línea) dividido en fragmentos de 4KB
            self._guardar_bloque(contenido + "\n")
        except Exception as e:
            print(f"❌ Error al escribir: {e}")

    def _reconstruir_contenido(self, hasta_version):
        contenido_total = ""
        # Concatenamos los bloques de la versión 0 hasta 'hasta_version'
        for lista_bloques in self.inodo["versiones"][:hasta_version + 1]:
            for block_path in lista_bloques:
                if os.path.exists(block_path):
                    with open(block_path, "r", encoding="utf-8") as f:
                        contenido_total += f.read()
        return contenido_total

    def leer(self):
        contenido_total = self._reconstruir_contenido(self.current_version)
        print("\n📄 Contenido concatenado desde la versión 0 hasta la actual:\n")
        print(contenido_total)

    def listar_versiones(self):
        if self.inodo["versiones"]:
            print("📜 Bloques (versiones) guardadas:")
            for i, bloques in enumerate(self.inodo["versiones"], 1):
                print(f"{i}. {bloques}")
            print(f"\nBloque actual: {self.current_version + 1}")
        else:
            print("⚠️ No hay bloques (versiones) guardadas.")

    def rollback_backward(self):
        # Retrocede a la versión anterior (más antigua)
        if self.current_version > 0:
            self._actualizar_current_version(self.current_version - 1)
            contenido_total = self._reconstruir_contenido(self.current_version)
            extension = os.path.splitext(self.ruta_archivo)[-1].lower()
            try:
                if extension == ".txt":
                    with open(self.ruta_archivo, "w", encoding="utf-8") as f:
                        f.write(contenido_total)
                elif extension == ".docx":
                    doc = docx.Document()
                    doc.add_paragraph(contenido_total)
                    doc.save(self.ruta_archivo)
                print(f"🔄 Rollback backward a la versión {self.current_version + 1} realizado con éxito.")
                self._registrar_log(f"🔄 Rollback backward a versión {self.current_version + 1}.")
            except Exception as e:
                print(f"❌ Error en rollback backward: {e}")
        else:
            print("⚠️ Ya estás en la versión más antigua.")

    def rollback_forward(self):
        # Avanza a la siguiente versión (más reciente)
        if self.current_version < len(self.inodo["versiones"]) - 1:
            self._actualizar_current_version(self.current_version + 1)
            contenido_total = self._reconstruir_contenido(self.current_version)
            extension = os.path.splitext(self.ruta_archivo)[-1].lower()
            try:
                if extension == ".txt":
                    with open(self.ruta_archivo, "w", encoding="utf-8") as f:
                        f.write(contenido_total)
                elif extension == ".docx":
                    doc = docx.Document()
                    doc.add_paragraph(contenido_total)
                    doc.save(self.ruta_archivo)
                print(f"🔄 Rollback forward a la versión {self.current_version + 1} realizado con éxito.")
                self._registrar_log(f"🔄 Rollback forward a versión {self.current_version + 1}.")
            except Exception as e:
                print(f"❌ Error en rollback forward: {e}")
        else:
            print("⚠️ Ya estás en la versión más reciente.")

    def guardar_version(self):
        # Método de compatibilidad; en este sistema se guarda por bloques
        self._guardar_version()
