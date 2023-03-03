
from syntax import *
from semantics import *
from questions import *
parsing_tests = [('', None, ''),
                 ('x', 'x', ''),
                 ('T', 'T', ''),
                 ('a', None, ''),
                 (')', None, ''),
                 ('x&', 'x', '&'),
                 ('p&y', 'p', '&y'),
                 ('F)', 'F', ')'),
                 ('~x', '~x', ''),
                 ('~', None, ''),
                 ('x', 'x', ''),
                 ('x|y', 'x', '|y'),
                 ('(p|x)', '(p|x)', ''),
                 ('((p|x))', None, ''),
                 ('x->x', 'x', '->x'),
                 ('(x->x)', '(x->x)', ''),
                 ('(x&y', None, ''),
                 ('(T)', None, ''),
                 ('(x&&y)', None, ''),
                 ('-|x', None, ''),
                 ('-->', None, ''),
                 ('(q~p)', None, ''),
                 ('(~F)', None, ''),
                 ('(r&(y|(z->w)))', '(r&(y|(z->w)))', ''),
                 ('~~~x~~', '~~~x', '~~'),
                 ('(((~T->s)&s)|~y)', '(((~T->s)&s)|~y)', ''),
                 ('((p->q)->(~q->~p))->T)', '((p->q)->(~q->~p))', '->T)'),
                 ('((p->q)->(~q->~p)->T)', None, ''),
                 ('(x|y|z)', None, ''),
                 ('~((~x->p)&~~(~F|~p))', '~((~x->p)&~~(~F|~p))', '')]


def test_parse_prefix(debug=False):
    if (debug):
        print()
    for s, f, r in parsing_tests:
        if debug:
            print("Testing parsing prefix of", s)
        ff, rr = Formula._parse_prefix(s)
        if ff is None:
            assert f is None, "_parse_prefix returned error: " + rr
            if debug:
                print("... _parse_prefix correctly returned error message:", rr)
            continue
        assert type(ff) is Formula
        assert type(rr) is str
        ff = str(ff)
        assert ff == f, "_parse_prefix parsed " + str(ff)
        assert rr == r, "_parse_prefix did not parse " + rr


def test_parse(debug=False):
    if (debug):
        print()
    for s, f, r in parsing_tests:
        if f is None or r != '':
            continue
        if debug:
            print("Testing parsing ", s)
        ff = Formula.parse(s)
        assert type(ff) is Formula
        assert str(ff) == f


def test_variables(debug=False):
    for formula, expected_variables in [
            (Formula('T'), set()),
            (Formula('x'), {'x'}),
            (Formula('~', Formula('r')), {'r'}),
            (Formula('->', Formula('x'), Formula('y')), {'x', 'y'}),
            (Formula('&', Formula('F'), Formula('~', Formula('T'))), set()),
            (Formula('|', Formula('~', Formula('->', Formula('p'),
                                               Formula('q'))), Formula('F')),
             {'p', 'q'}),
            (Formula('~', Formula('~', Formula('|', Formula('x'),
                                               Formula('~', Formula('x'))))),
             {'x'})]:
        if debug:
            print('Testing variables of', formula)
        assert formula.variables() == expected_variables


def test_evaluate(debug=False):
    infix1 = '~(p&q)'
    models_values1 = [
        ({'p': True,  'q': False}, True),
        ({'p': False, 'q': False}, True),
        ({'p': True,  'q': True},  False)
    ]
    infix2 = '~~~x'
    models_values2 = [
        ({'x': True}, False),
        ({'x': False}, True)
    ]
    infix3 = '((x->y)&(~x->z))'
    models_values3 = [
        ({'x': True,  'y': False, 'z': True},  False),
        ({'x': False, 'y': False, 'z': True},  True),
        ({'x': True,  'y': True,  'z': False}, True)
    ]
    infix4 = '(T&p)'
    models_values4 = [
        ({'p': True},  True),
        ({'p': False}, False)
    ]
    infix5 = '(F|p)'
    models_values5 = [
        ({'p': True},  True),
        ({'p': False}, False)
    ]
    for infix, models_values in [[infix1, models_values1],
                                 [infix2, models_values2],
                                 [infix3, models_values3],
                                 [infix4, models_values4],
                                 [infix5, models_values5]]:
        formula = Formula.parse(infix)
        for model, value in models_values:
            if debug:
                print('Testing evaluation of formula', formula, 'in model',
                      model)
            assert evaluate(formula, model) == value


def test_truth_values(debug=False):
    for infix, variables, values in [
            ['~(p&q)', ('p', 'q'), [True, True, True, False]],
            ['(y|~x)',  ('y', 'x'),  [True, False, True, True]],
            ['~~~p',    ('p'),       [True, False]]]:
        formula = Formula.parse(infix)
        if debug:
            print('Testing the evaluation of', formula,
                  'on all models over its variables')
        tvals = list(truth_values(
            formula, tuple(all_valuations(tuple(variables)))))
        assert tvals == values, \
            'Expected ' + str(values) + '; got ' + str(tvals)


test_parse_prefix(True)
test_parse(True)
test_variables(True)
test_evaluate(True)
test_truth_values(True)
print_truth_table(Formula.parse("~(p&(q|r))"))

ex = Exercise()
ex.formula = Formula.parse("~(~p&q)")

print('ans', ex.check_answer("(p|~q)"))
print('ans', ex.check_answer('~(q&~p)'))
print('ans', ex.check_answer('(((p&q)|(p&~q))|(~p&~q))'))
print('ans', ex.check_answer('(p|q)'))
