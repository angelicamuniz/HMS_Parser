import lark

# Definição da gramática:
grammar = """root: (state | transition)*
state: "state" STATE "{" (state | transition | internal_transition)* "}"
internal_transition: ":" TRIGGER (("," TRIGGER)*)? ("[" GUARD "]")? ("/" BEHAVIOR)?
transition: (STATE | ENDPOINT)? "->" (STATE | ENDPOINT) ":" (TRIGGER ("," TRIGGER)*)? (("[" GUARD "]")? ("/" BEHAVIOR)?)?

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
json_parser = lark.Lark(grammar, start="root")


text = """[*] -> S1 : ev0 / "c = 1;"

    state S1 {
        [*] -> S11 :

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
    }

    state S2 {
                [*] -> S22 :
        state S21 {

        }
        state S22 {

        }
         : ev11, ev22, ev33, ev44 ["foo == 1"] / "foo = 0"
         : EV11, EV22, EV33, EV44 ["foo == 1"] / "foo = 0"
    }
    S21 -> S22 : ev21 ["foo == 0"] / "foo = 1"
"""
tree = json_parser.parse(text)
# print(tree.pretty())

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
        # Alterei a localização do trigger, guard e behavior para serem encontrados de trás para frente, por causa da inclusão de um novo campo quando há transição init
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

''' CORRIGIR: Transições escritas externamente ao estado, não são incluídas devidamente no estado correspondente.
    Ficam como transições da root.'''

# Nome do estado, Filhos, Pai, Transições, Transições internas
root_state = processa_estado(None, tree.children)

# Assumindo que já temos uma lista de estados, outra de transições e outra de eventos, faça o código que vai gerar os arquivos finais. Depois disso, implemente a parte do código que gerará essas listas.

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
state_dict = {"S2": [
    # Transições iniciais
    {"": ["S22", ""]},
    # Transições externas"
    {("ev3", "foo == 0"): ["S1", "foo = 1"]},
    # Transições internas
    {("ev11", "foo == 1"): "foo = 0",
     ("ev22", "foo == 1"): "foo = 0",
     ("ev33", "foo == 1"): "foo = 0",
     ("ev44", "foo == 1"): "foo = 0",
    },
    # Lista de subestados
    ["S21", "S22"]],
    # Falta fazer os estados abaixo
              "S21": [
    # Transições iniciais
    {},
    # Transições externas"
    {},
    # Transições internas
    {},
    # Lista de subestados
    []],
              "S22": [
    # Transições iniciais
    {},
    # Transições externas"
    {},
    # Transições internas
    {},
    # Lista de subestados
    []]
}

# A lista abaixo não deveria ser um conjunto?
state_list = ['S1', 'S11', 'S111', 'S12', 'S121', 'S122', 'S2', 'S21', 'S22']

# As duas listas abaixo devem desaarecer?
event_list = ['ev1', 'ev2', 'ev3', 'ev11',
              'ev22', 'ev33', 'ev44', 'ev0', 'ev21', 'EV']
transition_list = [['S1', '[*]', 'S11', [], [], []], ['S11', '[*]', 'S111', [], [], []], ['S12', '[*]', 'S122', [], [], []], ['S2', ['EV11', 'EV22', 'EV33', 'EV44'], ['"foo == 1"'], ['"foo = 0"']], ['S1', 'S2', ['ev1', 'ev2', 'ev3'], ['"foo == 0"'], ['"foo = 1"']],
                   ['S1', 'S21', ['EV1'], [], []], ['S2', '[*]', 'S22', [], [], []], ['S2', ['ev11', 'ev22', 'ev33', 'ev44'], ['"foo == 1"'], ['"foo = 0"']], ['root', '[*]', 'S1', ['ev0'], [], ['"c = 1;"']], ['S21', 'S22', ['ev21'], ['"foo == 1"'], ['"foo = 2"']]]


# String que representa a inclusão de outras bibliotecas
event_header_str = '''#include <avr/pgmspace.h>
#include "ch.h"
#include "hal.h"
#include "chprintf.h"
#include "event.h"
#include "sm.h"
#include "transitions.h"
#include <string.h>

'''

# String que representa a inclusão da lista de eventos
event_enum_begin_str = """enum{{
    {} = USER_EVENT"""
event_enum_body_str = """,
    {}"""
event_enum_end_str = """
    };,
"""

# Função que preenche a primeira parte do código main_hsm.
def create_header_events(event_list):
    main_file = open('main_hsm.txt', 'w')
    main_file.write(event_header_str)
    main_file.write((event_enum_begin_str.format(event_list[0])))
    for event in event_list[1:]:
        main_file.write(event_enum_body_str.format(event))
    #main_file.write(event_enum_end_str)
    main_file.write('\n};')
    main_file.close()

create_header_events(event_list)

# Funcao que cria as funções de call back de cada estado.. cb_status
def create_cb_status(state_list):
    main_file = open('main_hsm.txt', 'a')
    main_file.write(
        '''\n\ncb_status init_cb(event_t ev);\ncb_status fn_cb(event_t ev);\n''')
    for state in state_list:
        main_file.write('\ncb_status fn_' + state + '_cb(event_t ev);')
    main_file.close()


create_cb_status(state_list)


# Funcao que cria o corpo das funções de call back dos estados e suas transições

def create_function_body(state_list, transition_list):
    main_file = open('main_hsm.txt', 'a')
    main_file.write('''

cb_status init_cb(event_t ev)
{
        Top_init_tran();
        return EVENT_HANDLED;
}


cb_status fn_cb(event_t ev)
{
        switch(ev) {
        case ENTRY_EVENT:
            return EVENT_HANDLED;
        case EXIT_EVENT:
            return EVENT_HANDLED;
        case INIT_EVENT:
            fn_init_tran();
            return EVENT_HANDLED;
        }

        return EVENT_NOT_HANDLED;
}
''')
    for state in state_list:
        i = 1
        main_file.write('\n\ncb_status fn_' + state + '_cb(event_t ev)' + '''
{
        switch(ev) {
        case ENTRY_EVENT:
                return EVENT_HANDLED;
        case EXIT_EVENT:
                return EVENT_HANDLED;''')
        for transition in transition_list:
            # Fixando um estado para verificar suas transições:
            if transition[0] == state:
                if transition[1] == '[*]':
                    main_file.write('\n\tcase INIT_EVENT:\n\t\tfn_' +
                                    state + '_init_tran();\n\t\treturn EVENT_HANDLED;')
                else:
                    for event in transition[-3]:
                        main_file.write('\n\tcase EVENT_' + event + ':')
                    if transition[0] == transition[-4]:
                        # Na transição interna não é necessário uma transição. Só deve ser tratada a condição de guarda e o behavior
                        # main_file.write('\n\t\t' + 'fn_' + transition[0] + '_intern_' + str(i) + '_tran();\n\t\treturn EVENT_HANDLED;')
                        i = i + 1
                    else:
                        for guard in transition[-2]:
                            print("Detectada condição de guarda:", guard, "no estado:",
                                  state, "behavior:", transition[-1][0][1:-1])
                            main_file.write("\n\t\tif (" + guard[1:-1] + ") {\n\t\t\t" + transition[-1][0][1:-1] + ';\n\t\t\t' + 'fn_' +
                                            transition[0] + '_' + transition[-4] + '_tran();\n\t\t\treturn EVENT_HANDLED;\n\t\t}\n\t\tbreak;')
                        # main_file.write('\n\t\t' + 'fn_' + transition[0] + '_' + transition[-4] + '_tran();\n\t\treturn EVENT_HANDLED;')
        main_file.write('\n\t}\n\treturn EVENT_NOT_HANDLED;\n}')
    main_file.close()


create_function_body(state_list, transition_list)

# Onde é mesmo que fn_init_tran() é implementada? Ou ela só é os dispatch da transição mesmo?

# Organizar em bibliotecas.
