import copy


class RegisterTable():
    def __init__(self):
        self.registers = []
        self.types = {}
        self.coherence = True
        self.copy = {}
        self.invalid_types = ["CHARACTER", "INT", "FLOAT", "BOOLEAN", "NULL"]
        self.add = True

    def add_type(self, name, type):
        if name not in self.types.keys() and name not in self.invalid_types and type not in self.invalid_types:
            for key, value in type.items():
                if not self.coherence:
                    # Si se encuentra un tipo no coherente se descarta el tipo
                    return False
                if value not in self.invalid_types:
                    self.add_type(name + key, type[key])
                    type[key] = name + key
                else:
                    # Si el tipo asignado a la variable del diccionario es correcta es True, sino False
                    self.coherence = value in self.types.keys() or value in self.invalid_types
            self.copy[name] = type
            return True
        return False

    def apply_coherence(self):
        """
        Si la asignación de cada uno de los tipos es correcta se añade, sino se descarta
        """
        if self.coherence:
            self.types = copy.deepcopy(self.copy)
        else:
            self.copy = copy.deepcopy(self.types)
        self.coherence = True

    def add_register(self, name, type, value, scope):
        # Si no existe otro registro con en mismo nombre y el tipo es correcto se añade
        if type not in self.types:
            return False
        self.check_type(type, value)
        if value is None:
            value = self.none_dict(type, {})
        if self.add:
            for register in self.registers:
                if register[0] == name and register[3] == scope:
                    # Si el registro ya existe en ese nivel no se añade
                    return False
            self.registers.append([name, type, value, scope])
            return True
        else:
            self.add = True
            return False


    def check_type(self, types, dictionary):
        if dictionary == None or dictionary[0] == None:
            return True
        if dictionary[1] != "DICT":
            self.add = False
            return False
        if types not in self.types.keys():
            # Si no existe el tipo que se intenta comprobar devuelve false
            return False
        real = {}
        for key in self.types.keys():
            # Se busca el diccionario que almacena el tipo que se está comprobando
            if key == types:
                real = self.types[key]
                break
        if real.keys() != dictionary[0].keys():
            return False

        for key in real.keys():
            if real[key] not in self.invalid_types:
                self.check_type(types + key, dictionary[0][key])
            else:
                if real[key] != dictionary[0][key][1]:
                    self.add = False
        return True


    def obtener_puntero (self, dictionary, lista, objetivo):
        if objetivo in dictionary[0].keys():
            return dictionary
        elif len(lista) == 0:
            return
        return self.obtener_puntero(dictionary[0][lista[0]], lista[1:], objetivo)

    def none_dict(self, type, dictionary, num = None):
        for key, value in self.types[type].items():
            if value in self.invalid_types:
                dictionary[key] = [None, value]
            else:
                dictionary[key] = {}
                if num is None:
                    dictionary[key] = self.none_dict(type + key, dictionary[key], 1)
                else:
                    dictionary[key] = self.none_dict(type + key, dictionary[key], num +1)
        return [dictionary, "DICT"]

