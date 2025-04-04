// bloques yyy bitmap 

#include "almacena.h"

almacena::almacena(size_t bloquesTotal) {
    bitmap.resize(bloquesTotal, false); // Inicializa todos los bloques como libres
}

int almacena::asignarBloque() {
    for (size_t i = 0; i < bitmap.size(); i++) {
        if (!bitmap[i]) {  // Si el bloque está libre
            bitmap[i] = true;  // Marcarlo como ocupado
            return i;
        }
    }
    return -1;  // No hay espacio disponible
}

void almacena::liberarBloque(int blockIndex) {
    if (blockIndex >= 0 && blockIndex < bitmap.size()) {
        bitmap[blockIndex] = false;  // Marcar el bloque como libre
    }
}

void almacena::imprimirBitmap() {
    for (bool bit : bitmap) {
        std::cout << (bit ? "1" : "0") << " ";
    }
    std::cout << std::endl;
}

