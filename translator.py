"""
var x
var c
var a
var s
print('h')
print(c)
x = 2
c = 'x'
c = input()
d = [11, 22, 33]
e = ['a', 'b', 'c']
print(e[0])
x = (2 + 2) - 3 * 4 / 4
e[0] = 3
var i
i = 2
e[i + 1] = 4
if (x < 10 and x >= 0 or x == 5 and x != 6) {
    x = x + 1
    y = x + 1
} else {
}
var i 
i = 0
while (i < 0) {
    i = i + 1
}
"""

"""
letter ::= "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i"
       | "j" | "k" | "l" | "m" | "n" | "o" | "p"
       | "q" | "r" | "s" | "t" | "u" | "v" | "w"
       | "x" | "y" | "z" 

digit ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"

variable_name ::= letter (letter | digit)*

number ::= ( digit ) +

char ::= "'" <any symbol> "'"

string ::= "\"" <any symbol except a double quote>  "\""

array ::= "[" elements "]"

elements :: = expression | expression "," elements

array_access ::= variable_name "[" expression "]"        

operator ::= "+" | "-" | "*" | "/" | "%" | "==" | "!=" | "<" | ">" | "<=" | ">=" | "and" | "or"

expression ::= 
    number |
    char |
    string |
    array |
    variable_name |
    array_access |
    expression operator expression |
    "(" expression ")" |
    "input" "(" ")" |
    "print" "(" experession ")"
    
statement ::= 
    "var" variable_name |
    "if" "(" expression ")" "{" ( statement ) * "}" 
    ( "else" "{" ( statement ) * "}" ) ? |
    "while" "(" expression ")" "{" ( statement ) * "}" |
    variable_name "=" expression |
    array_access "=" expression

program ::= ( statement ) +
"""
# x = (1 + 2) - 3 * 4 / 5
# 
# 1 2 +  3 4 * 5 /   -
# 
# ld 1            ; a == 1
# {
#     "op_code": "LD",
#     "operand_type": "number",
#     "operand_type": "memory",
#     "operand": 2,
# },
# add 2           ; a == 1 + 2
# st [1000]       ; [1000] == 3
# ld 3            ; a == 3
# mul 4           ; a == 3 * 4
# div 5           ; a == 3 * 4 / 5
# st [1001]       ; [1001] == 2
# ld [1000]       ; a == 3
# sub [1001]      ; 3 - 2
# out
# 
# [ a b c d ] registers
# 
# lda 1001
# add a, 1
# 
# Набор инстркции
# Вычисления
# 
# ADD operand      +
# SUB operand      +
# MUL operand      *
# DIV operand      /
# MOD operand      %
# AND operand      ?
# OR operand       ?
# SHL operand      ?
# SHR operand      ?
# Доступ к памяти
# 
# LD opreand      +
# ST address      +
# Работа со стеком
# 
# PUSH            ?
# POP (The popped element is discarded and not stored in ACC)  ?
# 
# 
# Branching
# 
# CMP operand         +
# JZ address          +
# JNZ address         +
# JB address          +
# JBE address         +
# JA address          +
# JAE address         +
# JMP address         +
# 
# 
# Управление Control Unit
# 
# HLT - Устанавливает флаг HLT в Control Unit   +


# ['var', 'a', 'var', 'b', 'var', 'c', 'print', '(', 'a', ')', 'if', '(', 'c', '>', '5', '{', 'print', '(', 'b', ')', '}']

def tokenize(s):
    separators = {'(', ')', '{', '}', '[', ']', ' ', '\n'}
    result = []
    current_word = ''
    inside_quotes = False
    
    for char in s:
        if char == '"':
            if inside_quotes:
                inside_quotes = False
            else:
                inside_quotes = True
        
        if char in separators and not inside_quotes:
            if current_word:
                result.append(current_word)
                current_word = ''
            if char != ' ' and char != '\n':
                result.append(char)
        else:
            current_word += char

    if current_word:
        result.append(current_word)
    
    return result

#not worked
p1 = """
1 - 2 + 3 * (4 - 5) + 6
"""
#work
p = """
1 + 2 - 3 
"""
#not worked
p2 = """
x + y - x
"""
#work
p3 = """
1 + 2 - 3 var a
""" 
p4 = """
1 + 2 + 3 * 4
""" 

# print(tokenize(p))

# ['x', 'y', 'z']
# 'y'
# 1 * 4  ->  4

def syntax_error():
    print("Syntax error: Invalid syntax.")
    exit(1)

# syntax_error()

def is_name(s):
    if not isinstance(s, str) or not s.isidentifier() or not s.islower():
        return False
    keywords = {'false', 'none', 'true', 'and', 'as', 'assert', 'async', 'await',
                'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
                'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
                'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with',
                'yield', 'var'}
    return s not in keywords    
    
    
# print( is_name('x') )  # true
# print( is_name('x2') )  # true
# print( is_name('abc') )  # true
# print( is_name('var') )  # false
# print( is_name('15') )  # false
# print( is_name('ABC') )  # false 
# print( is_name('') )  # false
# print( is_name(None) )  # false

def is_op(s):
    if not isinstance(s, str):
        return False
    operators = {'<', '<=', '==', '>=', '>', '!=', '+', '-', '*', '/', '%'}
    return s in operators

# print(is_op('<'))     # True
# print(is_op('<='))    # True
# print(is_op('=='))    # True
# print(is_op('>='))    # True
# print(is_op('>'))     # True
# print(is_op('!='))    # True
# print(is_op('+'))     # True
# print(is_op('-'))     # True
# print(is_op('*'))     # True
# print(is_op('/'))     # True
# print(is_op('%'))     # True
# print(is_op('x'))     # False
# print(is_op('123'))   # False
# print(is_op('var'))   # False
# print(is_op(None))    # False

def skip(tokens, position, expected_token):
    if position >= len(tokens):
        syntax_error()
    if tokens[position] != expected_token:
        syntax_error()
    return position + 1

# print( skip(['(', ')'], 0, '(') )   # 1
# print( skip(['(', ')'], 1, ')') )   # 2
# 
# print( skip(['(', ')'], 0, 'a') )   # syntax_error
# print( skip(['(', ')'], 1, 'b') )   # syntax_error

def is_higher_op(new_op, base_op):
    priority = {'*': 2, '/': 2, '%': 2, '+': 1, '-': 1, '<': 0, '<=': 0, '==': 0, '!=': 0, '>=': 0, '>': 0}
    return priority.get(new_op, -1) > priority.get(base_op, -1)

# print( is_higher_op('*', '+') )   # true
# print( is_higher_op('/', '+') )   # true
# print( is_higher_op('%', '+') )   # true
# 
# print( is_higher_op('+', '==') )   # true
# print( is_higher_op('+', '-') )   # false
# 
# print( is_higher_op('+', '<') )   # true
# print( is_higher_op('+', '<=') )   # true
# print( is_higher_op('+', '==') )   # true
# print( is_higher_op('+', '!=') )   # true
# print( is_higher_op('+', '>=') )   # true
# print( is_higher_op('+', '>') )   # true
# 
# print( is_higher_op('xyz', '>') )   # false
# print( is_higher_op(None, '>') )   # false

def get_token(tokens, pos):
    if pos < len(tokens):
        return tokens[pos]
    else:
        return ''

# print( get_token(['a', 'b', 'c'], 0) )  # 'a'
# print( get_token(['a', 'b', 'c'], 1) )  # 'b'
# print( get_token(['a', 'b', 'c'], 2) )  # 'c'
# print( get_token(['a', 'b', 'c'], 3) )  # ''

def arith_opcode(operator):
    opcodes = {'+': 'add', '-': 'sub', '*': 'mul', '/': 'div', '%': 'mod'}
    return opcodes.get(operator, '')

# print( arith_opcode("+") )   # "add"
# print( arith_opcode("-") )   # "sub"
# print( arith_opcode("*") )   # "mul"
# print( arith_opcode("/") )   # "div"
# print( arith_opcode("%") )   # "mod"

def cmp_jump_opcode(operator):
    opcodes = {'<': 'jb', '<=': 'jbe', '==': 'je', '>=': 'jae', '>': 'ja', '!=': 'jne'}
    return opcodes.get(operator, '')

# print( cmp_jump_opcode('<') )   # jb
# print( cmp_jump_opcode('<=') )  # jbe
# print( cmp_jump_opcode('==') )  # je
# print( cmp_jump_opcode('>=') )  # jae
# print( cmp_jump_opcode('>') )   # ja
# print( cmp_jump_opcode('!=') )  # jne
   
#todo: need to complete function for tests: p1, p2
def parse_expression(tokens, pos, program):
    instructions = program["instructions"]
    variables = program["variables"]

    while pos < len(tokens):
        token = tokens[pos]
        
        if pos + 1 < len(tokens):
            next_token = tokens[pos + 1]
        else:
            next_token = None

        if token.isdigit():
            instructions.append({"opcode": "ld", "arg_type": "immediate", "arg": int(token)})
        #todo: except `var`, `if`, `while`, `input`, `print`
        elif token.isalpha() and token.islower():
            instructions.append({"opcode": "ld", "arg_type": "address", "arg": variables[token]})
                
                                    
        elif token == "+":
            if pos + 1 < len(tokens) and tokens[pos + 1].isdigit():
                instructions.append({"opcode": "add", "arg_type": "immediate", "arg": int(tokens[pos + 1])})
                pos += 1
            #todo: except `var`, `if`
            if pos + 1 < len(tokens) and tokens[pos + 1].isalpha() and tokens[pos + 1].islower():
                instructions.append({"opcode": "add", "arg_type": "address", "arg": variables[tokens[pos + 1]]})
            else:
                raise ValueError("Invalid expression")
        elif token == "-":
            if pos + 1 < len(tokens) and tokens[pos + 1].isdigit():
                instructions.append({"opcode": "sub", "arg_type": "immediate", "arg": int(tokens[pos + 1])})
                pos += 1
            else:
                raise ValueError("Invalid expression")
        else:
            break

        pos += 1

    return pos


# parsed_expression = parse_expression(tokenize(p4), 0, [])
# print(parsed_expression)

program = {
    'instructions': [],
    'variables': {"x": 0, "y": 4},
    "data_size": 0,
    ###
}
parse_expression(tokenize("x + y"), 0, program)
print(program)

#result func parse_expression if use test 'p'
[
    {
        "opcode": "ld",
        "arg_type": "immediate",
        "arg": 1
    },
    {
        "opcode": "add",
        "arg_type": "immediate",
        "arg": 2    
    },
    {
        "opcode": "sub",
        "arg_type": "immediate",
        "arg": 3
    },
]

# def parse_statement(tokens, pos, instructors):
#     parse_expression(tokens, pos, instructors)
#     # if tokens[pos] == "var":
#     #     ...
#     # elif tokens[pos] == "if":
# 
# def parse_program(tokens):
#     instructors = []
#     pos = 0
#     while pos < len(tokens):
#         pos = parse_statement(tokens, pos, instructors)
#     return instructors
# 
# print(parse_program(tokenize(p)))

#todo: rewirte to our simplified js 
def sum_even_fibonacci(limit):
    sum_even = 0
    prev = 1
    current = 2
    
    while current <= limit:
        if current % 2 == 0:
            sum_even += current
            
        prev, current = current, prev + current
    
    # print(
    return sum_even

# print(sum_even_fibonacci(4_000_000_000)) # числа 2 и 8 (1, 2, 3, 5, 8)
    
# should be:
# ['var', 'a', 'a', '=', '"hello world"', 'print', 
# '(', 'a', ')', 'if', '(', 'c', '>', '5', ')', 
# '{', 'print', '(', 'b', ')', '}'
