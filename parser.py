import lark




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
        -> S1 : ev3 ["foo == 0"] / "foo = 1"
    }
    S21 -> S22 : ev21 ["foo == 0"] / "foo = 1"
"""
tree = parser.parse(text)
#print(tree.pretty())




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
    #print("Children is ", children)
    if children[1].type in ["STATE", "ENDPOINT"]:
        #Caso em que a descrição da transicao é: S1 -> S2...
        print ('children[0] é:', children[0], children[0].type)
        if children[0].type in ["ENDPOINT"]:
            if current_state == '':
                current_state = 'root'
            transicao = [current_state, children[0].value, children[1].value, [], [], []]   #Estado inicial, init?, Estado final, Trigger, Guard, Behavior
        else:
            transicao = [children[0].value, children[1].value, [], [], []]   #Estado inicial, Estado final, Trigger, Guard, Behavior
        children = children[1:]
    else:
        #Caso em que a descrição da transicao é: -> S2...
        transicao = [current_state, children[0].value, [], [], []]
        print('Est atual:', current_state, 'Est final:', children[0].value)
    for node in children[1:]:
        #Alterei a localização do trigger, guard e behavior para serem encontrados de trás para frente, por causa da inclusão de um novo campo quando há transição init
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
    #print("Transição interna detectada.", children)
    transicao_interna = [current_state, [], [], []]   #Nome do estado, Trigger, Guard, Behavior
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
    estado = ["", [], parent, [], []]   #Nome do estado, Filhos, Pai, Transições, Transições internas
    for node in children:
        if type(node) == lark.lexer.Token:
            if node.type == "STATE":
                estado[0] = node.value
                #print("Detectamos um Token: ", node.value)
            else:
                print("Token desconhecido")
    
        elif type(node) == lark.tree.Tree:
            #print("Detectamos uma Tree: ", node.children[0].value)
            if node.data == "state":
                estado[1].append(processa_estado(estado[0], node.children))
            elif node.data == "transition":
                estado[3].append(processa_transicao(node.children, estado[0]))  #já envia a lista de filhos
                '''#testar se tem estado inicial'''
            elif node.data == "internal_transition":
                estado[4].append(processa_transicao_interna(node.children, estado[0]))
            else:
                print("Árvore desconhecida: ", node.data)
        else:
            print("Tipo de nó desconhecido", type(node))
    
    return estado

#Imprime a árvore
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

''' CORRIGIR: Transições realizadas externamente ao estado, não são incluídas devidamente no estado correspondente.
    Ficam como transições da root.'''

#Nome do estado, Filhos, Pai, Transições, Transições internas
#root_state = processa_estado(None, tree.children)

#Assumindo que já temos uma lista de estados, outra de transições e outra de eventos, faça o código que vai gerar os arquivos finais. Depois disso, implemente a parte do código que gerará essas listas.

#Como ler os eventos de uma determinada transição

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
event_list = ['ev1', 'ev2', 'ev3', 'ev11', 'ev22', 'ev33', 'ev44', 'ev0', 'ev21', 'EV']

# As duas listas abaixo devem desaarecer?
state_list = ['S1', 'S11', 'S111', 'S12', 'S121', 'S122', 'S2', 'S21', 'S22']
transition_list = [['S1', '[*]', 'S11', [], [], []], ['S11', '[*]', 'S111', [], [], []], ['S12', '[*]', 'S122', [], [], []]], ['S2', ['EV11', 'EV22', 'EV33', 'EV44'], ['"foo == 1"'], ['"foo = 0"']], ['S1', 'S2', ['ev1', 'ev2', 'ev3'], ['"foo == 0"'], ['"foo = 1"']], ['S1', 'S21', ['EV1'], [], []], ['S2', '[*]', 'S22', [], [], []], ['S2', ['ev11', 'ev22', 'ev33', 'ev44'], ['"foo == 1"'], ['"foo = 0"']], ['root', '[*]', 'S1', ['ev0'], [], ['"c = 1;"']], ['S21', 'S22', ['ev21'], ['"foo == 0"'], ['"foo = 1"']]]

for event in transition_list[1][-3]:
    print (event)

#
# Definimos primeiro as strings definindo as várias partes do código
# em C.  Algumas s]ao strings puras, outras strings para formatação
# (contendo {})
#
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
        fn_{}_init_tran();
        return EVENT_HANDLED;
"""
cb_definition_body2_str = """    case EVENT_{}:
"""
cb_definition_body3_str = """
        fn_{}_{}_tran();
        return EVENT_HANDLED;
"""
cb_definition_end_str = """    }
    return EVENT_NOT_HANDLED;
}

"""

#
# Definimos agora os geradores que serão usados para criar o código linha por linha
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

def cb_definitions_def(state_list, transition_list):
    """Generator function to generate the code lines for defining the
state callback functions"""
    yield cb_header_str
    for state in state_list:
        yield cb_definition_begin_str.format(state)
        for transition_state, initial_state, final_state, event_list, _, _ in transition_list:
            if transition_state == state:
                if initial_state == '[*]':
                    yield cb_definition_body1_str.format(state)
                else:
                    for event in event_list:
                        yield cb_definition_body2_str.format(event)
                    if transition_state == final_state:
                        # Preciso entender melhor o que está acontecendo aqui
                        print("ERROR: Describe error")
                        # main_file.write('\n\t\t\t' + 'fn_' + transition[0] + '_intern_' + str(i) + '_tran();\n\t\t\treturn EVENT_HANDLED;')
                    else:
                        yield cb_definition_body3_str.format(transition_state, final_state)
        yield cb_definition_end_str

#
# Agora, com todos os geradores definidos, podemos gerar o arquivo da máquina de estados
#
from itertools import chain

with open('main_hsm.c', 'w') as f:
    events_seq = events_def(event_list)
    cb_decl_seq = cb_declarations_def(state_list)
    cb_def_seq = cb_definitions_def(state_list, transition_list)
    f.writelines(chain(events_seq, cb_decl_seq, cb_def_seq))


#Transição interna precisa de fn_s2_s2_tran() ?
#SIM  (?)  ->    se tiver duas transicoes internas, estarão com o mesmo nome --->  CORRIGIDO
    #Correção de Hermano: Não precisa da transição. Só faz o que deve ser feito e pronto (condição de guarda e ação). Não tem entry nem exit

#onde é mesmo que fn_init_tran() é implementada? Ou ela só é os dispatch da transição mesmo? 

#SIM -> a condição de guarda é realizada no switch case com ifs
#Falta implementar a condição de guarda. Tentar alterar o código do text para que não fique com "", como os ev2. Assim podemos colocar direto

#Organizar em bibliotecas. 
