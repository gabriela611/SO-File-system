from cow_file_manager import GestorArchivos

gestor = None

while True:
    print("\nMenú:")
    print("1. Abrir o crear archivo")
    print("2. Escribir en archivo")
    print("3. Leer archivo (mostrar concatenación de bloques)")
    print("4. Listar bloques (versiones)")
    print("5. Rollback backward (retroceder)")
    print("6. Rollback forward (avanzar)")
    print("7. Salir")
    opcion = input("Seleccione una opción: ").strip()

    if opcion == "1":
        ruta = input("Ingrese la ruta o nombre del archivo (ej. C:/ruta/archivo.txt): ").strip()
        gestor = GestorArchivos(ruta)
        print(f"📁 Archivo cargado: {ruta}")

    elif opcion == "2":
        if gestor:
            texto = input("Ingrese el texto que desea escribir: ")
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
        print("👋 Saliendo del sistema.")
        break

    else:
        print("❌ Opción no válida.")
