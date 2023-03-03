

from syntax import *
from itertools import product
from typing import Iterable, Sequence, Mapping

Valuation = Mapping[str, bool]


def evaluate(formula: Formula, valuation: Valuation) -> bool:
    if (isinstance(formula.val, Connective)):
        match formula.val:
            case Connective.NOT:
                return not evaluate(formula.left, valuation)
            case Connective.AND:
                return evaluate(formula.left, valuation) and evaluate(formula.right, valuation)
            case Connective.OR:
                return evaluate(formula.left, valuation) or evaluate(formula.right, valuation)
            case Connective.IMPLIES:
                return (not evaluate(formula.left, valuation)) or evaluate(formula.right, valuation)
            case Connective.IFF:
                return evaluate(formula.left, valuation) == evaluate(formula.right, valuation)
    if (formula.val in ['T', 'F']):
        return formula.val == 'T'
    if (formula.val not in valuation):
        raise Exception(f"No valuation for {formula.val} in {valuation}")
    else:
        return valuation[formula.val]

# Return the mapping in lexiographical order


def all_valuations(vars: Sequence[str]) -> Iterable[Valuation]:
    valuations = product([False, True], repeat=len(vars))
    return map(lambda p: dict(zip(vars, p)), valuations)


def truth_values(formula: Formula, valuations: Iterable[Valuation]) -> Iterable[bool]:
    return [evaluate(formula, p) for p in valuations]


def print_truth_table(formula: Formula) -> None:
    valuations = all_valuations(formula.variables())
    header = "|"
    for var in formula.variables():
        header += f" {var} |"
    header += f" {str(formula)}"
    header += ("\n" + '-' * len(header))
    print(header)
    for valuation in valuations:
        row = "|"
        for var in valuation:
            row += f" {'T' if valuation[var] else 'F'} |"
        row += f" {'T' if evaluate(formula, valuation) else 'F'}"
        print(row)
