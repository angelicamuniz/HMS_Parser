from itertools import zip_longest
from itertools import chain
import sys
import lark

# Definição da gramática:
grammar = """root: (state | transition | initial_transition)*
state: "state" STATE "{" (state | transition | initial_transition | internal_transition | local_transition)* "}"
initial_transition: ENDPOINT "->" STATE ":" ("[" GUARD "]")? ("/" BEHAVIOR)?
local_transition: (STATE)? "->"  "local" (STATE | ENDPOINT) ":" (TRIGGER ("," TRIGGER)*)? ("[" GUARD "]")? ("/" BEHAVIOR)?
transition: (STATE)? "->" (STATE | ENDPOINT) ":" (TRIGGER ("," TRIGGER)*) ("[" GUARD "]")? ("/" BEHAVIOR)?
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

if len(sys.argv) > 1:
    print("Entrei!", sys.argv[1])
    with open(sys.argv[1], "rt") as f:
        text = f.read()
        print(len(text))
else:
    text = """[*] -> S11 :

    state S1 {
        [*] -> S11 :
        [*] -> S112 : ["foo == 1"] / "foo = 0;"
        [*] -> S122 : ["c == 1"] / "c = 0;"

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
        -> S121 : ev4 ["foo == 1"] / "foo = 0;"
    }

    state S2 {
        [*] -> S22 :
        state S21 {

        }
        state S22 {

        }
         : ev11, ev22, ev33, ev44 ["foo == 1"] / "foo = 0;"
        -> S1 : ev3 ["foo == 0"] / "foo = 1;"
        -> S21 : ev5
        -> local S21 : ev6
    }
    S21 -> S22 : ev21 ["foo == 0"] / "foo = 1;"
"""
tree = parser.parse(text)
# print(tree.pretty())

guard_list      = set()
behavior_list   = set()

def parse_states(a, parent, state_dict, bottom_up_state_dict):
    if a.data == "state":
        state, *lst = a.children
        state = state.value
        if state not in state_dict:
            state_dict[state] = [{}, {}, {}, {}, []]
        else:
            print("ERROR: State {} was previously defined!".format(state))
            sys.exit(-1)
        bottom_up_state_dict[state] = parent
        if parent != "[*]":
            state_dict[parent][-1].append(state)
        else:
            initial_state[1].append(state)
        for el in lst:
            state_dict, bottom_up_state_dict = parse_states(el, state,
                                                            state_dict, bottom_up_state_dict)

    return state_dict, bottom_up_state_dict

initial_state = [{}, []]
state_dict, bottom_up_state_dict = {}, {}
for child in tree.children:
    state_dict, bottom_up_state_dict = parse_states(child, "[*]",
                                                    state_dict, bottom_up_state_dict)

def parse_external_local_tran(a, parent, transitions):
    guard, behavior, triggers = "", "", []
    print("Transition has {} grandchildren".format(len(a.children)))
    children = a.children
    (state1, state2), children = children[:2], children[2:]
    if state2.type == "TRIGGER":
        state1, state2, triggers = parent, state1.value, [state2.value]
    else:
        state1, state2 = state1.value, state2.value
    for el in children:
        if el.type == "TRIGGER":
            triggers.append(el.value)
        elif el.type == "GUARD":
            if not guard:
                guard = el.value.strip("\"")
                guard_list.add(guard)
            else:
                print("ERROR: more than one guard condition ({})!".format(el.value))
                sys.exit(-1)
        elif el.type == "BEHAVIOR":
            if not behavior:
                behavior = el.value.strip("\"")
                behavior_list.add(behavior)
            else:
                print("ERROR: more than one behavior ({})!".format(el.value))
                sys.exit(-1)
    if parent == "[*]":
        return
    for trigger in triggers:
        transitions.setdefault(trigger, []).append((state2, behavior, guard))
    print("TRANSITION: {} -> {}: {}{}".format(state1, state2, ", ".join(triggers),
                                              " [{}] / {}".format(guard, behavior)))

def parse_internal_tran(a, parent, transitions):
    guard, behavior, triggers = "", "", []
    print("Transition has {} grandchildren".format(len(a.children)))
    children = a.children
    for el in children:
        if el.type == "TRIGGER":
            triggers.append(el.value)
        elif el.type == "GUARD":
            if not guard:
                guard = el.value.strip("\"")
                guard_list.add(guard)
            else:
                print("ERROR: more than one guard condition ({})!".format(el.value))
                sys.exit(-1)
        elif el.type == "BEHAVIOR":
            if not behavior:
                behavior = el.value.strip("\"")
                behavior_list.add(behavior)
            else:
                print("ERROR: more than one behavior ({})!".format(el.value))
                sys.exit(-1)
    if parent == "[*]":
        return
    for trigger in triggers:
        transitions[(trigger, guard)] = behavior
    print("INTERNAL TRANSITION: : {}{}".format(", ".join(triggers),
                    " [{}] / {}".format(guard, behavior)))

def parse_initial_tran(a, transitions):
    guard, behavior = "", ""
    print("Initial transition has {} grandchildren".format(len(a.children)))
    children = a.children
    (_, state), children = children[:2], children[2:]
    state = state.value
    for el in children:
        if el.type == "GUARD":
            if not guard:
                guard = el.value.strip("\"")
                guard_list.add(guard)
            else:
                print("ERROR: more than one guard condition ({})!".format(el.value))
                sys.exit(-1)
        elif el.type == "BEHAVIOR":
            if not behavior:
                behavior = el.value.strip("\"")
                behavior_list.add(behavior)
            else:
                print("ERROR: more than one behavior ({})!".format(el.value))
                sys.exit(-1)
    transitions[guard] = (state, behavior)
    # print("TRANSITION: {} -> {}: {}{}".format(state1, state2, ", ".join(triggers),
    #                                           " [{}] / {}".format(guard, behavior)))

def parse_transitions(a, parent, state_dict):
    if a.data == "state":
        for el in a.children[1:]:
            parse_transitions(el, a.children[0], state_dict)
    elif a.data == "transition":
        if parent == "[*]":
            return
        if parent not in state_dict:
            print("Error")
            sys.exit(-1)
        parse_external_local_tran(a, parent, state_dict[parent][1])
    elif a.data == "local_transition":
        if parent == "[*]":
            return
        if parent not in state_dict:
            print("Error")
            sys.exit(-1)
        parse_external_local_tran(a, parent, state_dict[parent][2])
    elif a.data == "internal_transition":
        parse_internal_tran(a, parent, state_dict[parent][3])
    elif a.data == "initial_transition":
        if parent == "[*]":
            parse_initial_tran(a, initial_state[0])
        else:
            parse_initial_tran(a, state_dict[parent][0])

for child in tree.children:
    parse_transitions(child, "[*]", state_dict)

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
#     - um dicionário para representar as transições locais
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
# O segundo, o terceiro e o quarto dicionários tem como chaves tuplas de duas
# strings representando o evento e a condição de guarda associada (se
# não houver condição de guarda a segunda string será a string vazia).
# No caso dos dicionários relativos às transições externas e às transições locais (segundo e terceiro dicionários), cada chave
# tem associada a si uma tupla consistindo de duas strings, uma
# representando o estado-destino e a outra a ação associada à
# transição.
#
# Por último, cada chave do quarto dicionário está associada a uma
# string representando a ação da transição interna.
#
# O quinto elemento dos itens acima é a lista de strings representando
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
# state_dict = {
#     "S1": [
#         # Transições iniciais - dicionário
#         {
#             "": ["S11", ""],
#             "foo == 1": ["S112", "foo = 0;"],
#             "c == 1": ["S122", "c = 0;"],
#         },
#         # Transições externas - dicionário
#         {
#             ("ev1", "foo == 0"): ("S2", "foo = 1;"),
#             ("ev2", "foo == 0"): ("S2", "foo = 1;"),
#             ("ev3", "foo == 0"): ("S2", "foo = 1;"),
#             ("EV1", ""): ("S21", ""),
#             ("ev4", "foo == 1"): ("S121", "foo = 0;"),
#         },
#         # Transições locais - dicionário
#         {},
#         # Transições internas - dicionário
#         {},
#         # Lista de subestados
#         ["S11", "S22"],
#     ],
#     "S11": [
#         # Transições iniciais - dicionário
#         {"": ["S111", ""]},
#         # Transições externas" - dicionário
#         {},
#         # Transições locais - dicionário
#         {},
#         # Transições internas - dicionário
#         {},
#         # Lista de subestados
#         ["S111", "S112"],
#     ],
#     "S111": [
#         # Transições iniciais - dicionário
#         {},
#         # Transições externas" - dicionário
#         {},
#         # Transições locais - dicionário
#         {
#             ("ev1", "foo == 2"): ("S1", "foo = 3;")
#         },
#         # Transições internas - dicionário
#         {},
#         # Lista de subestados
#         [],
#     ],
#     "S112": [
#         # Transições iniciais - dicionário
#         {},
#         # Transições externas" - dicionário
#         {
#             ("ev2", ""): ("S1", "foo = 1;")
#         },
#         # Transições locais - dicionário
#         {},
#         # Transições internas - dicionário
#         {},
#         # Lista de subestados
#         [],
#     ],
#     "S12": [
#         # Transições iniciais - dicionário
#         {"": ["S122", ""]},
#         # Transições externas" - dicionário
#         {},
#         # Transições locais - dicionário
#         {},
#         # Transições internas - dicionário
#         {},
#         # Lista de subestados
#         ["S121", "S122"],
#     ],
#     "S121": [
#         # Transições iniciais - dicionário
#         {},
#         # Transições externas" - dicionário
#         {},
#         # Transições locais - dicionário
#         {},
#         # Transições internas - dicionário
#         {},
#         # Lista de subestados
#         [],
#     ],
#     "S122": [
#         # Transições iniciais - dicionário
#         {},
#         # Transições externas" - dicionário
#         {
#             ("ev3", ""): ("S121", "foo = 10;")
#         },
#         # Transições locais - dicionário
#         {},
#         # Transições internas - dicionário
#         {},
#         # Lista de subestados
#         [],
#     ],
#     "S2": [
#         # Transições iniciais - dicionário
#         {"": ["S22", ""]},
#         # Transições externas" - dicionário
#         {
#             ("ev3", "foo == 0"): ("S1", "foo = 1;"),
#             ("ev5", ""): ("S21", ""),
#         },
#         # Transições locais - dicionário
#         {
#             ("ev1", ""): ("S21", ""),
#         },
#         # Transições internas - dicionário
#         {
#             ("ev11", "foo == 1"): "foo = 0;",
#             ("ev22", "foo == 1"): "foo = 0;",
#             ("ev33", "foo == 1"): "foo = 0;",
#             ("ev44", "foo == 1"): "foo = 0;",
#         },
#         # Lista de subestados
#         ["S21", "S22"],
#     ],
#     "S21": [
#         # Transições iniciais - dicionário
#         {},
#         # Transições externas" - dicionário
#         {
#             ("ev21", "foo == 0"): ("S22", "foo = 1;")
#         },
#         # Transições locais - dicionário
#         {},
#         # Transições internas - dicionário
#         {},
#         # Lista de subestados
#         [],
#     ],
#     "S22": [
#         # Transições iniciais - dicionário
#         {},
#         # Transições externas" - dicionário
#         {},
#         # Transições locais - dicionário
#         {},
#         # Transições internas - dicionário
#         {},
#         # Lista de subestados
#         [],
#     ],
# }

# bottom_up_state_dict = {
#     "S1": "[*]",
#     "S11": "S1",
#     "S111": "S11",
#     "S112": "S11",
#     "S12": "S1",
#     "S121": "S12",
#     "S122": "S12",
#     "S2": "[*]",
#     "S21": "S2",
#     "S22": "S2",
# }

# initial_state = [
#     {"": ["S11", ""]},
#     ["S1", "S2"]
# ]

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

event_list = list(set(ev for d1, d2, d3, d4, lst
                      in state_dict.values()
                      for ev in d2))

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

cb_declaration_str = "cb_status {}_cb(event_t ev);\n"
cb_header_str = """
cb_status init_cb(event_t ev)
{
    top_init_tran();
    return EVENT_HANDLED;
}

"""

cb_definition_begin_str = """cb_status {}_cb(event_t ev)
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
            {};
            return EVENT_HANDLED;
        }}
        break;
"""

cb_definition_body6_str = """    case {}:
        {};
        return EVENT_HANDLED;
        break;
"""

cb_case_statement_str = """    case {}:
        {}
        break;
"""

cb_case_body1_str = """if ({}) {{
            {};
            return EVENT_HANDLED;
        }}"""

cb_case_body2_str = """{};
        return EVENT_HANDLED;"""

cb_definition_end_str = """    }
    return EVENT_NOT_HANDLED;
}

"""

cb_init_body1_str = """        {};
        {};
        return EVENT_HANDLED;
"""

cb_init_body12_str = """        {};
        return EVENT_HANDLED;
"""

cb_init_body2_str = """            {};
            {};
            return EVENT_HANDLED;
"""

cb_guard_functions_definitions_str = """
int {}
{{
    /* Desenvolva aqui sua funcao.*/
    return 1;
}}

"""

cb_action_functions_definitions_str = """
int {}
{{
    /* Desenvolva aqui sua funcao.*/
    return 1;
}}

"""

#
# Definimos agora os geradores que serão
# usados para criar o código linha por linha
#

def cb_guard_definitions_def(guard_list):
    for gc in guard_list:
        print ('GC: ',gc)
        print ('Type GC: ', type(gc))
        yield cb_guard_functions_definitions_str.format(gc)


def cb_actions_definitions_def(behavior_list):
    for action in behavior_list:
        yield cb_action_functions_definitions_str.format(action)



def events_def(event_list):
    """Generator function to generate the code lines for defining the
events enum"""
    yield event_header_str
    if event_list:
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

    INDENTATION_SIZE = 4

    def if_gen(gc, action, tran_name):
        case_statements = []
        if action:
            case_statements.append(action)
        if tran_name:
            case_statements.append(tran_name)
        join_str = ";\n" + " "*((3 if gc else 2)*INDENTATION_SIZE)
        lines = join_str.join(case_statements)
        if gc:
            return cb_case_body1_str.format(gc + "()", lines, tran_name)
        else:
            return cb_case_body2_str.format(lines, tran_name)

    yield cb_header_str
    for state, (d1, d2, d3, d4, lst) in state_dict.items():
        yield cb_definition_begin_str.format(state)
        # Transições iniciais
        if d1:
            yield cb_definition_body1_str.format(state)
            if len(d1) == 1:
                final_state, action = d1[""]
                if action:
                    yield cb_init_body1_str.format(action,
                                               tran_init_name_str.format(state, final_state))
                else:
                    yield cb_init_body12_str.format(tran_init_name_str.format(state, final_state))
            else:
                #Aqui não testa se tem ação, então, caso não tenha, aparecerá um ; em seu lugar.
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
        else_join_str = " else "
        for ev, lst in d2.items():
            ifs = else_join_str.join(if_gen(gc, action,
                    tran_ext_name_str.format(state, final_state))
                for final_state, action, gc in lst)
            yield cb_case_statement_str.format(ev, ifs)

        # Transições locais
        for (ev, gc), (final_state, action) in d3.items():
            if gc:
                if action:
                    yield cb_definition_body4_str.format(ev, gc, action,
                                                 tran_local_name_str.format(state, final_state))
                else:
                    yield cb_definition_body42_str.format(ev, gc,
                                                 tran_local_name_str.format(state, final_state))
            else:
                if action:
                    yield cb_definition_body6_str.format(ev, action,
                                                 tran_local_name_str.format(state, final_state))
                else:
                    yield cb_definition_body62_str.format(ev,
                                                 tran_local_name_str.format(state, final_state))

        # Transições internas
        for (ev, gc), action in d4.items():
            if gc:
                yield cb_definition_body4_str.format(ev, gc, action)
            else:
                yield cb_definition_body6_str.format(ev, action)

        yield cb_definition_end_str

#
# Agora, com todos os geradores definidos,
# podemos gerar o arquivo da máquina de estados
#


tran_header_str = '''#ifndef TRANSITIONS_H
#define TRANSITIONS_H

#include "event.h"
#include "sm.h"
#include "guard_and_actions.h"

'''

tran_top_init_begin_str = """
#define Top_init_tran() do {{\t\t\t\t\\
"""

tran_def_begin_str = """
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

push_init_path_str = """                push_state({}_cb);\t\t\t\\
                dispatch(ENTRY_EVENT);\t\t\t\\
"""
dispatch_init_str = "\t\tdispatch(INIT_EVENT);\t\t\t\\\n"

pop_exit_path_str = """                dispatch(EXIT_EVENT);\t\t\t\\
                pop_state();\t\t\t\t\\
"""

tran_local_begin_str = """
#define {} do {{\t\t\t\\
"""

tran_ext_exit_entry_str = """                dispatch(EXIT_EVENT);\t\t\t\\
                dispatch(ENTRY_EVENT);\t\t\t\\
"""

tran_init_name_str = "{}_init_{}_tran()"
tran_local_name_str = "{}_local_{}_tran()"
tran_ext_name_str = "{}_{}_tran()"

tran_end_str = """        } while (0)
"""


def transitions1_def():
    global state_dict
    yield tran_header_str.format()


def transitions2_path_def(path1, path2, local):
    for state in path1[::-1]:
        yield pop_exit_path_str

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
            yield tran_def_begin_str.format(
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

    # Gerando transições locais
    external_trans = False
    for state, (_, _, d3, _, children_lst) in state_dict.items():
        for dst_state, _ in d3.values():
            yield tran_local_begin_str.format(
                 tran_local_name_str.format(state, dst_state))
            path2, cur_state = [], dst_state
            while cur_state != "[*]":
                path2.append(cur_state)
                cur_state = bottom_up_state_dict[cur_state]
            path2 = path2[::-1]

            path1, cur_state = [], state
            while cur_state != "[*]":
                path1.append(cur_state)
                cur_state = bottom_up_state_dict[cur_state]
            path1 = path1[::-1]

            print("-----")
            # print(path1)
            # print(path2)
            path1a = [el1 for el1, el2 in zip_longest(path1, path2) if el1 and el1 != el2]
            path2 = [el2 for el1, el2 in zip_longest(path1, path2) if el2 and el1 != el2]
            path1 = path1a
            print(path1)
            print(path2)
            # print("**********")

            if children_lst:
                yield "\t\texit_inner_states();\t\t\t\\\n"

            for state in path1[::-1]:
                yield pop_exit_path_str
            if (not path1 or not path2) and external_trans:
                yield tran_ext_exit_entry_str
            for state in path2:
                yield push_init_path_str.format(state)
            if state_dict[dst_state][-1]:
                yield dispatch_init_str

        # src_state, dst_state = "S1", "S122"
        # src_state = state
        # for dst_state, _ in d3.values():
        #     path, cur_state = [], dst_state
        #     while cur_state != src_state:
        #         path.append(cur_state)
        #         cur_state = bottom_up_state_dict[cur_state]
        #         path = path[::-1]

        #     yield tran_local_begin_str.format(
        #         tran_local_name_str.format(src_state, dst_state))
        #     for state_p in path:
        #         yield push_init_path_str.format(state_p)
        #         if state_dict[dst_state][-1]:
        #             yield dispatch_init_str
        #             yield tran_end_str

    # Gerando transições externas
    external_trans = True
    for state, (_, d2, _, _, children_lst) in state_dict.items():
        for lst in d2.values():
            for dst_state, _, _ in lst:
                yield tran_def_begin_str.format(
                    tran_ext_name_str.format(state, dst_state))

                if children_lst:
                    yield "\t\texit_inner_states();\t\t\t\\\n"

                path2, cur_state = [], dst_state
                while cur_state != "[*]":
                    path2.append(cur_state)
                    cur_state = bottom_up_state_dict[cur_state]
                path2 = path2[::-1]

                path1, cur_state = [], state
                while cur_state != "[*]":
                    path1.append(cur_state)
                    cur_state = bottom_up_state_dict[cur_state]
                path1 = path1[::-1]

                print("-----")
                # print(path1)
                # print(path2)
                path1a = [el1 for el1, el2 in zip_longest(path1, path2) if el1 and el1 != el2]
                path2 = [el2 for el1, el2 in zip_longest(path1, path2) if el2 and el1 != el2]
                path1 = path1a
                print(path1)
                print(path2)
                # print("**********")

                for state in path1[::-1]:
                    yield pop_exit_path_str
                if (not path1 or not path2) and external_trans:
                    yield tran_ext_exit_entry_str
                for state in path2:
                    yield push_init_path_str.format(state)
                if state_dict[dst_state][-1]:
                    yield dispatch_init_str


                # for el in path1[1:][::-1]:
                #     yield pop_exit_path_str

                # parent = bottom_up_state_dict[path1[0]]

                yield tran_end_str


smh_str = """#ifndef SM_H
#define SM_H

#include <stdint.h>
#include "event.h"

typedef uint8_t cb_status;
enum {
        EVENT_HANDLED = 0,
        EVENT_NOT_HANDLED
};

enum {
        EMPTY_EVENT = EVENT0,
        ENTRY_EVENT = EVENT1,
        EXIT_EVENT  = EVENT2,
        INIT_EVENT  = EVENT3,
        USER_EVENT  = EVENT4
};

typedef cb_status (*cb_t)(event_t ev);
typedef cb_t state_t;

#define MAX_ACTIVE_STATES 10
extern state_t *_p_state;
extern uint8_t _state_stack_len;

void init_machine(cb_t init_fun);

#define dispatch(ev) (*_p_state)(ev)
#define push_state(st) *++_p_state = (st)
#define pop_state() _p_state--
#define replace_state(st) *_p_state = (st)
#define exit_inner_states()                     \\
        do {                                    \\
                _p_state += _state_stack_len;   \\
                while (_state_stack_len) {      \\
                        dispatch(EXIT_EVENT);   \\
                        pop_state();            \\
                        _state_stack_len--;     \\
                }                               \\
        } while(0)

#define dispatch_event(ev) do {                                 \\
        _state_stack_len = 0;                                   \\
        while(*_p_state) {                                      \\
                if (dispatch(ev) == EVENT_HANDLED) {            \\
                        _p_state += _state_stack_len;           \\
                        break;                                  \\
                }                                               \\
                _state_stack_len++;                             \\
                pop_state();                                    \\
        }                                                       \\
        if (!*_p_state) {                                       \\
                _p_state += _state_stack_len;                   \\
                _state_stack_len = 0;                           \\
        }                                                       \\
        } while (0)

#endif /* SM_H */
"""

eventh_str="""#ifndef EVENTS_H
#define EVENTS_H

#include <stdint.h>

typedef uint16_t event_t;

event_t wait_for_events(void);
event_t test_for_event(event_t);

extern volatile event_t _events;
#define set_event(ev)                           \\
        do {                                    \\
                enter_critical_region();        \\
                _events |= (1 << (ev));         \\
                leave_critical_region();        \\
        } while (0)

#define MAX_EVENTS 16

enum {
    EVENT0 = 0,
    EVENT1,
    EVENT2,
    EVENT3,
    EVENT4,
    EVENT5,
    EVENT6,
    EVENT7,
    EVENT8,
    EVENT9,
    EVENT10,
    EVENT11,
    EVENT12,
    EVENT13,
    EVENT14,
    EVENT15
};

#endif /* EVENTS_H */
"""

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

with open('guard_and_actions.h', 'w') as f:
    functions_gc = (guard_list)
    functions_actions = cb_actions_definitions_def(behavior_list)
    f.writelines(chain(functions_gc, functions_actions))

with open('sm.h', 'w') as f:
    f.writelines(smh_str)
    
with open('event.h',  'w') as f:
    f.writelines(eventh_str)

print('guard list: ', guard_list)
print('behavior list: ',behavior_list)


































