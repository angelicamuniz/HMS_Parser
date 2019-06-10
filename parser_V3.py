import lark


grammar = """root: (state | transition)*
state: "state" STATE "{" (state | transition | internal_transition)* "}"
internal_transition: ":" TRIGGER ("[" GUARD "]")? ("/" BEHAVIOR)?
transition: (STATE | ENDPOINT)? "->" (STATE | ENDPOINT) (":" (TRIGGER ("," TRIGGER)*)? ("[" GUARD "]")? ("/" BEHAVIOR)?)?

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
		[*] -> S11

		state S11 {
			state S111 {

			}
			state S112 {

			}
		}

		state S12 {
			state S121 {

			}
			state S122 {

			}
		}

		-> S2 : ev1, ev2, ev3 ["foo == 0"] / "foo = 1"
	}

	state S2 {
		state S21 {

		}
		state S22 {

		}
	}
"""
tree = json_parser.parse(text)
#print(tree.pretty())

actions = {"root": None,
           "transition": None,
           "state": None}

def processa_transicao(children):
    if children[1].type in ["STATE", "ENDPOINT"]:
        transicao = [children[0].value, children[1].value, [], [], []]
        children = children[1:]
    else:
        transicao = [None, children[0].value, [], [], []]
    for node in children[1:]:
        if node.type == "TRIGGER":
            transicao[2].append(node.value)
        elif node.type == "GUARD":
            transicao[3].append(node.value)
        elif node.type == "BEHAVIOR":
            transicao[4].append(node.value)
        else:
            print("Tipo de nó desconhecido", type(node))

    return transicao

def processa_estado(parent, children):
    estado = ["", [], parent, [], []]
    for node in children:
        if type(node) == lark.lexer.Token:
            if node.type == "STATE":
                estado[0] = node.value
            else:
                print("Token desconhecido")
        elif type(node) == lark.tree.Tree:
            if node.data == "state":
                estado[1].append(processa_estado(estado, node))
            elif node.data == "transition":
                estado[3].append(processa_transicao(node.children)) #testar se tem estado inicial
            elif node.data == "internal_transition":
                estado[4].append(processa_transicao_interna(estado, node))
            else:
                print("Árvore desconhecida: ", node.data)
        else:
            print("Tipo de nó desconhecido", type(node))

    return estado

def pretty(tree, indentacao=""):
   # actions[tree.data](tree.children)
    print(indentacao + "Data: {}".format(tree.data))
    for node in tree.children:
        if type(node) == lark.tree.Tree:
            print(indentacao + "===Tree===")
            pretty(node, indentacao + "   ")
        else:
            print("{}Child: {}".format(indentacao, node))

print(processa_transicao(tree.children[1].children[4].children))


#pretty(tree)
