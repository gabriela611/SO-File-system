// journal para guardar cositas y que no se borren xd
#include "journal.h"
#include <iostream>

void journal::registrarEvento(const std::string& evento) {
    eventos.push_back(evento);
}

void journal::mostrarEventos() {
    for (const std::string& evento : eventos) {
        std::cout << evento << std::endl;
    }
}
