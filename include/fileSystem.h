#ifndef FILESYSTEM_H
#define FILESYSTEM_H

#include <string>
#include <unordered_map>
#include "almacena.h"
#include "journal.h"
#include "tablaVersiones.h"
#include <fstream>
#include <filesystem>

namespace fs = std::filesystem;

class fileSystem {
private:
    almacena almacenamiento;
    journal bitacora;
    tablaVersiones versiones;
    std::unordered_map<std::string, std::string> archivos; // Simulación de memoria

public:
    fileSystem(size_t totalBlocks);
    void mostrarMenu();
    void crearArchivo(const std::string& nombre);
    void escribirArchivo(const std::string& nombre, const std::string& contenido);
    std::string leerArchivo(const std::string& nombre);
    void eliminarArchivo(const std::string& nombre);
    void listarArchivos();
    void restaurarVersion(const std::string& nombre, int version);
    void imprimirEstado();
    void mostrarEventosJournal();

    // Métodos para manejo en disco
    void guardarArchivoEnDisco(const std::string& nombre);
    void cargarArchivosDesdeDisco();
};

#endif
