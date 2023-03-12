from syntax import Formula, Connective
from semantics import truth_values, all_valuations
import random


class Proposition:
    def __init__(self, noun: str = 'Dog', adjective: str = 'Hungry', negated=False) -> None:
        self.noun = noun
        self.adjective = adjective
        self.negated = negated

    def __str__(self):
        return f"{self.noun} is {('not ' if self.negated else '')+self.adjective}"


class Exercise:
    nouns = ['Water', 'Bread', 'Pizza', 'Celery', 'Pasta']
    adjs = ['Red', 'Green', 'Blue', 'Yellow', 'Hot',
            'Cold', 'Tasty', 'Bland', 'Spicy', 'Sour']

    def __init__(self, difficulty=2) -> None:
        self.formula = Formula.generate_formula(difficulty)
        self._generate_mapping()

    def __str__(self):
        parsed_formula = self._parse_formula(self.formula)
        return parsed_formula

    def _parse_formula(self, formula: Formula) -> str:
        if isinstance(formula.val, Connective):
            l = self._parse_formula(formula.left)
            if formula.val == Connective.NOT:
                return f"'{l}' is false"
            r = self._parse_formula(formula.right)
            match formula.val:
                case Connective.AND:
                    return f"'{l} and {r}'"
                case Connective.OR:
                    return f"'{l} or {r}'"
                case Connective.IMPLIES:
                    return f"'If {l}, then {r}'"
                case Connective.IFF:
                    return f"'{l} if and only if {r}'"
        elif formula.val is not None:
            return str(self.var_map[formula.val])
        else:
            return

    def _generate_mapping(self):
        vars = self.formula.variables()
        var_map = {}
        for var, noun, adj in zip(vars, random.sample(Exercise.nouns, len(vars)),
                                  random.sample(Exercise.adjs, len(vars))):
            var_map[var] = Proposition(noun, adj)
        self.var_map = var_map

    def check_answer(self, answer: str) -> bool:
        formula = Formula.parse(answer)
        valuations = list(all_valuations(self.formula.variables()))
        if (truth_values(formula, valuations) == truth_values(self.formula, valuations)):
            return True
        return False
