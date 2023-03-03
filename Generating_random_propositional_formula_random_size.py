import random

propositions = ['P', 'Q', 'R', 'S']
connectives = ['&', '|', '->', '<->']

def generate_formula(depth):
    if depth == 0:
        return random.choice(propositions)
    else:
        connective = random.choice(connectives)
        if connective in ['&', '|']:
            formula = '(' + generate_formula(depth-1) + ' ' + connective + ' ' + generate_formula(depth-1) + ')'
        elif connective == '->':
            formula = '(' + generate_formula(depth-1) + ' -> ' + generate_formula(depth-1) + ')'
        elif connective == '<->':
            formula = '(' + generate_formula(depth-1) + ' <-> ' + generate_formula(depth-1) + ')'
        return formula

depth = random.randint(1, 2)
print(generate_formula(depth))