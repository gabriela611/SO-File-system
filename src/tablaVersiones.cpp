// tabla de versiones wow
#include "tablaVersiones.h"

void tablaVersiones::registrarCambio(const std::string& nombre, int bloque) {
    versiones[nombre].push_back(bloque);
}

std::vector<int> tablaVersiones::obtenerVersiones(const std::string& nombre) {
    return versiones[nombre];
}
