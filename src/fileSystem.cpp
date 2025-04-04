#include "fileSystem.h"
#include <iostream>
#include <fstream>

fileSystem::fileSystem(size_t totalBlocks) : almacenamiento(totalBlocks) {
    if (!fs::exists("data")) {
        fs::create_directory("data");
    }
    cargarArchivosDesdeDisco();
}

void fileSystem::mostrarMenu() {
    std::cout << "\n=== Sistema de Archivos laVacaMu ===\n";
    std::cout << "1. Crear archivo\n";
    std::cout << "2. Escribir en archivo\n";
    std::cout << "3. Leer archivo\n";
    std::cout << "4. Eliminar archivo\n";
    std::cout << "5. Listar archivos\n";
    std::cout << "6. Mostrar eventos del Journal\n";
    std::cout << "7. Salir\n";
    std::cout << "Seleccione una opcion: ";
}

void fileSystem::crearArchivo(const std::string& nombre) {
    if (archivos.find(nombre) != archivos.end()) {
        std::cerr << "Error: El archivo ya existe.\n";
        return;
    }

    archivos[nombre] = "";
    guardarArchivoEnDisco(nombre);
    bitacora.registrarEvento("Archivo creado: " + nombre);
    std::cout << "Archivo '" << nombre << "' creado.\n";
}

void fileSystem::guardarArchivoEnDisco(const std::string& nombre) {
    std::ofstream archivo("data/" + nombre, std::ios::binary);
    if (!archivo) {
        std::cerr << "Error al guardar el archivo en disco.\n";
        return;
    }
    archivo.close();
}

void fileSystem::cargarArchivosDesdeDisco() {
    for (const auto& entry : fs::directory_iterator("data")) {
        std::string nombreArchivo = entry.path().filename().string();
        archivos[nombreArchivo] = "";
    }
}

void fileSystem::escribirArchivo(const std::string& nombre, const std::string& contenido) {
    if (archivos.find(nombre) == archivos.end()) {
        std::cerr << "Error: El archivo no existe.\n";
        return;
    }

    int bloque = almacenamiento.asignarBloque();
    if (bloque != -1) {
        archivos[nombre] += contenido;
        std::ofstream archivo("data/" + nombre, std::ios::binary | std::ios::app);
        if (!archivo) {
            std::cerr << "Error al escribir en disco.\n";
            return;
        }
        archivo << contenido;
        archivo.close();
        versiones.registrarCambio(nombre, bloque);
        bitacora.registrarEvento("Archivo modificado: " + nombre);
        std::cout << "Se escribió en '" << nombre << "'.\n";
    } else {
        std::cerr << "No hay espacio disponible.\n";
    }
}

std::string fileSystem::leerArchivo(const std::string& nombre) {
    if (archivos.find(nombre) == archivos.end()) {
        std::cerr << "Error: El archivo no existe.\n";
        return "";
    }

    std::ifstream archivo("data/" + nombre, std::ios::binary);
    if (!archivo) {
        std::cerr << "Error al leer el archivo.\n";
        return "";
    }

    std::string contenido((std::istreambuf_iterator<char>(archivo)), std::istreambuf_iterator<char>());
    archivo.close();
    return contenido;
}

void fileSystem::listarArchivos() {
    if (archivos.empty()) {
        std::cout << "No hay archivos en el sistema.\n";
        return;
    }
    std::cout << "Archivos en el sistema:\n";
    for (const auto& archivo : archivos) {
        std::cout << "- " << archivo.first << "\n";
    }
}
