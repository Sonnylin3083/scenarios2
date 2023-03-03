from syntax import Formula
from semantics import truth_values, all_valuations


class Exercise:

    def __init__(self, difficulty=3) -> None:
        self.formula = Formula('lol')

    @staticmethod
    def generate_question(letters=3, connectives=3):
        pass

    def check_answer(self, answer: str) -> bool:
        formula = Formula.parse(answer)
        valuations = list(all_valuations(self.formula.variables()))
        if (truth_values(formula, valuations) == truth_values(self.formula, valuations)):
            return True
        return False
