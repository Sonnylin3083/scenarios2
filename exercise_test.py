from exercise import *
from syntax import *
a = Proposition("PERSON", "ANGRY")
b = Proposition("PERSON", "ANGRY", True)
print(a)
print(b)

for connective in Connective:
    e = Exercise(difficulty=2)
    # print(e.formula_to_str())
    print(e.formula)
    for var in e.var_map:
        q: Proposition = e.var_map[var]
        print(q.noun, q.adjective)
    print(e.formula_to_str())
