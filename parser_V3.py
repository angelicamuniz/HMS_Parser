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

def pretty(tree, indentacao=""):
    print("Data: {}".format(tree.data))
    for node in tree.children:
        if type(node) == lark.tree.Tree:
            print(indentacao + "===Tree===")
            pretty(node, indentacao + "   ")
        else:
            print("{}Child: {}".format(indentacao, node))


pretty(tree)
