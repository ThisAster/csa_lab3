# Отчёт по лабораторной работе №3

- Выполнил: Абульфатов Руслан
- Группа: P33312
- Вариант: `alg | acc | harv | mc | tick | struct | stream | port | cstr | prob2 | [4]char`

## Язык программирования

По варианту необходимо реализовать Java/JavaScript/Lua-подобный язык.

Был реализован JavaScript-подобный язык с различными упрощениями.

Реализована поддержка:
* создание переменных
* числовые и строковые литералы
* математические выражения с приоритетами и группировкой `()`
* ветвление `if`
* цикл `while`
* посимвольный ввод/вывод

Грамматика языка:

```ebnf
letter ::= "a" | "b" | "c" | "d" | "e" | "f" | "g" | 
       "h" | "i" | "j" | "k" | "l" | "m" | "n" | 
       "o" | "p" | "q" | "r" | "s" | "t" | "u" | 
       "v" | "w" | "x" | "y" | "z" 

digit ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"

variable_name ::= letter (letter | digit)*

number ::= digit+

string ::= "\"" <any symbol except a double quote>  "\""

string_access ::= variable_name "[" expression "]"        

operator ::= 
    "+" | "-" | "*" | "/" | "%" | 
    "==" | "!=" | "<" | ">" | "<=" | ">=" 
    
expression ::= 
    number |
    variable_name |
    string_access |
    expression operator expression |
    "(" expression ")" |
    "input" "(" ")" 

statement ::= 
    "var" variable_name |
    "if" "(" expression ")" "{" statement* "}" |
    "while" "(" expression ")" "{" statement* "}" |
    variable_name "=" expression |
    variable_name "=" string | 
    string_access "=" expression |
    "print" "(" experession ")"

program ::= statement*
```

Вычисления производятся последовательно, за исключением ветвления и циклов. 

Область видимости всех переменных - глобальная, потому что нет поддержки функций и процедур.

Язык поддерживает два типа данных:

* 32-битное знаковое целое число
* строка (C-string)

Булевые литералы не поддерживаются для упрощения языка, но операции сравнения (`==`, `!=`, `<` и т. д.) возвращают `1` или `0` -- в зависимости от результата сравнения. Операции сравнения не являются частью конструкций `if` и `while`, и могут использоваться в любом контексте.

`print` и `input` осуществляют ввод/вывод посимвольно. Один символ выводится или вводится за один вызов.

Комментарии не поддерживаются для упрощения транслятора.

## Организация памяти

Используется гарвардская модель памяти с разделением на память инструкций и память данных.

Память инструкций: машинное слово -- не определено. Реализуется списком словарей, описывающих инструкции (одно слово -- одна ячейка).

Память данных: машинное слово -- 32-битное целое, знаковое. Линейное адресное пространство. Реализуется списком чисел.

Числовые константы не выделяются в памяти данных, потому что они являются частью инструкций загрузки, сложения и т. д. Например, `LD 5` загружает число `5` в `ACC`, при этом само число является частью инструкции. 

Также транслятор может создавать временные числовые переменные при трансляции выражений для сохранения промежуточных результатов, например, при разборе составных математических выражений со скобками. Обращение к данным временным переменным происходит при помощи прямой адресации. Временные переменные также выделяются в памяти данных последовательно, по мере необходимости.

Строки сохраняются в памяти данных последовательно по мере обнаружения их в программе транслятором. Один символ - одна ячейка памяти. Когда строковые переменные встречаются в программе, транслятор использует их адрес в памяти данных.

Программисту доступен один регистр `ACC` (аккумулятор), все вычисления производятся с его участием. Так как регистр всего один, то никакие переменные не отображаются на него.

## Система команд

Особенности процессора:

* Аккумуляторная архитектура
* 32-битное машинное слово
* Доступ к памяти инструкций осуществляется по адресу, хранимому в специальном регистре `PC`.
* Доступ к памяти микро-инструкций осуществляется по адресу, хранимому в специальном регистре `mPC`.
* Доступ к памяти данных осуществляется по адресу, хранимому в специальном регистре `data_address`.
* Поток управления: 
 * инкремент `mPC` после каждой микро-инструкции;
 * инкремент `PC` после каждой инструкции;
 * условные (je, jne, jg, jl, jge, jle) и безусловный (jmp) переходы сбрасывают `PC` на адрес целевой инструкции

### Набор инструкций 

| Инструкция  | Тип аргумента    | Кол-во тактов  | Пояснение                                          |
|:------------|------------------|:---------------|:---------------------------------------------------|
| LD          | immediate        | 2              | Загрузка числа в ACC 
| LD          | address          | 3              | Прямая адресация
| LD          | indirect_address | 5              | Косвенная адресация
| ST          | address          | 3              | Сохранение ACC по адресу
| ST          | indirect_address | 4              | Косвенная адресация
| ADD         | immediate        | 2              | Прибавить число к ACC
| ADD         | address          | 3              | Прямая адресация
| SUB         | immediate        | 2              | Прибавить число к ACC
| SUB         | address          | 3              | Прямая адресация
| MUL         | immediate        | 2              | Прибавить число к ACC
| MUL         | address          | 3              | Прямая адресация
| DIV         | immediate        | 2              | Прибавить число к ACC
| DIV         | address          | 3              | Прямая адресация
| MOD         | immediate        | 2              | Прибавить число к ACC
| MOD         | address          | 3              | Прямая адресация
| JMP         | address          | 2              | Безусловный переход
| JE          | address          | 2              | Переход при равенстве
| JNE         | address          | 2              | Переход при неравенстве
| JG          | address          | 2              | Переход, если больше
| JL          | address          | 2              | Переход, если меньше
| JGE         | address          | 2              | Переход, если больше или равно
| JLE         | address          | 2              | Переход, если меньше или равно
| IN          | address          | 3              | Ввод из порта   
| OUT         | address          | 2              | Вывод в порт
| HLT         | (нет аргумента)  | 2              | Останов


### Способ кодирования инструкций

* Машинный код сериализуется в список JSON.
* Один элемент списка -- одна инструкция.
* Индекс списка -- адрес инструкции. Используется для команд перехода.

```json
{
    "opcode": "add",
    "arg_type": "address",
    "arg": 5
}
```
где:
* `opcode` -- строка с кодом операции;
* `arg_type` -- тип аргумента (например, `immediate`, `address`)
* `arg` -- аргумент (отсутствует у инструкции `HLT`);

## Транслятор

Интерфейс командной строки: 

```
python3 translator.py <input_file> <output_code> <output_data>
```

где
* `input_file` - имя файла с программой на языке программирования
* `output_code` - имя файла для записи списка инструкций в формате JSON
* `output_data` - имя файла для записи памяти данных в формате JSON

Этапы трансляции:

1. Трансформирование текста в последовательность значимых токенов.
2. Парсинг токенов с одновременной генерацией машинного кода.

Правила генерации машинного кода:

* Один токен языка -- одна или несколько инструкций;
* Код для математических выражений генерируется слева направо, все вычисления происходят на аккумуляторе. При необходимости автоматически создаются временные переменные, если вычисление выражения невозможно произвести используя только аккумулятор
* Простые присвоения порождают инструкцию `ST` с предварительным вычислением правой части от знака присвоения `=`. (Пример инструкции: `x = 5`) 
* Присвоения к элементы строки порождают инструкцию `ST` с предварительным вычислением адреса символа на основе индекса и с вычислением правой части от знака присвоения `=` (Пример инструкции: `s[i] = 97`) 
* Для ветвления `if` генерируются инструкция перехода `JE` (прыжок через тело конструкции):

| Номер инструкции | Программа       | Машинный код               |
| ---------------- | --------------- | -------------------------- |
| n                | if (условие)    | (вычисление условия)       |
| n + 1            |                 | je k                       |
| ...              | ...             | (тело условного оператора) |
| k                | ...             | ...                        |

Перед генерацией `JE` генерируется код, вычисляющий значение условия `if`.
* Для цикла `while` генерируются инструкция перехода `JE` (прыжок через тело конструкции):

| Номер инструкции | Программа       | Машинный код         |
| ---------------- | --------------- | -------------------- |
| n                | while (условие) | (вычисление условия) |
| n + 1            |                 | je k + 1             |
| ...              | ...             | (тело цикла)         |
| k                | }               | jmp n                |
| k + 1            | ...             | ...                  |

Перед генерацией `JE` генерируется код, вычисляющий значение условия `while`.
* Ключевое слово `print` генерирует инструкцию вывода в порт -- `OUT`
* Ключевое слово `input` генерирует инструкцию ввода из порта -- `IN`


## Модель процессора

Интерфейс командной строки: 

```
python3 machine.py <input_code> <input_data> <input_file>
```

где
* `input_code` - имя файла с программой на языке программирования
* `input_data` - имя файла с описанием памяти данных в формате JSON
* `input_file` - имя файла с входным буффером для симулятора

Проргамма выводит журнал работы симулятора и выход данных процессора на экран.

### Data Path

************************* СХЕМА DATA PATH *************************
************************* СХЕМА DATA PATH *************************
************************* СХЕМА DATA PATH *************************

Реализован в классе DataPath.

`data_memory` -- однопортовая память, поэтому либо читаем, либо пишем.

Сигналы (обрабатываются за один такт):

* `latch_data_address` -- защёлкнуть выбранное значение в регистр `data_address`:
    * выход из модуля памяти (`data_out`)
    * операнд инструкции (`instruction_arg`)
* `data_read` -- перевод памяти в режим чтения
* `data_write` -- записать аккумулятор в память
* `latch_acc` -- защёлкнуть в аккумулятор выбранное значение:
    * операнд инструкции (`instruction_arg`)
    * значение из входного буфера (обработка на Python):
        * извлечь из входного буфера значение и записать в память
        * если буфер пуст -- выбросить исключение
    * выход из модуля памяти (`data_out`)
    * результат вычислений на АЛУ
* `output_write` -- записать аккумулятор в порт вывода (обработка на Python).
* АЛУ выполняет операцию, заданную `alu_operation_sel`:
    * левый операнд -- всегда аккумулятор
    * правый операнд выбирается на основании сигнала `alu_operand_sel`:
        * выход из модуля памяти (`data_out`)
        * операнд инструкции (`instruction_arg`)

Флаги:

* `negative_flag` -- отражает наличие отрицательного значения в аккумуляторе.
* `zero_flag` -- отражает наличие нулевого значения в аккумуляторе.
* `positive_flag` -- отражает наличие положительного значения в аккумуляторе.



### Control Unit

************************* CONTROL UNIT *************************
************************* CONTROL UNIT *************************
************************* CONTROL UNIT *************************

Реализован в классе ControlUnit.

`code_memory` -- однопортовая память, поэтому либо читаем, либо пишем. Всегда находится в режиме чтения.

`micro_code_memory` -- однопортовая память, поэтому либо читаем, либо пишем. Всегда находится в режиме чтения.

Сигналы:
* `latch_pc` - записать в регистр `PC` выбранное значение:
    * аргумент инструкции перехода (`JMP`, `JE`, `JG` и т.д.)
    * адрес следующей инструкции
* `mpc_sel` - записать в регистр `mPC` выбранное значение:
    * ноль - выбор специальной микро-инструкции для загрузки нового микрокода (выбирается при переходе к новой инструкции)
    * адрес, приходящий с декодера инструкции (используется, когда новая инструкция уже выбрана в памяти инструкций)
    * адрес следующей микро-инструкции
* `jump_if_negative`, `jump_if_zero`, `jump_if_positive` - активные, если необходимо сделать условный или безусловный прыжок (данные сигналы сигналы показывают условие перехода)


## Тестирование

В качестве тестов использовано четыре задачи:

1. hello world -- программа, выводящая "hello world"
2. cat -- программа cat, повторяем ввод на выводе.
3. hello user name -- программа, приветствующая пользователя
4. prob2 -- подсчёт чётных чисел Фибоннаячи до 4000000

Интеграционные тесты реализованы в файле `tests/test_golden.py` с использованием golden-тестов.

CI:

```yaml
name: CI

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

permissions:
  contents: read

jobs:

  lint:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry
          poetry install --no-root

      - name: Check code formatting with Ruff
        run: |
          poetry run ruff format --check .

      - name: Run Ruff linters
        run: |
          poetry run ruff check .

  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry
          poetry install

      - name: Run tests
        run: |
          poetry run pytest ./tests -v
```

* Все задачи запускаются на образе ОС `ubuntu-latest`.
* Устанавливается `Python`
* Устанавливается менеджер пакетов `poetry`
* Устанавливаются зависимости:
    * ruff -- утилита для форматирования и проверки стиля кодирования.
    * pytest -- утилита для запуска тестов.
* Запускаются линтер, форматтер и тесты

Пример использования и журнал работы процессора на примере `cat`:

```
$ cat cat.js
var char
while (1) {
   char = input()
   print(char)
}
$ cat cat.txt
foo
$ python3 translator.py cat.js cat.code cat.data
LoC: 5, code instructinos: 8
$ python3 machine.py cat.code cat.data cat.txt
tick #1: PC=0 MPC=1 ACC=0 DA=0 DOUT=None  LD 1
input=['f', 'o', 'o', '\n'] output=[]
tick #2: PC=1 MPC=0 ACC=1 DA=0 DOUT=None  JE 7
input=['f', 'o', 'o', '\n'] output=[]
tick #3: PC=1 MPC=22 ACC=1 DA=0 DOUT=None  JE 7
input=['f', 'o', 'o', '\n'] output=[]
tick #4: PC=2 MPC=0 ACC=1 DA=0 DOUT=None  IN 0
input=['f', 'o', 'o', '\n'] output=[]
tick #5: PC=2 MPC=28 ACC=1 DA=0 DOUT=None  IN 0
input=['f', 'o', 'o', '\n'] output=[]
tick #6: PC=2 MPC=29 ACC=1 DA=0 DOUT=None  IN 0
input=['o', 'o', '\n'] output=[]
tick #7: PC=3 MPC=0 ACC=102 DA=0 DOUT=None  ST [0]
input=['o', 'o', '\n'] output=[]
tick #8: PC=3 MPC=9 ACC=102 DA=0 DOUT=None  ST [0]
input=['o', 'o', '\n'] output=[]
tick #9: PC=3 MPC=10 ACC=102 DA=0 DOUT=None  ST [0]
input=['o', 'o', '\n'] output=[]
tick #10: PC=4 MPC=0 ACC=102 DA=0 DOUT=None  LD [0]
input=['o', 'o', '\n'] output=[]
tick #11: PC=4 MPC=7 ACC=102 DA=0 DOUT=None  LD [0]
input=['o', 'o', '\n'] output=[]
tick #12: PC=4 MPC=8 ACC=102 DA=0 DOUT=102  LD [0]
input=['o', 'o', '\n'] output=[]
tick #13: PC=5 MPC=0 ACC=102 DA=0 DOUT=None  OUT 0
input=['o', 'o', '\n'] output=[]
tick #14: PC=5 MPC=30 ACC=102 DA=0 DOUT=None  OUT 0
input=['o', 'o', '\n'] output=[]
tick #15: PC=6 MPC=0 ACC=102 DA=0 DOUT=None  JMP 0
input=['o', 'o', '\n'] output=['f']
tick #16: PC=6 MPC=21 ACC=102 DA=0 DOUT=None  JMP 0
input=['o', 'o', '\n'] output=['f']
tick #17: PC=0 MPC=0 ACC=102 DA=0 DOUT=None  LD 1
input=['o', 'o', '\n'] output=['f']
tick #18: PC=0 MPC=1 ACC=102 DA=0 DOUT=None  LD 1
input=['o', 'o', '\n'] output=['f']
tick #19: PC=1 MPC=0 ACC=1 DA=0 DOUT=None  JE 7
input=['o', 'o', '\n'] output=['f']
tick #20: PC=1 MPC=22 ACC=1 DA=0 DOUT=None  JE 7
input=['o', 'o', '\n'] output=['f']
tick #21: PC=2 MPC=0 ACC=1 DA=0 DOUT=None  IN 0
input=['o', 'o', '\n'] output=['f']
tick #22: PC=2 MPC=28 ACC=1 DA=0 DOUT=None  IN 0
input=['o', 'o', '\n'] output=['f']
tick #23: PC=2 MPC=29 ACC=1 DA=0 DOUT=None  IN 0
input=['o', '\n'] output=['f']
tick #24: PC=3 MPC=0 ACC=111 DA=0 DOUT=None  ST [0]
input=['o', '\n'] output=['f']
tick #25: PC=3 MPC=9 ACC=111 DA=0 DOUT=None  ST [0]
input=['o', '\n'] output=['f']
tick #26: PC=3 MPC=10 ACC=111 DA=0 DOUT=None  ST [0]
input=['o', '\n'] output=['f']
tick #27: PC=4 MPC=0 ACC=111 DA=0 DOUT=None  LD [0]
input=['o', '\n'] output=['f']
tick #28: PC=4 MPC=7 ACC=111 DA=0 DOUT=None  LD [0]
input=['o', '\n'] output=['f']
tick #29: PC=4 MPC=8 ACC=111 DA=0 DOUT=111  LD [0]
input=['o', '\n'] output=['f']
tick #30: PC=5 MPC=0 ACC=111 DA=0 DOUT=None  OUT 0
input=['o', '\n'] output=['f']
tick #31: PC=5 MPC=30 ACC=111 DA=0 DOUT=None  OUT 0
input=['o', '\n'] output=['f']
tick #32: PC=6 MPC=0 ACC=111 DA=0 DOUT=None  JMP 0
input=['o', '\n'] output=['f', 'o']
tick #33: PC=6 MPC=21 ACC=111 DA=0 DOUT=None  JMP 0
input=['o', '\n'] output=['f', 'o']
tick #34: PC=0 MPC=0 ACC=111 DA=0 DOUT=None  LD 1
input=['o', '\n'] output=['f', 'o']
tick #35: PC=0 MPC=1 ACC=111 DA=0 DOUT=None  LD 1
input=['o', '\n'] output=['f', 'o']
tick #36: PC=1 MPC=0 ACC=1 DA=0 DOUT=None  JE 7
input=['o', '\n'] output=['f', 'o']
tick #37: PC=1 MPC=22 ACC=1 DA=0 DOUT=None  JE 7
input=['o', '\n'] output=['f', 'o']
tick #38: PC=2 MPC=0 ACC=1 DA=0 DOUT=None  IN 0
input=['o', '\n'] output=['f', 'o']
tick #39: PC=2 MPC=28 ACC=1 DA=0 DOUT=None  IN 0
input=['o', '\n'] output=['f', 'o']
tick #40: PC=2 MPC=29 ACC=1 DA=0 DOUT=None  IN 0
input=['\n'] output=['f', 'o']
tick #41: PC=3 MPC=0 ACC=111 DA=0 DOUT=None  ST [0]
input=['\n'] output=['f', 'o']
tick #42: PC=3 MPC=9 ACC=111 DA=0 DOUT=None  ST [0]
input=['\n'] output=['f', 'o']
tick #43: PC=3 MPC=10 ACC=111 DA=0 DOUT=None  ST [0]
input=['\n'] output=['f', 'o']
tick #44: PC=4 MPC=0 ACC=111 DA=0 DOUT=None  LD [0]
input=['\n'] output=['f', 'o']
tick #45: PC=4 MPC=7 ACC=111 DA=0 DOUT=None  LD [0]
input=['\n'] output=['f', 'o']
tick #46: PC=4 MPC=8 ACC=111 DA=0 DOUT=111  LD [0]
input=['\n'] output=['f', 'o']
tick #47: PC=5 MPC=0 ACC=111 DA=0 DOUT=None  OUT 0
input=['\n'] output=['f', 'o']
tick #48: PC=5 MPC=30 ACC=111 DA=0 DOUT=None  OUT 0
input=['\n'] output=['f', 'o']
tick #49: PC=6 MPC=0 ACC=111 DA=0 DOUT=None  JMP 0
input=['\n'] output=['f', 'o', 'o']
tick #50: PC=6 MPC=21 ACC=111 DA=0 DOUT=None  JMP 0
input=['\n'] output=['f', 'o', 'o']
tick #51: PC=0 MPC=0 ACC=111 DA=0 DOUT=None  LD 1
input=['\n'] output=['f', 'o', 'o']
tick #52: PC=0 MPC=1 ACC=111 DA=0 DOUT=None  LD 1
input=['\n'] output=['f', 'o', 'o']
tick #53: PC=1 MPC=0 ACC=1 DA=0 DOUT=None  JE 7
input=['\n'] output=['f', 'o', 'o']
tick #54: PC=1 MPC=22 ACC=1 DA=0 DOUT=None  JE 7
input=['\n'] output=['f', 'o', 'o']
tick #55: PC=2 MPC=0 ACC=1 DA=0 DOUT=None  IN 0
input=['\n'] output=['f', 'o', 'o']
tick #56: PC=2 MPC=28 ACC=1 DA=0 DOUT=None  IN 0
input=['\n'] output=['f', 'o', 'o']
tick #57: PC=2 MPC=29 ACC=1 DA=0 DOUT=None  IN 0
input=[] output=['f', 'o', 'o']
tick #58: PC=3 MPC=0 ACC=10 DA=0 DOUT=None  ST [0]
input=[] output=['f', 'o', 'o']
tick #59: PC=3 MPC=9 ACC=10 DA=0 DOUT=None  ST [0]
input=[] output=['f', 'o', 'o']
tick #60: PC=3 MPC=10 ACC=10 DA=0 DOUT=None  ST [0]
input=[] output=['f', 'o', 'o']
tick #61: PC=4 MPC=0 ACC=10 DA=0 DOUT=None  LD [0]
input=[] output=['f', 'o', 'o']
tick #62: PC=4 MPC=7 ACC=10 DA=0 DOUT=None  LD [0]
input=[] output=['f', 'o', 'o']
tick #63: PC=4 MPC=8 ACC=10 DA=0 DOUT=10  LD [0]
input=[] output=['f', 'o', 'o']
tick #64: PC=5 MPC=0 ACC=10 DA=0 DOUT=None  OUT 0
input=[] output=['f', 'o', 'o']
tick #65: PC=5 MPC=30 ACC=10 DA=0 DOUT=None  OUT 0
input=[] output=['f', 'o', 'o']
tick #66: PC=6 MPC=0 ACC=10 DA=0 DOUT=None  JMP 0
input=[] output=['f', 'o', 'o', '\n']
tick #67: PC=6 MPC=21 ACC=10 DA=0 DOUT=None  JMP 0
input=[] output=['f', 'o', 'o', '\n']
tick #68: PC=0 MPC=0 ACC=10 DA=0 DOUT=None  LD 1
input=[] output=['f', 'o', 'o', '\n']
tick #69: PC=0 MPC=1 ACC=10 DA=0 DOUT=None  LD 1
input=[] output=['f', 'o', 'o', '\n']
tick #70: PC=1 MPC=0 ACC=1 DA=0 DOUT=None  JE 7
input=[] output=['f', 'o', 'o', '\n']
tick #71: PC=1 MPC=22 ACC=1 DA=0 DOUT=None  JE 7
input=[] output=['f', 'o', 'o', '\n']
tick #72: PC=2 MPC=0 ACC=1 DA=0 DOUT=None  IN 0
input=[] output=['f', 'o', 'o', '\n']
tick #73: PC=2 MPC=28 ACC=1 DA=0 DOUT=None  IN 0
input=[] output=['f', 'o', 'o', '\n']
end of input - simulation terminated
instructions executed: 31, ticks: 73
output=['f', 'o', 'o', '\n']
```

Пример проверки исходного кода:

```
============================= test session starts ==============================
platform linux -- Python 3.11.8, pytest-7.4.4, pluggy-1.4.0 -- /home/runner/.cache/pypoetry/virtualenvs/test-ci-ZmaL7ir5-py3.11/bin/python
cachedir: .pytest_cache
rootdir: /home/runner/work/csa_lab3/csa_lab3
configfile: pyproject.toml
plugins: golden-0.2.2
collecting ... collected 4 items

tests/test_golden.py::test_golden[cat.yaml] PASSED                       [ 25%]
tests/test_golden.py::test_golden[hello.yaml] PASSED                     [ 50%]
tests/test_golden.py::test_golden[fib.yaml] PASSED                       [ 75%]
tests/test_golden.py::test_golden[hello_user.yaml] PASSED                [100%]
```

```
| ФИО                         | алг        | LoC | code байт | code инстр. | инстр. | такт. | вариант                                                                        |
| Абульфатов Руслан Мехтиевич | cat        | 5   | -         | 8           | 31     | 73    | alg | acc | harv | mc | tick | struct | stream | port | cstr | prob2 | [4]char |
| Абульфатов Руслан Мехтиевич | fib        | 30  | -         | 72          | 888    | 2225  | alg | acc | harv | mc | tick | struct | stream | port | cstr | prob2 | [4]char |
| Абульфатов Руслан Мехтиевич | hello      | 8   | -         | 23          | 750    | 2008  | alg | acc | harv | mc | tick | struct | stream | port | cstr | prob2 | [4]char |
| Абульфатов Руслан Мехтиевич | hello_user | 36  | -         | 118         | 187    | 497   | alg | acc | harv | mc | tick | struct | stream | port | cstr | prob2 | [4]char |
```
