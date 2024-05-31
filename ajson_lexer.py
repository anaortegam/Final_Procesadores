import ply.lex as lex
from ply.lex import TOKEN
import os
directiorio_salida = os.getcwd() + "/test_files/output_lexer"

reserved = (
        "TR",
        "FL",
        "LET",
        "INT",
        "FLOAT",
        "CHARACTER",
        "WHILE",
        "BOOLEAN",
        "FUNCTION",
        "RETURN",
        "TYPE",
        "IF",
        "ELSE",
        "NULL"
    )


class LexerClass():

    def __init__(self):
        self.lexer = lex.lex(module=self)
        self.reserved_map = {}
        for r in reserved:
            self.reserved_map[r.lower()] = r   # Solo reconocidas minúsculas

    tokens = (
        "PUNTO",
        "CARACTER",
        "LBRACKET",
        "RBRACKET",
        "DOS_PUNTOS",
        "PUNTO_COMA",
        "COMA",
        "STR_CON_COMILLAS",
        "STR_SIN_COMILLAS",
        "RPARENTESIS",
        "LPARENTESIS",
        "MAS",
        "MENOS",
        "POR",
        "ENTRE",
        "FLOAT_VALUE",
        "INT_VALUE",
        "MAYOR",
        "MENOR",
        "MAYIGUAL",
        "MENIGUAL",
        "IGUALBOOL",
        "ASIGNACION",
        "AND",
        "OR",
        "NOT",
        "LCORCHETE",
        "RCORCHETE"
    ) + reserved

    t_PUNTO = r"\."
    t_RPARENTESIS = r'\)'
    t_LPARENTESIS = r'\('
    t_PUNTO_COMA = r";"
    t_LBRACKET = r"{"
    t_RBRACKET = r"}"
    t_DOS_PUNTOS = ":"
    t_COMA = r","
    t_MAS = r'\+'
    t_MENOS = r'-'
    t_POR = r'\*'
    t_ENTRE = r'/'
    t_MAYOR = r'>'
    t_MENOR = r'<'
    t_MAYIGUAL = r'>='
    t_MENIGUAL = r'<='
    t_IGUALBOOL = r'=='
    t_ASIGNACION = r'='
    t_AND = r'&&'
    t_OR = r'\|\|'
    t_NOT = r'!'
    t_LCORCHETE = r"\["
    t_RCORCHETE = r"\]"


    binario = r"(0b[01]+|0B[01]+)"
    hexadecimal = r"(0x[A-Fa-f0-9]+|0X[A-Fa-f0-9]+)"
    octal = r"(0[0-7]+)"
    cientifico = r"([0-9]*[\.,]?[0-9]+(?:e|E)-?[0-9]+)"
    flotante = r"([0-9]+\.[0-9]*|[0-9]*\.[0-9]+)"   #O BIEN 50. O BIEN .50(NUMERO SIEMPRE O DELANATE DEL PUNTO O DETRÁS).
    entero = r"([1-9]+[0-9]*|0)"
    regex_number = r'(' + binario + r'|' + hexadecimal + r'|' + octal + r'|' + cientifico + r'|' + flotante + r'|' + entero + r')'

    @TOKEN(regex_number)
    def t_NUMBER(self, t):
        is_float = False
        if t.value.startswith("0b") or t.value.startswith("0B"):
            t.value = int(t.value[2:], 2)  # Convert binary to integer
        elif t.value.startswith("0x") or t.value.startswith("0X"):
            t.value = int(t.value, 16)  # Convert hexadecimal to integer
        elif t.value.startswith("0") and not ("." in t.value and (len(t.value)>1)) and not ("e" in t.value):
            t.value = int(t.value, 8)  # Convert octal to integer
        elif 'e' in t.value.lower():
            t.value = t.value.replace(',', '.')
            t.value = float(t.value)  # Convert scientific notation to float
        else:
            if (len(t.value)>=1):
                is_float = '.' in t.value
                t.value = float(t.value) if is_float else int(t.value)  # Convert float or integer
        if not is_float:
            t.type = "INT_VALUE"
            t.value = int(t.value)
        else:
            t.type = "FLOAT_VALUE"
        return t

    def t_STR_CON_COMILLAS(self, t):
        r'\"[^"]*\"'
        t.value = t.value[1:-1]     # Eliminar comillas del valor
        if '\n' in t.value:
            return
        return t

    def t_STR_SIN_COMILLAS(self, t):
        r'[a-zA-Z_ñÑ][a-zA-Z0-9_ñÑ]*'
        for key in self.reserved_map.keys():
            if t.value == key:
                t.type = self.reserved_map[key]
                if key == "tr":
                    t.value = True
                elif key == "fl":
                    t.value = False
                elif key == "null":
                    t.value = None
                return t
        return t

    def t_CARACTER(self, t):
        r"\'[\x00-\xFF]\'"
        #t.value = t.value
        if '\n' in t.value:
            return
        t.value = t.value.strip("'")
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count('\n')

    def t_ignore_SCOMMENT(self, t):
        r'//.*(\n|$)'
        t.lexer.lineno += t.value.count('\n')  # Contar el número de líneas correctamente.
        t.value = t.value[:-1]
        pass
    def t_ignore_MCOMMENT(self, t):
        r'/\*(.|\n)*?\*/'
        t.lexer.lineno += t.value.count('\n')  # Contar el número de líneas correctamente.
        a = ""
        for char in t.value:
            if char != "\n":
                a += char
        t.value = a
        pass

    t_ignore = " \t"
    def t_error(self, t):
        print("[Ex1][Lexer] Illegal character", t.value)
        t.lexer.skip(1)

    def test(self, t, file_name):
        self.lexer.input(t)
        to_print = ""
        for token in self.lexer:
            to_print += f"{token.type} {token.value}\n"
        if not os.path.exists(directiorio_salida):
            os.makedirs(directiorio_salida)
        a = ""
        for char in file_name[::-1]:
            if char == "/":
                break
            a += char

        file_name = a[::-1]
        file_path = os.path.join(directiorio_salida, file_name + ".token")
        with open(file_path, 'w') as file:
            file.write(to_print)




