from ajson_lexer import LexerClass
from ajson_parser import Parser
import sys

file = open(sys.argv[1])
data = file.read()



l = LexerClass()
p = Parser()


if len(sys.argv) < 3 or sys.argv[2] == "-par":
    if len(data) <= 2:
        print(">> FICHERO AJSON VACIO", sys.argv[1])
        exit()
    print(">> FICHERO AJSON", sys.argv[1])
    p.test(data, sys.argv[1])
elif sys.argv[2] == "-lex":
    print(">> FICHERO AJSON", sys.argv[1])
    l.test(data, sys.argv[1])
else:
    raise AttributeError("Parámetros de entrada incorrectos")
