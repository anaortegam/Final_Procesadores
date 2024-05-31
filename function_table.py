from register_table import RegisterTable
from symbol_table import SymbolTable
class FunctionTable:
    def __init__(self):
        self.functions = []

    def add_function(self, name, type, dic, register_table: RegisterTable, symbol_table: SymbolTable, scope):
        #Para añadir una función a nuestra tabla de funciones.
        param_types = []
        for tipo in dic:
            param_types.append(tipo[1])
        if type not in register_table.types and type not in register_table.invalid_types:
            return False
        elif self.new_function(name, param_types, register_table.types):
            #Se mete el nombre, el tipo y los parametros.
            self.functions.append([name, type, param_types])
            return True


    def new_function(self, name, dic, tipos):
        # Comprobación de la función.
        add = True
        for function in self.functions:
            # Si tiene el mismo nombre.
            if function[0] == name:
                # Se comprueba la cantidad de parámetros, si el igual no se mete.
                if len(function[2]) == len(dic):
                    add = False
        if not add:
            return False
        for param in dic:
            # Si los parametros no corresponden con ninguno de los tipos ni objetos declarados.
            if param not in tipos.keys() and param != "CHARACTER" and param != "INT" and param != "FLOAT" and param != "BOOLEAN":
                return False
        return True


    def check_parameters(self, name, list, register_table: RegisterTable = None):
        lista = None
        type = None
        #Por cada funcion.
        for function in self.functions:
            #Si el nombre es igual.
            if function[0] == name:
                if len(function[2]) == len(list):
                    type = function[1]
                    lista = function[2]
        if lista is None and type is None:
            return [False, type]
        for i in range(len(lista)):
            #Recorres la lista parámetros por parámetro, con su tipo.
            if list[i][1] == "DICT":
                if not register_table.check_type(lista[i], list[i]):
                    return [False, type]
            else:
                if lista[i] != list[i][1]:
                    return [False, type]

        return [True, type]

