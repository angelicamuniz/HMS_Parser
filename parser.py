from itertools import zip_longest
from itertools import chain
import sys
import lark
use_avr = 0

# Definição da gramática:
grammar = """root: (state | transition | initial_transition)*
state: "state" STATE "{" (state | transition | initial_transition | internal_transition | local_transition | behavior_entry | behavior_exit)* "}"
initial_transition: ENDPOINT "->" STATE ":" ("[" GUARD "]")? ("/" BEHAVIOR)?
local_transition: (STATE)? "->"  "local" (STATE | ENDPOINT) ":" (TRIGGER ("," TRIGGER)*)? ("[" GUARD "]")? ("/" BEHAVIOR)?
transition: (STATE)? "->" (STATE | ENDPOINT) ":" (TRIGGER ("," TRIGGER)*) ("[" GUARD "]")? ("/" BEHAVIOR)?
internal_transition: ":" TRIGGER (("," TRIGGER)*)? ("[" GUARD "]")? ("/" BEHAVIOR)?
behavior_entry: "ENTRY" BEHAVIOR
behavior_exit: "EXIT" BEHAVIOR

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
    try:
    	(arquivo, arquitetura) = sys.argv[1].split(',')
    	if (arquitetura == 'avr'):
    		use_avr = 1
    except:
    	arquivo = sys.argv[1]
    with open(arquivo, "rt") as f:
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

def parse_behavior_entry(a, state_dict):
    pass

def parse_behavior_exit(a, state_dict):
    pass

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
    elif a.data == "behavior_entry":
        parse_behavior_entry(a, state_dict[parent][3])
    elif a.data == "behavior_exit":
        parse_behavior_exit(a, state_dict[parent][3])

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

event_header_str = """#ifndef HSM_H
#define HSM_H

#include "sm.h"
#include "event.h"
"""

hsmc_header_str = """#include "event.h"
#include "sm.h"
#include "transitions.h"
#include "guardandactions.h"
#include "bsp.h"
#include "hsm.h"
#include <stdio.h>
#include <Arduino.h>
#include <avr/pgmspace.h>

char buffer[100];
""" if use_avr else """#include "event.h"
#include "sm.h"
#include "transitions.h"
#include "guardandactions.h"
#include "bsp.h"
#include "hsm.h"
#include <stdio.h>
"""


event_enum_begin_str = """enum {{
    {} = USER_EVENT,
"""
event_enum_body_str = """    {},
"""
event_enum_end_str = """};

"""

guardandactionsh_header_str = """#ifndef GUARDANDTRANSITIONS_H
#define GUARDANDTRANSITIONS_H
"""

guardandactionsc_header_str = """#include "guardandactions.h"
#include <stdio.h>
#include <Arduino.h>
#include <avr/pgmspace.h>

extern char buffer[100];
""" if use_avr else """#include "guardandactions.h"
#include <stdio.h>
"""

guardandactions_end_str = """

#endif
"""

cb_declaration_str = "cb_status {}_cb(event_t ev);\n"
cb_header_str = """
cb_status init_cb(event_t ev)
{
    top_init_tran();
    return EVENT_HANDLED;
}

"""

cb_definition_begin_str = """cb_status {0}_cb(event_t ev)
{{
	const static char PROGMEM entry_msg[] = "ENTRY_EVENT..{0}";
	const static char PROGMEM exit_msg[] = "EXIT_EVENT..{0}";
    switch(ev) {{
    case ENTRY_EVENT:
		strcpy_P(buffer, (char *) entry_msg);
		Serial.println(buffer);
        return EVENT_HANDLED;
    case EXIT_EVENT:
		strcpy_P(buffer, (char *) exit_msg);
		Serial.println(buffer);
        return EVENT_HANDLED;
""" if use_avr else """cb_status {0}_cb(event_t ev)
{{
    switch(ev) {{
    case ENTRY_EVENT:
    	printf("ENTRY_EVENT..{0}\\n");
        return EVENT_HANDLED;
    case EXIT_EVENT:
    	printf("EXIT_EVENT..{0}\\n");
        return EVENT_HANDLED;
"""
cb_definition_body1_str = """    case INIT_EVENT:
		const static char PROGMEM exit_msg[] = "INIT_EVENT..{}";
		strcpy_P(buffer, (char *) entry_msg);
		Serial.println(buffer);
""" if use_avr else """    case INIT_EVENT:
    	printf("INIT_EVENT..{}\\n");
"""

cb_definition_body4_str = """    case {0}:
    	printf("EVENT..{0}\\n");
        if ({1}) {{
            {2};
            {3};
            return EVENT_HANDLED;
        }}
        break;
"""

cb_definition_body42_str = """    case {0}:
    	printf("EVENT..{0}\\n");
        if ({1}) {{
            {2};
            return EVENT_HANDLED;
        }}
        break;
"""

cb_definition_body5_str = """    case {0}:
    	printf("EVENT..{0}\\n");
        if ({1}) {{
            {2};
            return EVENT_HANDLED;
        }}
        break;
"""


cb_definition_body52_str = """    case {0}:
    	printf("EVENT..{0}\\n");
        {1};
        return EVENT_HANDLED;
"""

cb_definition_body6_str = """    case {0}:
    	printf("EVENT..{0}\\n");
        {1};
        {2};
        return EVENT_HANDLED;
"""

cb_definition_body62_str = """    case {0}:
    	printf("EVENT..{0}\\n");
        {1};
        return EVENT_HANDLED;
"""
cb_case_statement_str = """    case {0}:
    	printf("EVENT..{0}\\n");
        {1}
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
int {0}
{{
    const static char PROGMEM gc_msg[] = "GC: {0}";
    strcpy_P(buffer, (char *) gc_msg);
	Serial.println(buffer);
    /* Desenvolva aqui sua funcao.*/
    return 0;
}}

""" if use_avr else """
int {0}
{{
    /* Desenvolva aqui sua funcao.*/
    printf("GC: {0}\\n");
    return 0;
}}

"""

cb_action_functions_definitions_str = """
int {0}
{{
    const static char PROGMEM action_msg[] = "ACTION: {0}";
    strcpy_P(buffer, (char *) action_msg);
	Serial.println(buffer);
	/* Desenvolva aqui sua funcao.*/
    return 1;
}}

""" if use_avr else """
int {0}
{{
    /* Desenvolva aqui sua funcao.*/
    printf("ACTION: {0}\\n");
    return 1;
}}

"""


functions_declarations_str = """
int {};"""


int_gc_str = """

/* Guard Conditions: */"""


int_actions_str = """

/* Actions: */"""

#
# Definimos agora os geradores que serão
# usados para criar o código linha por linha
#

def cb_guard_definitions_def(guard_list):
    for gc in guard_list:
    	if ("(" in gc):
        	yield cb_guard_functions_definitions_str.format(gc)


def cb_actions_definitions_def(behavior_list):
    for action in behavior_list:
    	if ("(" in action):
        	yield cb_action_functions_definitions_str.format(action)

def functions_declarations_def(guard_list):
    for function in guard_list:
    	if ("(" in function):
        	yield functions_declarations_str.format(function)


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
    yield "cb_status init_cb(event_t ev);\n"
    for state in state_list:
        yield cb_declaration_str.format(state) 


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
            return cb_case_body1_str.format(gc, lines, tran_name)
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
#include "guardandactions.h"

'''

tran_endfile_str="""
#endif
"""

tran_top_init_begin_str = """
#define top_init_tran() do {\t\t\t\t\\
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

            for state_in_path in path1[::-1]:
                yield pop_exit_path_str
            if (not path1 or not path2) and external_trans:
                yield tran_ext_exit_entry_str
            for state_in_path in path2:
                yield push_init_path_str.format(state_in_path)
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
        print("\n\n=========================\nd2 = {}\n".format(d2))
        for lst in d2.values():
            print("lst = {} \n=========================\n\n".format(lst))
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
                print("Estado inicial: ", state)
                print("Estado   final: ", dst_state)
                path1a = [el1 for el1, el2 in zip_longest(path1, path2) if el1 and el1 != el2]
                path2 = [el2 for el1, el2 in zip_longest(path1, path2) if el2 and el1 != el2]
                path1 = path1a
                print(path1)
                print(path2)
                # print("**********")

                for state_in_path in path1[::-1]:
                    yield pop_exit_path_str
                if (not path1 or not path2) and external_trans:
                    yield tran_ext_exit_entry_str
                for state_in_path in path2:
                    yield push_init_path_str.format(state_in_path)
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

#if defined(__cplusplus)
extern "C"
{
#endif
void init_machine(cb_t init_fun);
#if defined(__cplusplus)
}
#endif

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

smc_str = """#include "sm.h"

state_t _active_states[MAX_ACTIVE_STATES];

state_t *_p_state = _active_states;

uint8_t _state_stack_len;

void init_machine(cb_t init_fun)
{
        *_active_states = 0;
        init_fun(INIT_EVENT);
}
"""

eventh_str="""#ifndef EVENTS_H
#define EVENTS_H

#include <stdint.h>

typedef uint32_t event_t;

#if defined(__cplusplus)
extern "C"
{
#endif
event_t wait_for_events(void);
event_t check_for_events(void);
event_t test_for_event(event_t);
#if defined(__cplusplus)
}
#endif

extern volatile event_t _events;
#define set_event(ev)                           \\
        do {                                    \\
                enter_critical_region();        \\
                _events |= (1 << (ev));         \\
                leave_critical_region();        \\
        } while (0)

#define MAX_EVENTS 32

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
    EVENT15,
    EVENT16,
    EVENT17,
    EVENT18,
    EVENT19,
    EVENT20,
    EVENT21,
    EVENT22,
    EVENT23,
    EVENT24,
    EVENT25,
    EVENT26,
    EVENT27,
    EVENT28,
    EVENT29,
    EVENT30,
    EVENT31
};

#endif /* EVENTS_H */
"""

eventc_str="""#include "event.h"
#include "bsp.h"


volatile event_t _events;

event_t test_for_event(event_t ev)
{
	return _events & (1 << ev);
}


event_t wait_for_events(void)
{
	uint8_t ev;
	event_t copy;

	while(!_events)
		;

	for(ev=0, copy=_events; ev<MAX_EVENTS && copy; ev++, copy>>=1)
		if (copy & 0x1) {
			enter_critical_region();
			_events &= ~(1 << ev);
			leave_critical_region();
			break;
		}

	return ev;
}

event_t check_for_events(void)
{
	uint8_t ev = 0;
	event_t copy;

	if(_events){
		for(ev=0, copy=_events; ev<MAX_EVENTS && copy; ev++, copy>>=1)
			if (copy & 0x1) {
				enter_critical_region();
				_events &= ~(1 << ev);
				leave_critical_region();
				break;
			}
	}
	return ev;
}
"""

hsmh_medium_str="""
#if defined(__cplusplus)
extern "C"
{
#endif
"""

hsmh_bottom_str="""
#if defined(__cplusplus)
}
#endif

#endif"""

bsph_str="""#ifndef BSP_H
#define BSP_H

#ifdef __AVR__
#include "bsp_avr.h"
#elif defined __linux__
#include "bsp_linux.h"
#else
#error "Architecture not know!"
#endif

#endif /* BSP_H */
"""

bsp_avrh_str="""#ifndef BSP_AVR_H
#define BSP_AVR_H

#include <avr/interrupt.h>

#define enter_critical_region() cli()
#define leave_critical_region() sei()

#endif /* BSP_AVR_H */
"""

bsp_linuxh_str="""#ifndef BSP_LINUX_H
#define BSP_LINUX_H

void bsp_init(void);
void enter_critical_region(void);
void leave_critical_region(void);

#endif /* BSP_LINUX_H */
"""

bsp_linuxc_str="""#include <pthread.h>
#include "bsp_linux.h"

pthread_mutex_t _event_mutex;

void bsp_init(void)
{
        pthread_mutex_init(&_event_mutex, 0);
}


void enter_critical_region()
{
        pthread_mutex_lock(&_event_mutex);
}


void leave_critical_region()
{
        pthread_mutex_unlock(&_event_mutex);
}
"""

main_linuxc_top_str = """#include "event.h"
#include "guardandactions.h"
#include "hsm.h"
#include "sm.h"
#include "bsp.h"
#include "transitions.h"

void verifica_serial()
{
  int char_received;
  char_received = Serial.read();
  if (char_received > -1){
    switch (char_received) {
                """ if use_avr else """#include "hsm.h"
#include "sm.h"
#include "bsp_linux.h"
#include <stdio.h>
#include <pthread.h>
#include <stdint.h>

pthread_mutex_t handling_mutex;
pthread_cond_t handling_cv;


void *event_thread(void *vargp)
{
        event_t ev;

        while (1) {
                ev = wait_for_events();
                if (ev == EMPTY_EVENT)
                        break;
                printf("\\n");
                dispatch_event(ev);
                pthread_mutex_lock(&handling_mutex);
                pthread_cond_signal(&handling_cv);
                pthread_mutex_unlock(&handling_mutex);
        }

        return NULL;
}


int main(int argc, char* argv[])
{
        char *ptr;
        pthread_t tid;

        if (argc < 2) {
                fprintf(stderr, "Usage: %s inputs\\n", argv[0]);
                return -1;
        }

        pthread_mutex_init(&handling_mutex, 0);
        pthread_cond_init(&handling_cv, 0);
        pthread_create(&tid, NULL, event_thread, NULL);

        init_machine(init_cb);
        ptr = argv[1];
        while(*ptr) {
                switch (*ptr++) {
                """

main_linuxc_bottom_str = """
                default:
                        set_event(USER_EVENT);
                        /* continue; */
                }
  }
}

void setup() {
  Serial.begin(115200);
  init_machine(init_cb);
}

void loop() {
  event_t ev;
  verifica_serial();
  ev = check_for_events();
  if (ev != 0)
    dispatch_event(ev);
}


""" if use_avr else """
                default:
                        set_event(USER_EVENT);
                        /* continue; */
                }
                pthread_mutex_lock(&handling_mutex);
                pthread_cond_wait(&handling_cv, &handling_mutex);
                pthread_mutex_unlock(&handling_mutex);
        }
        printf("\\n");

        set_event(EMPTY_EVENT);
        pthread_join(tid, NULL);

        return 0;
}
"""

body_case_main_linuxc_str = """
                case '{}':
                case '{}':
                        set_event({});
                        break;"""

ABC_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
abc_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

def completing_body_case_main_linuxc_str(event_list, ABC_list, abc_list):
    case_events_tuple = list(zip(ABC_list, abc_list, event_list))

    for event_tuple in case_events_tuple:
        yield (body_case_main_linuxc_str.format(event_tuple[0], event_tuple[1], event_tuple[2]))

def completing_case_main_linuxc_str(body_case_main):
    body_main_intermediary = ""
    for item in body_case_main:
        body_main_intermediary = body_main_intermediary + item
    return body_main_intermediary

# Gerando arquivos hsm de definição e descrição da máquina de estados
with open('hsm.h', 'w') as f:
    events_seq = events_def(event_list)
    cb_decl_seq = cb_declarations_def(state_dict.keys())
    f.writelines(chain(events_seq, hsmh_medium_str, cb_decl_seq, hsmh_bottom_str))

with open('hsm.{}'.format('cpp' if use_avr else 'c'), 'w') as f:
    cb_def_seq = cb_definitions_def(state_dict)
    f.writelines(chain(hsmc_header_str, cb_def_seq))

# Gerando arquivo transitions de descrição das transições
with open('transitions.h', 'w') as f:
    transitions1_seq = transitions1_def()
    transitions2_seq = transitions2_def()
    f.writelines(chain(transitions1_seq, transitions2_seq,  tran_endfile_str))

# Gerando arquivos guard and actions de definição e descrição das condições de guarda e ações
with open('guardandactions-esqueleto.{}'.format('cpp' if use_avr else 'c'), 'w') as f:
    functions_gc = cb_guard_definitions_def(guard_list)
    functions_actions = cb_actions_definitions_def(behavior_list)
    f.writelines(chain(guardandactionsc_header_str, int_gc_str, functions_gc, int_actions_str, functions_actions))


with open('guardandactions.h', 'w') as f:
    functions_gc = functions_declarations_def(guard_list)
    functions_actions = functions_declarations_def(behavior_list)
    f.writelines(chain(guardandactionsh_header_str, int_gc_str, functions_gc, int_actions_str, functions_actions, guardandactions_end_str))


with open('sm.h', 'w') as f:
    f.writelines(smh_str)
    
with open('sm.c', 'w') as f:
    f.writelines(smc_str)
    
with open('event.h',  'w') as f:
    f.writelines(eventh_str)

with open('event.c',  'w') as f:
    f.writelines(eventc_str)

with open('bsp.h',  'w') as f:
    f.writelines(bsph_str)

with open('bsp_avr.h',  'w') as f:
    f.writelines(bsp_avrh_str)

if not use_avr:
	with open('bsp_linux.h',  'w') as f:
		f.writelines(bsp_linuxh_str)

	with open('bsp_linux.c',  'w') as f:
		f.writelines(bsp_linuxc_str)

# Gerando arquivos para testar a máquina no linux
with open('main_{}.{}'.format('atmega' if use_avr else 'linux', 'ino' if use_avr else 'c'),  'w') as f:
    body_case_main = completing_body_case_main_linuxc_str(event_list, ABC_list, abc_list)
    body_main = completing_case_main_linuxc_str(body_case_main)
    f.writelines(chain(main_linuxc_top_str, body_main, main_linuxc_bottom_str))


































