#ifndef TABLAVERSIONES_H
#define TABLAVERSIONES_H

#include <unordered_map>
#include <vector>
#include <string>

class tablaVersiones {
private:
    std::unordered_map<std::string, std::vector<int>> versiones;

public:
    void registrarCambio(const std::string& nombre, int bloque);
    std::vector<int> obtenerVersiones(const std::string& nombre);
};

#endif // TABLAVERSIONES_H
