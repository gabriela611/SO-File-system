# Variables
CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -Iinclude
AR = ar
ARFLAGS = rcs

# Carpetas
SRC_DIR = src
LIB_DIR = lib
OBJ_DIR = obj

# Archivos fuente
SRCS = $(wildcard $(SRC_DIR)/*.cpp)
OBJS = $(patsubst $(SRC_DIR)/%.cpp, $(OBJ_DIR)/%.o, $(SRCS))

# Nombre de la librería
LIB_NAME = liblaVacaMu.a
LIB_PATH = $(LIB_DIR)/$(LIB_NAME)

# Regla principal
all: $(LIB_PATH)

# Crear librería estática
$(LIB_PATH): $(OBJS) | $(LIB_DIR)
	$(AR) $(ARFLAGS) $@ $^

# Compilar archivos .cpp a .o
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp | $(OBJ_DIR)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Crear carpetas necesarias
$(OBJ_DIR):
	mkdir -p $(OBJ_DIR)

$(LIB_DIR):
	mkdir -p $(LIB_DIR)

# Limpiar archivos generados
clean:
	rm -rf $(OBJ_DIR) $(LIB_DIR)
