from itertools import zip_longest
from itertools import chain
import lark

# Definição da gramática:
grammar = """root: (state | transition)*
state: "state" STATE "{" (state | transition | internal_transition)* "}"
transition: (STATE | ENDPOINT)? "->" (STATE | ENDPOINT) ":" (TRIGGER ("," TRIGGER)*)? (("[" GUARD "]")? ("/" BEHAVIOR)?)?
internal_transition: ":" TRIGGER (("," TRIGGER)*)? ("[" GUARD "]")? ("/" BEHAVIOR)?

STATE: CNAME
TRIGGER: CNAME
GUARD: ESCAPED_STRING
BEHAVIOR: ESCAPED_STRING
ENDPOINT: "[*]"

%import common.CNAME
%import common.ESCAPED_STRING
%import common.LF
%import common.LETTER
%import common.INT -> NUMBER
%import common.WS
%ignore WS"""
parser = lark.Lark(grammar, start="root")


text = """[*] -> S11 :

    state S1 {
        [*] -> S11 :
        [*] -> S112 : ["foo == 1"] / "foo = 0"
        [*] -> S122 : ["c == 1"] / "c = 0"

        state S11 {
            [*] -> S111 :
            state S111 {

            }
            state S112 {

            }
        }

        state S12 {
            [*] -> S122 :
            state S121 {

            }
            state S122 {

            }
        }

        -> S2 : ev1, ev2, ev3 ["foo == 0"] / "foo = 1"
        -> S21 : EV1
        -> S121 : ev1 ["foo == 1"] / "foo = 0"
    }

    state S2 {
        [*] -> S22 :
        state S21 {

        }
        state S22 {

        }
         : ev11, ev22, ev33, ev44 ["foo == 1"] / "foo = 0"
        -> S1 : ev3 ["foo == 0"] / "foo = 1"
        -> S21 : ev5
    }
    S21 -> S22 : ev21 ["foo == 0"] / "foo = 1"
"""
tree = parser.parse(text)
# print(tree.pretty())


def processa_token(tk):
    print("TOKEN: type = {}, value = {}".format(tk.type, tk.value))


def processa_arvore(a):
    if a.data == "state":
        state, *lst = a.children
        print("STATE: {} - {} children".format(state, len(lst)))
        for el in lst:
            processa_arvore(el)
    elif a.data == "transition":
        src, dest, *rest = a.children
        print("TRANSITION: {} children".format(len(a.children)))
        for el in a.children:
            processa_token(el)
    elif a.data == "internal_transition":
        print("INTERNALTRANSITION: {} children".format(len(a.children)))
    else:
        print("UNKNOWN: {}".format(a.data))


print("\n\n")


for child in tree.children:
    processa_arvore(child)
print("\n\n")

actions = {"root": None,
           "transition": None,
           "state": None}


def processa_transicao(children, current_state):
    # print("Children is ", children)
    if children[1].type in ["STATE", "ENDPOINT"]:
        # Caso em que a descrição da transicao é: S1 -> S2...
        print('children[0] é:', children[0], children[0].type)
        if children[0].type in ["ENDPOINT"]:
            if current_state == '':
                current_state = 'root'
            # Estado inicial, init?, Estado final, Trigger, Guard, Behavior
            transicao = [current_state, children[0].value,
                         children[1].value, [], [], []]
        else:
            # Estado inicial, Estado final, Trigger, Guard, Behavior
            transicao = [children[0].value, children[1].value, [], [], []]
        children = children[1:]
    else:
        # Caso em que a descrição da transicao é: -> S2...
        transicao = [current_state, children[0].value, [], [], []]
        print('Est atual:', current_state, 'Est final:', children[0].value)
    for node in children[1:]:
        # Alterei a localização do trigger, guard e behavior para serem 
        # encontrados de trás para frente, por causa da inclusão de um
        # novo campo quando há transição init
        if node.type == "TRIGGER":
            transicao[-3].append(node.value)
        elif node.type == "GUARD":
            transicao[-2].append(node.value)
        elif node.type == "BEHAVIOR":
            transicao[-1].append(node.value)
        else:
            print("Tipo de nó desconhecido", type(node))

    return transicao


def processa_transicao_interna(children, current_state):
    # print("Transição interna detectada.", children)
    # Nome do estado, Trigger, Guard, Behavior
    transicao_interna = [current_state, [], [], []]
    for node in children:
        if node.type == "TRIGGER":
            transicao_interna[1].append(node.value)
        elif node.type == "GUARD":
            transicao_interna[2].append(node.value)
        elif node.type == "BEHAVIOR":
            transicao_interna[3].append(node.value)
        else:
            print("Tipo de nó desconhecido", type(node))

    return transicao_interna


def processa_estado(parent, children):
    # Nome do estado, Filhos, Pai, Transições, Transições internas
    estado = ["", [], parent, [], []]
    for node in children:
        if type(node) == lark.lexer.Token:
            if node.type == "STATE":
                estado[0] = node.value
                # print("Detectamos um Token: ", node.value)
            else:
                print("Token desconhecido")

        elif type(node) == lark.tree.Tree:
            # print("Detectamos uma Tree: ", node.children[0].value)
            if node.data == "state":
                estado[1].append(processa_estado(estado[0], node.children))
            elif node.data == "transition":
                # já envia a lista de filhos
                estado[3].append(processa_transicao(node.children, estado[0]))
                '''#testar se tem estado inicial'''
            elif node.data == "internal_transition":
                estado[4].append(processa_transicao_interna(
                    node.children, estado[0]))
            else:
                print("Árvore desconhecida: ", node.data)
        else:
            print("Tipo de nó desconhecido", type(node))

    return estado

# Imprime a árvore


def pretty(tree, indentacao=""):
    # actions[tree.data](tree.children)
    print(indentacao + "Data: {}".format(tree.data))
    for node in tree.children:
        if type(node) == lark.tree.Tree:
            print(indentacao + "===Tree===")
            pretty(node, indentacao + "   ")
        else:
            print("{}Child: {}".format(indentacao, node))


'''print(processa_transicao(tree.children[1].children[4].children))'''


'''pretty(tree)'''

''' CORRIGIR: Transições escritas externamente ao estado,
    não são incluídas devidamente no estado correspondente.
    Ficam como transições da root.'''

# Nome do estado, Filhos, Pai, Transições, Transições internas
# root_state = processa_estado(None, tree.children)

# Assumindo que já temos uma lista de estados, outra de transições e
# outra de eventos, faça o código que vai gerar os arquivos finais.
# Depois disso, implemente a parte do código que gerará essas listas.

# Como ler os eventos de uma determinada transição

# Cada elemento / estado do dicionário de estados tem associado a si
# uma lista com os seguintes itens:
#
#     - um dicionário para representar as transições iniciais
#     - um dicionário para representar as transições externas
#     - um dicionário para representar as transições internas
#     - uma lista de strings representando os subestados do estado
#
# As chaves desses dicionários são aqueles elementos que identificam
# de forma única as respectivas transições.  No primeiro dicionário,
# as chaves são as strings representando as condições de guarda
# associadas às várias transições iniciais.  Esse dicionário será
# vazio se o estado não for um super-estado.  Se houver apenas uma
# transição inicial, caso em que necessariamente não haveria condição
# de guarda, a chave seria a string vazia. Cada chave tem associada a
# si uma lista (potencialmente vazia) com duas strings, uma
# representando o estado-destino e outra, a ação.
#
# O segundo e o terceiro dicionários tem como chaves tuplas de duas
# strings representando o evento e a condição de guarda associada (se
# não houver condição de guarda a segunda string será a string vazia).
# No caso do dicionário relativo às transições externas, cada chave
# tem associada a si uma tupla consistindo de duas strings, uma
# representando o estado-destino e a outra a ação associada à
# transição.
#
# Por último, cada chave do terceiro dicionário está associada a uma
# string representando a ação da transição interna.
#
# O quarto elemento dos itens acima é a lista de strings representando
# os subestados.  Esta lista pode ser vazia se o estado não for um
# superestado.  Cada string nesta lista representa um subestado e
# também é uma chave do dicionário de estados.
#
# Só lembrando, um super-estado pode ser identificado pelo seu
# dicionário não-nulo de transições internas
#
# Além do dicionário de estados, acredito que seja útil, embora não
# necessário, um conjunto com todos os eventos encontrados
#
state_dict = {
    "S1": [
        # Transições iniciais - dicionário
        {
            "": ["S11", ""],
            "foo == 1": ["S112", "foo = 0"],
            "c == 1": ["S122", "c = 0" ],
        },
        # Transições externas" - dicionário
        {
            ("ev1", "foo == 0"): ("S2", "foo = 1"),
            ("ev2", "foo == 0"): ("S2", "foo = 1"),
            ("ev3", "foo == 0"): ("S2", "foo = 1"),
            ("EV1", ""): ("S21", ""),
            # Transição local
            ("ev4", "foo == 1"): ("S121", "foo = 0"),
        },
        # Transições internas - dicionário
        {},
        # Lista de subestados
        ["S11", "S22"],
    ],
    "S11": [
        # Transições iniciais - dicionário
        {"": ["S111", ""]},
        # Transições externas" - dicionário
        {},
        # Transições internas - dicionário
        {},
        # Lista de subestados
        ["S111", "S112"],
    ],
    "S111": [
        # Transições iniciais - dicionário
        {},
        # Transições externas" - dicionário
        {},
        # Transições internas - dicionário
        {},
        # Lista de subestados
        [],
    ],
    "S112": [
        # Transições iniciais - dicionário
        {},
        # Transições externas" - dicionário
        {},
        # Transições internas - dicionário
        {},
        # Lista de subestados
        [],
    ],
    "S12": [
        # Transições iniciais - dicionário
        {"": ["S122", ""]},
        # Transições externas" - dicionário
        {},
        # Transições internas - dicionário
        {},
        # Lista de subestados
        ["S121", "S122"],
    ],
    "S121": [
        # Transições iniciais - dicionário
        {},
        # Transições externas" - dicionário
        {},
        # Transições internas - dicionário
        {},
        # Lista de subestados
        [],
    ],
    "S122": [
        # Transições iniciais - dicionário
        {},
        # Transições externas" - dicionário
        {},
        # Transições internas - dicionário
        {},
        # Lista de subestados
        [],
    ],
    "S2": [
        # Transições iniciais - dicionário
        {"": ["S22", ""]},
        # Transições externas" - dicionário
        {
            ("ev3", "foo == 0"): ("S1", "foo = 1"),
            ("ev5", ""): ("S21", ""),
        },
        # Transições internas - dicionário
        {
            ("ev11", "foo == 1"): "foo = 0",
            ("ev22", "foo == 1"): "foo = 0",
            ("ev33", "foo == 1"): "foo = 0",
            ("ev44", "foo == 1"): "foo = 0",
        },
        # Lista de subestados
        ["S21", "S22"],
    ],
    "S21": [
        # Transições iniciais - dicionário
        {},
        # Transições externas" - dicionário
        {("ev21", "foo == 0"): ("S22", "foo = 1")},
        # Transições internas - dicionário
        {},
        # Lista de subestados
        [],
    ],
    "S22": [
        # Transições iniciais - dicionário
        {},
        # Transições externas" - dicionário
        {},
        # Transições internas - dicionário
        {},
        # Lista de subestados
        [],
    ],
}

bottom_up_state_dict = {
    "S1": "[*]",
    "S11": "S1",
    "S111": "S11",
    "S112": "S11",
    "S12": "S1",
    "S121": "S12",
    "S122": "S12",
    "S2": "[*]",
    "S21": "S2",
    "S22": "S2",
}

initial_state = [
    {"": ["S11", ""]},
    {},
    {},
    ["S1", "S2"]
]

# A lista abaixo não deveria ser um conjunto?
# event_list = ['ev1', 'ev2', 'ev3', 'ev11', 'ev22',
#               'ev33', 'ev44', 'ev0', 'ev21', 'EV']

# As duas listas abaixo devem desaarecer?
# state_list = ['S1', 'S11', 'S111', 'S12', 'S121',
#               'S122', 'S2', 'S21', 'S22']

# for event in transition_list[1][-3]:
#     print (event)

#
# Definimos primeiro as strings definindo as várias partes do código
# em C.  Algumas s]ao strings puras, outras strings para formatação
# (contendo {})
#


event_list = list(set(ev for d1, d2, d3, lst
                      in state_dict.values()
                      for (ev, gc) in chain(d2, d3)))


event_header_str = """#include "event.h"
#include "sm.h"

"""
event_enum_begin_str = """enum {{
    {} = USER_EVENT,
"""
event_enum_body_str = """    {},
"""
event_enum_end_str = """};

"""

cb_declaration_str = "cb_status fn_{}_cb(event_t ev);\n"
cb_header_str = """
cb_status init_cb(event_t ev)
{
    top_init_tran();
    return EVENT_HANDLED;
}

"""

cb_definition_begin_str = """cb_status fn_{}_cb(event_t ev)
{{
    switch(ev) {{
    case ENTRY_EVENT:
        return EVENT_HANDLED;
    case EXIT_EVENT:
        return EVENT_HANDLED;
"""
cb_definition_body1_str = """    case INIT_EVENT:
"""
cb_definition_body2_str = """    case EVENT_{}:
"""
cb_definition_body3_str = """
        {}_{}_tran();
        return EVENT_HANDLED;
"""

cb_definition_body4_str = """    case {}:
        if ({}) {{
            {}
            {};
            return EVENT_HANDLED;
        }}
        break;
"""

cb_definition_body5_str = """    case {}:
        if ({}) {{
            {}
            return EVENT_HANDLED;
        }}
        break;
"""

cb_definition_end_str = """    }
    return EVENT_NOT_HANDLED;
}

"""
cb_init_body1_str = """        {}
        {};
        return EVENT_HANDLED;
"""
cb_init_body2_str = """            {}
            {};
            return EVENT_HANDLED;
"""


#
# Definimos agora os geradores que serão
# usados para criar o código linha por linha
#
def events_def(event_list):
    """Generator function to generate the code lines for defining the
events enum"""
    yield event_header_str
    yield event_enum_begin_str.format(event_list[0])
    for event in event_list[1:]:
        yield event_enum_body_str.format(event)
    yield event_enum_end_str


def cb_declarations_def(state_list):
    """Generator dunction to generate the code lines for declaring the
state callback functions"""
    return (cb_declaration_str.format(state) for state in state_list)


def cb_definitions_def(state_dict):
    """Generator function to generate the code lines for defining the
state callback functions"""
    yield cb_header_str
    for state, (d1, d2, d3, lst) in state_dict.items():
        yield cb_definition_begin_str.format(state)
        # Transições iniciais
        if d1:
            yield cb_definition_body1_str.format(state)
            if len(d1) == 1:
                final_state, action = d1[""]
                yield cb_init_body1_str.format(action,
                                               tran_init_name_str.format(state, final_state))
            else:
                ifs_lst = ["".join(["if ({}) {{\n".format(gc),
                           cb_init_body2_str.format(action,
                                                    tran_init_name_str.format(state, final_state)),
                           "        }"])
                           for gc, (final_state, action) in d1.items() if gc]
                ifs_str = " else ".join(ifs_lst)
                final_state, action = d1[""]
                ifs_str += " else {{\n{}\n        }}\n".format(cb_init_body2_str.format(action, tran_init_name_str.format(state, final_state)))
                yield "\t\t" + ifs_str

        # Transições externas
        for (ev, gc), (final_state, action) in d2.items():
            yield cb_definition_body4_str.format(ev, gc, action,
                                                 tran_ext_name_str.format(state, final_state))

        # Transições internas
        for (ev, gc), action in d3.items():
            yield cb_definition_body5_str.format(ev, gc, action)

        yield cb_definition_end_str

#
# Agora, com todos os geradores definidos,
# podemos gerar o arquivo da máquina de estados
#


tran_header_str = '''#ifndef TRANSITIONS_H
#define TRANSITIONS_H

#include "event.h"
#include "sm.h"

'''

tran_top_init_begin_str = """
#define Top_init_tran() do {{\t\t\t\t\\
"""

tran_init_def_begin_str = """
#define {} do {{\t\t\t\\
"""

'''
                exit_inner_states();            \\
                push_state(s1_cb);              \\
                dispatch(ENTRY_EVENT);          \\
                push_state(s11_cb);             \\
                dispatch(ENTRY_EVENT);          \\
        }} while (0)
'''

push_init_path_str = """                push_state(fn_{}_cb);\t\t\t\\
                dispatch(ENTRY_EVENT);\t\t\t\\
"""
dispatch_init_str = "\t\tdispatch(INIT_EVENT);\t\t\t\\\n"

tran_local_begin_str = """
#define {} do {{\t\t\t\\
"""

tran_init_name_str = "fn_{}_init_{}_tran()"
tran_local_name_str = "fn_{}_local_{}_tran()"
tran_ext_name_str = "fn_{}_{}_tran()"

tran_end_str = """
        } while (0)
"""


def transitions1_def():
    global state_dict
    yield tran_header_str.format()


def transitions2_def():
    global state_dict, bottom_up_state_dict
    dest_state = initial_state[0][""][0]
    path, cur_state = [], dest_state
    while cur_state != "[*]":
        path.append(cur_state)
        cur_state = bottom_up_state_dict[cur_state]
    path = path[::-1]

    # Gerando transições iniciais
    yield tran_top_init_begin_str
    for state in path:
        yield push_init_path_str.format(state)
    if state_dict[dest_state][-1]:
        yield dispatch_init_str
    yield tran_end_str

    for src_state, state_info in state_dict.items():
        for gc, (dst_state, action) in state_info[0].items():
            yield tran_init_def_begin_str.format(
                tran_init_name_str.format(src_state, dst_state))
            path, cur_state = [], dst_state
            while cur_state != src_state:
                path.append(cur_state)
                cur_state = bottom_up_state_dict[cur_state]
            path = path[::-1]

            for state in path:
                yield push_init_path_str.format(state)
            if state_dict[dst_state][-1]:
                yield dispatch_init_str
            yield tran_end_str

    # Gerando transições locais     -       Falta ler do dicionário
    src_state, dest_state = "S1", "S122"
    path, cur_state = [], dest_state
    while cur_state != src_state:
        path.append(cur_state)
        cur_state = bottom_up_state_dict[cur_state]
    path = path[::-1]

    yield tran_local_begin_str.format(
        tran_local_name_str.format(src_state, dest_state))
    for state in path:
        yield push_init_path_str.format(state)
    if state_dict[dest_state][-1]:
        yield dispatch_init_str
    yield tran_end_str

    # Gerando transições externas
    src_state, dst_state = "S11", "S2"
    path1, path2, cur_state = [], [], dst_state
    while cur_state != "[*]":
        path2.append(cur_state)
        cur_state = bottom_up_state_dict[cur_state]
    path2 = path2[::-1]

    cur_state = src_state
    while cur_state != "[*]":
        path1.append(cur_state)
        cur_state = bottom_up_state_dict[cur_state]
    path1 = path1[::-1]

    path1 = [el1 for el1, el2 in zip_longest(path1, path2) if el1 != el2]
    path2 = [el2 for el1, el2 in zip_longest(path1, path2) if el1 != el2]
    print(path1)
    print(path2)


with open('main_hsm.c', 'w') as f:
    events_seq = events_def(event_list)
    cb_decl_seq = cb_declarations_def(state_dict.keys())
    cb_def_seq = cb_definitions_def(state_dict)
    f.writelines(chain(events_seq, cb_decl_seq, cb_def_seq))


with open('transitions.h', 'w') as f:
    transitions1_seq = transitions1_def()
    cb_decl_seq = cb_declarations_def(state_dict.keys())
    transitions2_seq = transitions2_def()
    f.writelines(chain(transitions1_seq, cb_decl_seq, transitions2_seq))
