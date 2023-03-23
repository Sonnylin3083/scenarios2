from syntax import Formula, Connective
from semantics import truth_values, all_valuations
import random


class Proposition:
    """ Represents English propositions of the form 'x is p', where x is a noun and p an adjective """

    def __init__(self, noun: str = 'Dog', adjective: str = 'Hungry') -> None:
        self.noun = noun
        self.adjective = adjective

    def __str__(self):
        return f"{self.noun} is {self.adjective}"


class Exercise:

    nouns = ['Water', 'Bread', 'Pizza', 'Celery', 'Pasta', "Soda", 'Cheese', 'Milk', 'Chocolate',
             'Tea', 'Coffee', 'Sugar', 'Salt']
    adjs = ['Red', 'Green', 'Blue', 'Yellow', 'Orange', 'Purple', 'Violet', 'Hot',
            'Cold', 'Warm', 'Tasty', 'Bland', 'Spicy', 'Sour', "Sweet", "Salty", "Mild"]

    def __init__(self, difficulty=2, formula_str=None, english_repr=None) -> None:

        self.formula = Formula.generate_formula(
            difficulty) if formula_str is None else Formula.parse(formula_str)
        self.english_repr = english_repr
        if (english_repr is None):
            self.var_map = self._generate_mapping()

    def __str__(self):
        if (self.english_repr is not None):
            return self.english_repr
        parsed_formula = self._parse_formula(self.formula)

        if (parsed_formula[0] == '(' and parsed_formula[-1] == ')'):
            parsed_formula = parsed_formula[1:-1]
        return parsed_formula

    def _parse_formula(self, formula: Formula) -> str:
        if isinstance(formula.val, Connective):
            l = self._parse_formula(formula.left)
            if formula.val == Connective.NOT:
                return f"({l} is false)"
            r = self._parse_formula(formula.right)
            match formula.val:
                case Connective.AND:
                    return f"({l} and {r})"
                case Connective.OR:
                    return f"({l} or {r})"
                case Connective.IMPLIES:
                    return f"(If {l}, then {r})"
                case Connective.IFF:
                    return f"({l} if and only if {r})"
        elif formula.val is not None:
            return f"'{str(self.var_map[formula.val])}'"
        else:
            return

    def _generate_mapping(self,):
        vars = self.formula.variables()
        var_map = {}
        for var, noun, adj in zip(vars, random.sample(Exercise.nouns, len(vars)),
                                  random.sample(Exercise.adjs, len(vars))):
            var_map[var] = Proposition(noun, adj)
        return var_map

    def check_answer(self, answer: str) -> bool:
        """ Check that the formula str is logically equivalent to self.formula under all valuations """
        formula = Formula.parse(answer)
        valuations = list(all_valuations(self.formula.variables()))
        if (truth_values(formula, valuations) == truth_values(self.formula, valuations)):
            return True
        return False
