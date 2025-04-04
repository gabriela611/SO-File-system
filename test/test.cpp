#include <iostream>
#include "C:\Users\gabri\universidad\SO\proyecto 2\laVacaMu\include\fileSystem.h"  // Usa la librería

int main() {
    fileSystem fs(100);  // Crea un sistema de archivos con 100 bloques
    int opcion;

    do {
        fs.mostrarMenu();
        std::cin >> opcion;
        std::cin.ignore();  // Limpia el buffer del teclado

        switch (opcion) {
            case 1:
                std::string nombreArchivo;
                std::cout << "Ingrese el nombre del archivo: ";
                std::getline(std::cin, nombreArchivo);
                fs.crearArchivo(nombreArchivo);
                break;
            case 2:
                std::string nombreArchivoEscribir, contenido;
                std::cout << "Ingrese el nombre del archivo: ";
                std::getline(std::cin, nombreArchivoEscribir);
                std::cout << "Ingrese el contenido: ";
                std::getline(std::cin, contenido);
                fs.escribirArchivo(nombreArchivoEscribir, contenido);
                break;
            case 3:
                std::string nombreArchivoLeer;
                std::cout << "Ingrese el nombre del archivo: ";
                std::getline(std::cin, nombreArchivoLeer);
                std::cout << "Contenido del archivo: " << fs.leerArchivo(nombreArchivoLeer) << std::endl;
                break;
            case 4: 
                std::string nombreArchivoEliminar;
                std::cout << "Ingrese el nombre del archivo: ";
                std::getline(std::cin, nombreArchivoEliminar);
                fs.eliminarArchivo(nombreArchivoEliminar);
                break;
            case 5: 
                fs.listarArchivos();
                break;
        }

    } while (opcion != 7);


    

    
    
    return 0;
}
