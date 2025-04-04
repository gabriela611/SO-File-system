#ifndef JOURNAL_H
#define JOURNAL_H

#include <string>
#include <vector>

class journal {
private:
    std::vector<std::string> eventos;

public:
    void registrarEvento(const std::string& evento);
    void mostrarEventos();
};

#endif // JOURNAL_H
