#ifndef ALMACENA_H
#define ALMACENA_H

#include <vector>
#include <iostream>

class almacena {
    private: 
    std::vector<bool> bitmap;

    public:
    almacena(size_t bloquesTotal);
    int asignarBloque();
    void liberarBloque(int bloque);
    void imprimirBitmap();

};

#endif