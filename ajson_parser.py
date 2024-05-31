import ply.yacc as yacc
from ajson_lexer import LexerClass
from function_table import FunctionTable
from symbol_table import SymbolTable
from register_table import RegisterTable
import os
directiorio_salida = os.getcwd() + "/test_files/output_parser"




class Parser():
    tokens = LexerClass.tokens

    def __init__(self):
        self.parser = yacc.yacc(module=self)
        self.symbol_table = SymbolTable()
        self.register_table = RegisterTable()
        self.function_table = FunctionTable()
        self.in_function = False
        self.next_scope = 1
        self.errors = []

    def p_global(self, p):
        '''global : function global
                    | type PUNTO_COMA global
                    | let PUNTO_COMA global
                    | var_declaration PUNTO_COMA global
                    | conditional global
                    | loop global
                    |
        '''

    def p_inscope(self, p):
        '''inscope : type PUNTO_COMA inscope
                    | let PUNTO_COMA inscope
                    | var_declaration PUNTO_COMA inscope
                    | conditional inscope
                    | loop inscope
                    |
        '''

    def p_type(self, p):
        '''type : TYPE STR_SIN_COMILLAS ASIGNACION ajson_type'''
        if not self.register_table.add_type(p[2], p[4]):
            self._add_error(f"[ERROR] No se puede añadir el tipo {p[2]}", p.lineno(1))
        # Se comprueba la coherencia del tipo
        self.register_table.apply_coherence()
    def p_ajson_type(self, p):
        '''ajson_type : LBRACKET contents_type RBRACKET'''
        p[0] = p[2]
    def p_contents_type(self, p):
        ''' contents_type : key DOS_PUNTOS tipos
                     | key DOS_PUNTOS tipos COMA
                     | key DOS_PUNTOS tipos COMA contents_type
                     | key DOS_PUNTOS ajson_type
                     | key DOS_PUNTOS ajson_type COMA
                     | key DOS_PUNTOS ajson_type COMA contents_type
        '''
        if len(p) <= 5:
            p[0] = {p[1]: p[3]}
        else:
            p[5][p[1]] = p[3]
            p[0] = p[5]


    def p_let(self,p):
        '''let : LET asignaciones'''

    def p_var_declaration(self, p):
        '''var_declaration : STR_SIN_COMILLAS valores_anidados ASIGNACION valores
        '''
        # REGISTROS ANÓNIMOS
        to_change = None
        is_symbol = True
        if self.in_function:
            for register in self.register_table.registers:
                if register[0] == p[1] and register[3] == self.next_scope:
                    to_change = register
                    is_symbol = False
            for symbol in self.symbol_table.symbols:
                if symbol[0] == p[1] and symbol[3] == self.next_scope:
                    to_change = symbol
        else:
            for register in self.register_table.registers:
                if register[0] == p[1] and register[3] == 0:
                    to_change = register
                    is_symbol = False
            for symbol in self.symbol_table.symbols:
                if symbol[0] == p[1] and symbol[3] == 0:
                    to_change = symbol
        if not to_change:
            self._add_error(f"[ERROR] No existe la variable {p[1]}", p.lineno(1))
        elif is_symbol:
            to_change[1] = p[4][1]
            to_change[2] = p[4][0]
        else:
            if len(p[2]) > 0:
                # Obtenemos el diccionario que debemos modificar
                to_change = self.register_table.obtener_puntero(to_change[2], p[2][:len(p[2]) - 1], p[2][-1])
                tipo = ""
                for key in p[2]:
                    tipo += key
                tipo = p[1] + tipo
                if not to_change:
                    self._add_error(f"[ERROR] No se puede acceder no existe", p.lineno(1))
                    pass
                elif tipo not in self.register_table.types.keys():
                    # Probamos a ver si es un valor u otro diccionario anidado

                    if p[4][1] == to_change[0][p[2][-1]][1]:
                        # Si es un valor que tiene tipo se le asigna el valor si coincide
                        to_change[0][p[2][-1]][0] = p[4][0]
                    else:
                        aux = ""
                        for key in p[2]:
                            aux += "."+key
                        self._add_error(f"[ERROR] No se puede asignar valor a '{p[1]+aux}'", p.lineno(1))
                else:

                    if self.register_table.check_type(tipo, p[4]):
                        to_change[0][p[2][-1]] = p[4]
                    else:
                        aux = ""
                        for key in p[2]:
                            aux += "." + key
                        self._add_error(f"[ERROR] No coincide el tipo de {p[1]+aux} con {p[4]}", p.lineno(1))

            else:
                if self.register_table.check_type(to_change[1], p[4]):
                    to_change[2] = p[4]
                else:
                    aux = ""
                    for key in p[2]:
                        aux += "."+key
                    self._add_error(f"[ERROR] No se puede asignar valor a '{p[1]+aux}'",p.lineno(1))



    def p_function(self,p):
        ''' function : FUNCTION STR_SIN_COMILLAS LPARENTESIS parametros RPARENTESIS DOS_PUNTOS tipos LBRACKET inscope RETURN valores PUNTO_COMA RBRACKET
        '''
        #Añadimos la función en la tabla de funciones(nombre, tipo, parametros,objetos existentes)
        if not self.function_table.add_function(p[2], p[7], p[4], self.register_table, self.symbol_table, self.next_scope):
            self._add_error(f"[ERROR] No se puede añadir la función {p[2]}",p.lineno(1))
        self.in_function = False
        self.next_scope += 1

    def p_conditional(self,p):
        ''' conditional : IF LPARENTESIS expression RPARENTESIS LBRACKET inscope RBRACKET adicional '''
        if p[3][1] != "BOOLEAN":
            self._add_error("[ERROR] La expresión dentro del condicional debe ser de tipo 'BOOLEAN'", p.lineno(1))
        else:
            # Gestion de flujo que no se ha hecho
            pass
    def p_loop(self,p):
        '''loop : WHILE LPARENTESIS expression RPARENTESIS LBRACKET inscope RBRACKET '''
        if p[3][1] != "BOOLEAN":
            self._add_error("[ERROR] La expresión dentro del bucle debe ser de tipo 'BOOLEAN'",p.lineno(1))
        else:
            # Gestion de flujo que no se ha hecho
            pass
    def p_asignaciones(self, p):
        '''
        asignaciones : tipadas
                     | no_tipadas
        '''

    def p_tipadas(self, p):
        '''tipadas : STR_SIN_COMILLAS DOS_PUNTOS STR_SIN_COMILLAS COMA asignaciones
                     | STR_SIN_COMILLAS DOS_PUNTOS STR_SIN_COMILLAS ASIGNACION valores
                     | STR_SIN_COMILLAS DOS_PUNTOS STR_SIN_COMILLAS'''
        # Variables que tienen tipos(Regsiter Table).
        if len(p) == 6 and p[4] == "=":
            # Añadir su valor a la tabla de registros.
            if self.in_function:
                num_errors = len(self.errors)
                for register in self.register_table.registers:
                    if register[0] == p[1] and register[3] == self.next_scope:
                        self._add_error(f"[ERROR] El símbolo '{p[1]}' ya existe", p.lineno(1))
                for symbol in self.symbol_table.symbols:
                    if symbol[0] == p[1] and symbol[3] == self.next_scope and num_errors == len(self.errors):
                        self._add_error(f"[ERROR] El símbolo '{p[1]}' ya existe",p.lineno(1))
                if num_errors == len(self.errors):
                    if not self.register_table.add_register(p[1], p[3], p[5], self.next_scope):
                        self._add_error(f"[ERROR] No se puede asignar valor a la variable {p[1]}", p.lineno(1))
            else:
                num_errors = len(self.errors)
                for register in self.register_table.registers:
                    if register[0] == p[1] and register[3] == 0:
                        self._add_error(f"[ERROR] El símbolo '{p[1]} 'ya existe",p.lineno(1))
                for symbol in self.symbol_table.symbols:
                    if symbol[0] == p[1] and symbol[3] == 0 and num_errors == len(self.errors):
                        self._add_error(f"[ERROR] El símbolo '{p[1]}' ya existe",p.lineno(1))
                if num_errors == len(self.errors):
                    if not self.register_table.add_register(p[1], p[3], p[5], 0):
                        self._add_error(f"[ERROR] No se puede asignar valor a la variable {p[1]}", p.lineno(1))

        else:
            if self.in_function:
                num_errors = len(self.errors)
                for register in self.register_table.registers:
                    if register[0] == p[1] and register[3] == self.next_scope:
                        self._add_error(f"[ERROR] El símbolo '{p[1]}' ya existe", p.lineno(1))
                for symbol in self.symbol_table.symbols:
                    if symbol[0] == p[1] and symbol[3] == self.next_scope and num_errors == len(self.errors):
                        self._add_error(f"[ERROR] El símbolo '{p[1]}' ya existe", p.lineno(1))
                if num_errors == len(self.errors):
                    self.register_table.add_register(p[1], p[3], None, self.next_scope)
            else:
                num_errors = len(self.errors)
                for register in self.register_table.registers:
                    if register[0] == p[1] and register[3] == 0:
                        self._add_error(f"[ERROR] El símbolo '{p[1]} 'ya existe", p.lineno(1))
                for symbol in self.symbol_table.symbols:
                    if symbol[0] == p[1] and symbol[3] == 0 and num_errors == len(self.errors):
                        self._add_error(f"[ERROR] El símbolo '{p[1]}' ya existe", p.lineno(1))
                if num_errors == len(self.errors):
                    self.register_table.add_register(p[1], p[3], None, 0)


    def p_no_tipadas(self, p):
        '''no_tipadas : STR_SIN_COMILLAS COMA asignaciones
                       | STR_SIN_COMILLAS ASIGNACION valores
                       | STR_SIN_COMILLAS'''
        # Variables que no tienen tipo(Symbol Table).
        if len(p) == 4 and p[2] == "=":
            # Añadir su valor a la tabla de symbolos.
            if self.in_function:
                num_errors = len(self.errors)
                for register in self.register_table.registers:
                    if register[0] == p[1] and register[3] == self.next_scope:
                        self._add_error(f"[ERROR] El símbolo '{p[1]}' ya existe", p.lineno(1))
                for symbol in self.symbol_table.symbols:
                    if symbol[0] == p[1] and symbol[3] == self.next_scope and num_errors == len(self.errors):
                        self._add_error(f"[ERROR] El símbolo '{p[1]}' ya existe", p.lineno(1))
                if num_errors == len(self.errors):
                    self.symbol_table.add_symbol(p[1], p[3][1], p[3][0], self.next_scope)
            else:
                num_errors = len(self.errors)
                for register in self.register_table.registers:
                    if register[0] == p[1] and register[3] == 0:
                        self._add_error(f"[ERROR] El símbolo '{p[1]} 'ya existe", p.lineno(1))
                for symbol in self.symbol_table.symbols:
                    if symbol[0] == p[1] and symbol[3] == 0 and num_errors == len(self.errors):
                        self._add_error(f"[ERROR] El símbolo '{p[1]}' ya existe", p.lineno(1))
                if num_errors == len(self.errors):
                    self.symbol_table.add_symbol(p[1], p[3][1], p[3][0], 0)
        else:
            # Si se ha definido pero no devuelve valor correctamente se pondrá en NULL.
            if self.in_function:
                num_errors = len(self.errors)
                for register in self.register_table.registers:
                    if register[0] == p[1] and register[3] == self.next_scope:
                        self._add_error(f"[ERROR] El símbolo '{p[1]}' ya existe",p.lineno(1))
                for symbol in self.symbol_table.symbols:
                    if symbol[0] == p[1] and symbol[3] == self.next_scope and num_errors == len(self.errors):
                        self._add_error(f"[ERROR] El símbolo '{p[1]}' ya existe",p.lineno(1))
                if num_errors == len(self.errors):
                    self.symbol_table.add_symbol(p[1], "NULL", None, self.next_scope)
            else:
                num_errors = len(self.errors)
                for register in self.register_table.registers:
                    if register[0] == p[1] and register[3] == 0:
                        self._add_error(f"[ERROR] El símbolo '{p[1]} 'ya existe",p.lineno(1))
                for symbol in self.symbol_table.symbols:
                    if symbol[0] == p[1] and symbol[3] == 0:
                        self._add_error(f"[ERROR] El símbolo '{p[1]}' ya existe", p.lineno(1))
                if num_errors == len(self.errors):
                    self.symbol_table.add_symbol(p[1], "NULL", None, 0)

    def p_adicional(self, p):
        '''adicional : ELSE LBRACKET inscope RBRACKET
                    |
        '''

    def p_parametros(self, p):
        '''parametros : STR_SIN_COMILLAS DOS_PUNTOS tipos
                    | STR_SIN_COMILLAS DOS_PUNTOS tipos COMA parametros
                    |
        '''
        # Se detecta que se está declsrando una función para saber que hasta que se termine de declarar
        # todas las variables que se definan tendrán un scope diferente
        self.in_function = True

        #Guardar en p[0] el tipo de los parametros en forma de lista.
        if len(p) == 6:
            if p[3] in self.symbol_table.valid_types:
                self.symbol_table.add_symbol(p[1], p[3], None, self.next_scope)
            elif p[3] in self.register_table.types.keys():
                self.register_table.add_register(p[1], p[3], None, self.next_scope)
            p[5].append([p[1], p[3]])
            p[0] = p[5]

        elif len(p) == 4:
            if p[3] in self.symbol_table.valid_types:
                self.symbol_table.add_symbol(p[1], p[3], None, self.next_scope)
            elif p[3] in self.register_table.types.keys():
                self.register_table.add_register(p[1], p[3], None, self.next_scope)
            p[0] = [[p[1], p[3]]]
        else:
            p[0] = []

    def p_tipos(self, p):
        '''tipos : INT
                  | FLOAT
                  | BOOLEAN
                  | CHARACTER
                  | STR_SIN_COMILLAS
        '''
        #Los tipos en el diccionario se escriben en minúsulas.
        if p[1] == "int" or p[1] == "float" or p[1] == "boolean" or p[1] == "character":
            p[0] = p[1].upper()
        else:
            p[0] = p[1]
    def p_valores(self, p):
        '''
        valores : ajson_value
                | expression
        '''
        #Obtiene el valor.
        p[0] = p[1]

    #Las expresiones se dividen entres niveles; booleanes, comparación y operadores. Para establecer
    #el orden de precedencia.
    def p_expression(self, p):
        '''
        expression : comparation
                   | comparation AND expression
                   | comparation OR expression
                   | NOT expression
        '''
        #AND/OR
        if len(p) == 4:
            #Si el valor no es None en ninguno de los casos.
            if p[1][1] == None or p[3][1] == None or p[1][1] in self.register_table.types.keys() or p[3][1] in self.register_table.types.keys():
                # Será valor nulo.
                p[0] = [None, "NULL"]
            # Si ninguna de las dos es booleana.
            elif p[1][1] != "BOOLEAN" or p[3][1] != "BOOLEAN":
                self._add_error(f"[ERROR] No se puede comparar {p[1][1]} y {p[3][1]}",p.lineno(1))
                p[0] = [None, "NULL"]
            # Se realiza la operación.
            else:
                if p[1][0] == None or p[3][0] == None:
                    # Si el resultado es el de una función se devuelve el tipo pero no el valor
                    p[0] = [None, "BOOLEAN"]

                elif p[2] == "&&":
                    p[0] = [p[1][0] and p[3][0], "BOOLEAN"]
                elif p[2] == "||":
                    p[0] = [p[1][0] or p[3][0], "BOOLEAN"]
        elif len(p) == 3:
            # En caso de not.
            # Si el valor es Null
            if p[2][0] == None and p[2][1] == "BOOLEAN":
                p[0] = [None, "BOOLEAN"]
            elif p[2][1] != "BOOLEAN" or p[2][1] == None or p[2][1] in self.register_table.types.keys():
                p[0] = [None, "NULL"]
                self._add_error(f"[ERROR] Imposible realizar la operación Not sobre {p[2][0]}",p.lineno(1))
            else:
                #Operador Not.
                p[0] = [not p[2][0], "BOOLEAN"]
        else:
            p[0] = p[1]

    def p_comparation(self, p):
        '''comparation : subsum MAYOR comparation
             | subsum MENOR comparation
             | subsum MAYIGUAL comparation
             | subsum MENIGUAL comparation
             | subsum IGUALBOOL comparation
             | subsum'''
        if len(p) == 4:
            # Si el valor es booleano en alguno de los casos
            is_bool = p[1][1] == "BOOLEAN" and p[3][1] == "BOOLEAN"
            #En caso de que la comparacion sea None.
            if p[3][0] == None and p[3][1] == "NULL":
                p[0] = p[3]
            # Si es booleano
            elif p[1][1] in self.register_table.types.keys() or p[3][1] in self.register_table.types.keys():
                p[0] = [None, "NULL"]
            elif is_bool:
                #Si no es un IGUAL IGUAL
                if p[2] != "==":
                    p[0] = [None, "NULL"]
                    self._add_error("[ERROR] Tipos no válidos al realizar comparaciones", p.lineno(1))
                else:
                    #Realizar esta comparación SOLO POSIBLE para booleanas
                    p[0] = [p[1][0] == p[3][0], "BOOLEAN"]
            elif  (p[1][1] == "BOOLEAN" or p[3][1] == "BOOLEAN"):
                p[0] = [None, "NULL"]
                self._add_error("[ERROR] Tipos no válidos al realizar comparaciones", p.lineno(1))
            else:
                # Conversión caracteres
                if p[1][1] == "CHARACTER"and p[1][0] is not None:
                    p[1][0] = ord(p[1][0])
                if p[3][1] == "CHARACTER" and p[3][0] is not None:
                    p[3][0] = ord(p[3][0])
                # Comparadores, devuelven un booleano.
                if p[1][0] == None or p[3][0] == None:
                    # Si el resultado es el de una función se devuelve el tipo pero no el valor
                    p[0] = [None, "BOOLEAN"]
                elif p[2] == ">":
                    p[0] = [p[1][0] > p[3][0], "BOOLEAN"]
                elif p[2] == "<":
                    p[0] = [p[1][0] < p[3][0], "BOOLEAN"]
                elif p[2] == ">=":
                    p[0] = [p[1][0] >= p[3][0], "BOOLEAN"]
                elif p[2] == "<=":
                    p[0] = [p[1][0] <= p[3][0], "BOOLEAN"]
                elif p[2] == "==":
                    p[0] = [p[1][0] == p[3][0], "BOOLEAN"]
                else:
                    # Caso de error.
                    self._add_error("[ERROR] Tipos no válidos al realizar comparaciones", p.lineno(1))
                    p[0] = [None, "NULL"]
        else:
            p[0] = p[1]

    def p_subsum(self, p):
        '''subsum : assignation_var MAS subsum
                    | assignation_var MENOS subsum
                    | assignation_var'''
        # Operaciones + y -, solo con flotantes, caracteres y enteros(teniendo en cuenta conversión).
        if len(p) == 4:
            type = "NULL"
            #Conversión de caracteres.
            if p[1][1] == "CHARACTER":
                p[1][0] = ord(p[1][0])
            # Conversión de caracteres.
            if p[3][1] == "CHARACTER":
                if p[3][0]:
                    p[3][0] = ord(p[3][0])
            #Si es de tipo caracter.
            if p[1][1] == "CHARACTER" or p[3][1] == "CHARACTER":
                type = "CHARACTER"
            #Si es de tipo entero.
            if p[1][1] == "INT" or p[3][1] == "INT":
                type = "INT"
            #Si es de tipo float(prevalece).
            if p[1][1] == "FLOAT" or p[3][1] == "FLOAT":
                type = "FLOAT"
            if p[1][1] == "BOOLEAN" or p[3][1] == "BOOLEAN" or p[1][1] in self.register_table.types.keys() or p[3][1] in self.register_table.types.keys():
                # Manejo de error.
                self._add_error("[ERROR] Tipos no válidos al realizar suma/resta",p.lineno(1))
                p[0] = [None, "NULL"]

            elif p[1][0] == None or p[3][0] == None:
                # Si el resultado es el de una función se devuelve el tipo pero no el valor
                p[0] = [None, type]
            elif p[2] == "+":
                if type == "CHARACTER":
                    #Si son caracteres vuelve s ser un caracter.
                    p[0] = [chr(p[1][0] + p[3][0]), type]
                else:
                    # Otro caso.
                    p[0] = [p[1][0] + p[3][0], type]

            elif p[2] == "-":
                if type == "CHARACTER":
                    # Si son caracteres vuelve s ser un caracter.
                    if p[1][0] > p[3][0]:
                        p[0] = [chr(p[1][0] - p[3][0]), type]
                    else:
                        p[0] = [None, "NULL"]
                        self._add_error("[ERROR] No permitido esta operación entre caracteres valor de resta negativo",p.lineno(1))
                else:
                    p[0] = [p[1][0] - p[3][0], type]
        else:
            p[0] = p[1]

    def p_assignation_var(self, p):
        '''
        assignation_var : var
             | var POR assignation_var
             | var ENTRE assignation_var
        '''
        if len(p) == 4:
            type = "NULL"
            #Caracter y entero
            if p[1][1] == "CHARACTER":
                #Conversión de caracter.
                if p[1][0]:
                    p[1][0]= ord(p[1][0])
                type= "INT"
            if p[3][1] == "CHARACTER":
                # Conversión de caracter.
                if p[3][0]:
                    p[3][0] = ord(p[3][0])
                type="INT"
            if p[1][1] == "INT" or p[3][1] == "INT":
                type = "INT"
            if p[1][1] == "FLOAT" or p[3][1] == "FLOAT":
                type = "FLOAT"
            if p[1][1] == "BOOLEAN" or p[3][1] == "BOOLEAN" or p[1][1] in self.register_table.types.keys() or p[3][1] in self.register_table.types.keys():
                # Manejo de error.
                self._add_error("[ERROR] Tipos no válidos al realizar mul/div",p.lineno(1))
                p[0] = [None, "NULL"]
            elif p[3] == [None, "NULL"] or p[1] == [None, "NULL"]:
                p[0] = [None, "NULL"]
            elif p[1][0] == None or p[3][0] == None:
                # Si el resultado es el de una función se devuelve el tipo pero no el valor
                p[0] = [None, type]
            elif p[2] == "/":
                # En caso de que el denominador sea mayor que el numerador, tipo flotante.
                if (type == "INT" and p[1][0] < p[3][0]) or type == "FLOAT":
                    p[0] = [p[1][0] / p[3][0], "FLOAT"]
                else:
                    #En caso de que sea entero.
                    p[0] = [p[1][0] // p[3][0], type]
            elif p[2] == "*":
                #Multiplicación devuelve tipo correspondiente
                p[0] = [p[1][0] * p[3][0], type]
        else:
            p[0]=p[1]

    def p_var(self, p):
        '''
        var : entero
                | flotante
                | parentesis
                | caracter
                | identificador
                | booleano
                | valor_nulo
                | funciones
                | unarios
        '''
        #Separamos los casos para poder manejarlos independientemente.
        p[0] = p[1]
    def p_booleano(self, p):
        '''booleano : TR
                    | FL'''
        # Obtenemos el valor con el tipo, si llega hasta aquí tipo BOOLEAN.
        p[0] = [p[1], "BOOLEAN"]

    def p_valor_nulo(self, p):
        '''valor_nulo : NULL'''
        #Obtenemos el valor con el tipo, si llega hasta aquí tipo NULL.
        p[0] = [p[1], "NULL"]

    def p_expression_list(self,p):
        ''' expression_list : expression
                            | expression COMA expression_list
                            | ajson_value
                            | ajson_value COMA expression_list
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[3].append(p[1])
            p[0] = p[3]
    def p_valores_anidados(self, p):
        '''valores_anidados : LCORCHETE STR_CON_COMILLAS RCORCHETE valores_anidados
                            | PUNTO STR_SIN_COMILLAS valores_anidados
                            |
        '''
        if len(p) == 1:
            p[0] = []
        elif len(p) == 5:
            p[0] = [p[2]] + p[4]
        else:
            p[0] = [p[2]] + p[3]
    def p_ajson_value(self, p):
        ''' ajson_value : LBRACKET contents RBRACKET
        '''
        p[0] = [p[2], "DICT"]

    def p_contents(self, p):
        ''' contents : key DOS_PUNTOS valores
                     | key DOS_PUNTOS valores COMA
                     | key DOS_PUNTOS valores COMA contents
        '''
        if len(p) <= 5:
            p[0] = {p[1]: p[3]}
        else:
            p[5][p[1]] = p[3]
            p[0] = p[5]

    def p_key(self, p):
        ''' key : STR_CON_COMILLAS
                | STR_SIN_COMILLAS
        '''
        p[0] = p[1]

    def p_entero(self, p):
        ''' entero : INT_VALUE
        '''
        # Obtenemos el valor con el tipo, si llega hasta aquí tipo INT.
        p[0] = [p[1], "INT"]
    def p_flotante(self, p):
        '''flotante : FLOAT_VALUE
        '''
        # Obtenemos el valor con el tipo, si llega hasta aquí tipo FLOAT.
        p[0] = [p[1], "FLOAT"]

    def p_parentesis(self, p):
        '''parentesis : LPARENTESIS expression RPARENTESIS'''
        #QUITAMOS LOS PARENTESIS
        p[0] = p[2]
    def p_caracter(self, p):
        '''caracter : CARACTER'''
        # Obtenemos el valor con el tipo, si llega hasta aquí tipo character.
        p[0] = [p[1], "CHARACTER"]
    def p_funciones(self, p):
        '''funciones : STR_SIN_COMILLAS LPARENTESIS expression_list RPARENTESIS
                    | STR_SIN_COMILLAS LPARENTESIS RPARENTESIS'''
        # Comprobación de los parámetros de la función correspondiente.
        if len(p)==4:
            #No hay parámetros, lista vacía.
            check_function = self.function_table.check_parameters(p[1],[])
        elif len(p)==5:
            check_function = self.function_table.check_parameters(p[1], p[3], self.register_table)
        if check_function[0]:
            p[0] = [None, check_function[1]]
        else:
            self._add_error(f"[ERROR] La llamada a la función {p[1]} no es correcta", p.lineno(1))
            p[0] = [None, "NULL"]

    def p_unarios(self, p):
        '''unarios : MENOS var
                 | MAS var '''
        #Operadores unarios. Mayor precedencia(por niveles).
        if p[2][0] is None:
            p[0] = p[2]
        elif p[1]=="-":
            p[2][0]= -p[2][0]
            p[0]= p[2]
        else:
            p[0] = p[2]


    def p_identificador(self, p):
        '''identificador : STR_SIN_COMILLAS valores_anidados'''
        # Acceder al valor de la variable STR_SIN_COMILLAS(id), devuelve valor y tipo.
        if len(p[2]) == 0:
            is_symbol = True
            array = None
            if self.in_function:
                for register in self.register_table.registers:
                    if register[0] == p[1] and register[3] == self.next_scope:
                        is_symbol = False
                        array = [register[1], register[2]]
                if is_symbol:
                    array = self.symbol_table.get_type(p[1], self.next_scope)
            else:
                for register in self.register_table.registers:
                    if register[0] == p[1] and register[3] == 0:
                        array = [register[2], register[1]]
                        is_symbol = False
                if is_symbol:
                    array = self.symbol_table.get_type(p[1], 0)
            if array:
                p[0] = [array[1], array[0]]
            else:
                self._add_error(f"[ERROR] El identificador {p[1]} no se encontró en la tabla de símbolos",p.lineno(1))
                p[0] = [None, "NULL"]
        else:
            to_change = None
            for register in self.register_table.registers:
                if register[0] == p[1] and register[3] == 0:
                    to_change = register
            if not to_change:
                aux = ""
                for val in p[2]:
                    aux += "." + val
                self._add_error(f"[ERROR] El identificador {p[1] + aux} no se encontró en la tabla de registros",p.lineno(1))
                p[0] = [None, "NULL"]
            else:
                to_change = self.register_table.obtener_puntero(to_change[2], p[2][:len(p[2]) - 1], p[2][-1])
                value = to_change[0][p[2][-1]]

                if value[1] != "DICT":
                    p[0] = value
                else:
                    aux = ""
                    for val in p[2]:
                        aux += "." + val
                    self._add_error(f"[ERROR] No se puede operar con el valor de {p[1] + aux}",p.lineno(1))
                    p[0] = [None, "NULL"]

    def p_error(self, p):
        print("Yacc error at", p)

    def _add_error(self, message, lineno):
        if lineno is not None:
            message = f"Línea {lineno}: {message}"
        self.errors.append(message)

    def test(self, data, file_name):
        self.parser.parse(data, tracking=True)
        for error in self.errors:
            print(error)
        for register in self.register_table.registers:
            register[2] = self.quitar_tipo(register[2])
        to_print_register = "Registros:\n"
        for register in self.register_table.registers:
            to_print_register += f"\t- {register[0]}, Scope: {register[3]}, Tipo: {register[1]}, Valor: {register[2]}\n"
        to_print_register += "\nTipos:\n"
        for key, value in self.register_table.types.items():
            to_print_register += f"\t- {key}, {value}\n"
        to_print_register += "\nFunciones:\n"
        for function in self.function_table.functions:
            to_print_register += f"\t- {function[0]}, Tipo: {function[1]}, Atributos {function[2]}\n"
        to_print_symbol = ""
        for symbol in self.symbol_table.symbols:
            to_print_symbol += f"Symbol: {symbol[0]}, Scope: {symbol[3]}, Tipo: {symbol[1]}, Valor: {symbol[2]}\n"
        if not os.path.exists(directiorio_salida):
            os.makedirs(directiorio_salida)
        a = ""
        for char in file_name[::-1]:
            if char == "/":
                break
            a += char

        file_name = a[::-1]
        file_path_register = os.path.join(directiorio_salida, file_name + ".register")
        file_path_symbol = os.path.join(directiorio_salida, file_name + ".symbol")
        with open(file_path_register, 'w') as file:
            file.write(to_print_register)
        with open(file_path_symbol, 'w') as file:
            file.write(to_print_symbol)

    def quitar_tipo(self, valor_tipo):
        """
        Se quitan los pares [valor, tipo] de los diccionarios para su impresión
        """
        if valor_tipo is not None and valor_tipo[1] == "DICT":
            for key, value in valor_tipo[0].items():
                valor_tipo[0][key] = self.quitar_tipo(value)
            return valor_tipo[0]
        return valor_tipo


