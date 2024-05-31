class SymbolTable:
    def __init__(self):
        self.symbols = []
        self.valid_types = ["CHARACTER", "INT", "FLOAT", "BOOLEAN", "NULL"]

    def add_symbol(self, name, type, value, scope):
        #Añades las variables por nombre con su valor y tipo.
        if type not in self.valid_types:
            return False
        for symbol in self.symbols:
            if symbol[0] == name and symbol[3] == scope:
                return False
        self.symbols.append([name, type, value, scope])
    def update_symbol(self, name, type, value):
        #Actualizas el valor y tipo
        self.symbols[name][0] = value
        self.symbols[name][1] = type
    def get_type(self, name, scope):
        #Obtener el tipo de esa variable.
        for symbol in self.symbols:
            if symbol[0] == name and symbol[3] == scope:
                return [symbol[1], symbol[2]]
        return None
