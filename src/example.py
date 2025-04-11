from cow_file_manager.cow_file_manager import GestorArchivos

# Ejemplo de uso básico de la librería

def main():
    ruta = "ejemplo_archivo.bin"
    gestor = GestorArchivos(ruta)

    print("\n✨ Creando archivo...")
    gestor.create()

    print("\n✏️ Escribiendo datos...")
    gestor.write("Hola, este es un archivo versionado!")

    print("\n📖 Leyendo última versión...")
    gestor.read()

    print("\n📜 Listando versiones...")
    gestor.listar_versiones()

    print("\n📊 Mostrando uso de memoria...")
    gestor.mostrar_uso_memoria()

    print("\n🔒 Cerrando archivo...")
    gestor.close()

if __name__ == "__main__":
    main()
