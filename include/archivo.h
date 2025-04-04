#ifndef ARCHIVO_H
#define ARCHIVO_H

#include <string>

class Archivo {
public:
    std::string nombre;
    std::string contenido;

    Archivo(const std::string& nombre) : nombre(nombre), contenido("") {}

    void escribir(const std::string& nuevoContenido) {
        contenido = nuevoContenido;
    }

    std::string leer() const {
        return contenido;
    }
};

#endif
