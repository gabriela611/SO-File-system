from cow_file_manager import GestorArchivos

gestor = None

def mostrar_menu():
    print("\n" + "=" * 50)
    print("🧠 Sistema de Archivos Versionado - Menú Principal")
    print("=" * 50)
    print("1. 📂 Abrir o crear archivo")
    print("2. ✏️  Escribir en archivo")
    print("3. 📖 Leer archivo (contenido actual)")
    print("4. 📜 Listar versiones guardadas")
    print("5. ⏪ Rollback backward (retroceder)")
    print("6. ⏩ Rollback forward (avanzar)")
    print("7. 🔍 Ver contenido de una versión específica")
    print("8. ♻️  Restaurar una versión como nueva versión actual")
    print("9. 📤 Exportar una versión a archivo .txt")
    print("10. 🧱 Ver bloques usados por versión")
    print("11. 🚪 Salir")
    print("=" * 50)

while True:
    mostrar_menu()
    opcion = input("Seleccione una opción: ").strip()

    try:
        if opcion == "1":
            ruta = input("📄 Ingrese la ruta o nombre del archivo (ej. archivo.txt): ").strip()
            gestor = GestorArchivos(ruta)
            print(f"✅ Archivo cargado: {ruta}")

        elif opcion == "2":
            if gestor:
                texto = input("✏️ Ingrese el texto que desea escribir: ")
                gestor.escribir(texto)
            else:
                print("⚠️ Primero debe abrir o crear un archivo.")

        elif opcion == "3":
            if gestor:
                gestor.leer()
            else:
                print("⚠️ Primero debe abrir o crear un archivo.")

        elif opcion == "4":
            if gestor:
                gestor.listar_versiones()
            else:
                print("⚠️ Primero debe abrir o crear un archivo.")

        elif opcion == "5":
            if gestor:
                gestor.rollback_backward()
            else:
                print("⚠️ Primero debe abrir o crear un archivo.")

        elif opcion == "6":
            if gestor:
                gestor.rollback_forward()
            else:
                print("⚠️ Primero debe abrir o crear un archivo.")

        elif opcion == "7":
            if gestor:
                vid = input("🔍 Ingrese el ID de la versión que desea ver (ej. v0, v1, etc.): ").strip()
                gestor.recuperar_version(vid)
                gestor.leer()
            else:
                print("⚠️ Primero debe abrir o crear un archivo.")

        elif opcion == "8":
            if gestor:
                vid = input("♻️ Ingrese el ID de la versión que desea restaurar como actual: ").strip()
                gestor.restaurar_version(vid)
            else:
                print("⚠️ Primero debe abrir o crear un archivo.")

        elif opcion == "9":
            if gestor:
                vid = input("📤 Ingrese el ID de la versión a exportar: ").strip()
                destino = input("📁 Ingrese el nombre del archivo de destino (ej. exportado.txt): ").strip()
                contenido = None
                for i, v in enumerate(gestor.inodo["versiones"]):
                    if v["id"] == vid:
                        contenido = gestor._reconstruir_contenido(i)
                        break
                if contenido is not None:
                    with open(destino, "w", encoding="utf-8") as f:
                        f.write(contenido)
                    print(f"✅ Versión {vid} exportada como {destino}")
                else:
                    print(f"❌ No se encontró la versión {vid}")
            else:
                print("⚠️ Primero debe abrir o crear un archivo.")

        elif opcion == "10":
            if gestor:
                gestor.ver_bloques_usados()
            else:
                print("⚠️ Primero debe abrir o crear un archivo.")

        elif opcion == "11":
            print("👋 Saliendo del sistema. ¡Hasta luego!")
            break

        else:
            print("❌ Opción no válida.")

    except Exception as e:
        print(f"🚨 Error: {e}")
