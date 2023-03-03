from enum import Enum
prop_letters = ['T', 'F']+[chr(i) for i in range(ord('p'), ord('z')+1)]


class Connective(Enum):
    AND = '&'
    OR = '|'
    NOT = '~'
    IMPLIES = '->'
    IFF = '<>'

    # def __str__(self):
    #     return self.name
    def __repr__(self):
        return self.value

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class Formula:
    def __init__(self, val=None, left=None, right=None) -> None:
        self.left = left
        self.right = right
        if Connective.has_value(val):
            self.val = Connective(val)
        else:
            self.val = val

    def _insert(self, val):
        if (not isinstance(self.val, Connective)):
            raise Exception("Cannot insert in non-connective node")
        if (self.left is None):
            self.left = Formula(val)
        elif (self.right is None):
            self.right = Formula(val)
        else:
            raise Exception("Node has 2 children")

    def to_list(self):
        if (not isinstance(self.val, Connective)):
            return [self.val]
        if (self.val == Connective.NOT):
            return self.left.to_list()+[self.val]
        else:
            return self.left.to_list()+[self.val]+self.right.to_list()

    def variables(self):
        var_set = set()
        for symbol in self.to_list():
            if symbol in prop_letters and symbol not in ['T', 'F']:
                var_set.add(symbol)
        return var_set

    def inorder(self):
        if (not isinstance(self.val, Connective)):
            return str(self.val)
        if (self.val == Connective.NOT):
            return f"{repr(self.val)}{self.left.inorder()}"
        else:
            return f"({self.left.inorder()}{repr(self.val)}{self.right.inorder()})"

    @staticmethod
    def _parse_prefix(string: str):
        if (len(string) == 0):
            return (None, "Error: Zero Length String")
        token, rest = string[0], string[1:]
        if (token in prop_letters):
            return (Formula(token), rest)
        elif (token == Connective.NOT.value):
            next, remainder = Formula._parse_prefix(rest)
            if (next is None):
                return (None, f'Error in {rest}')
            return (Formula(Connective.NOT, next), remainder)
        elif (token == '('):
            pref_formula, suffix = Formula._parse_prefix(rest)
            if (pref_formula is None or len(suffix) == 0):
                return (None, 'Failed in ( step')
            if (Connective.has_value(suffix[0])
                    and suffix[0] != Connective.NOT.value):
                connective = Connective(suffix[0])
                suffix = suffix[1:]
            elif (len(suffix) > 1 and Connective.has_value(suffix[0:2])):
                connective = Connective(suffix[0:2])
                suffix = suffix[2:]
            else:
                return (None, f'Error in finding operator in {suffix}')
            suffix_formula, remainder = Formula._parse_prefix(suffix)
            if suffix_formula is None:
                return (None, f"Error in parsing {suffix}")
            if (len(remainder) == 0 or remainder[0] != ')'):
                return (None, f"Error in closing {remainder}")
            return (Formula(connective, pref_formula, suffix_formula), remainder[1:])
        else:
            return (None, f"Error in {string}")

    def parse(string: str) -> 'Formula':
        prefix, remainder = Formula._parse_prefix(string)
        if (len(remainder) == 0):
            return prefix
        else:
            raise Exception("Invalid String")

    def __repr__(self) -> str:
        return self.inorder()
