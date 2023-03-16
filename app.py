import json
import os
import random
import tkinter as tk

import appdirs
import PySimpleGUI as sg

from constants import *
from exercise import Exercise
from syntax import Connective, Formula, prop_letters


def load_saved_exercises():
    p = appdirs.user_data_dir('English_2_Prop_App')
    print(p)
    if (not os.path.exists(p)):
        os.makedirs(p)
    exercises_json = {'exercises': []}
    exercise_fp = os.path.join(p, SAVED_EX_FILE)
    if (not os.path.exists(exercise_fp)):
        with open(exercise_fp, 'w+') as outfile:
            json.dump(exercises_json, outfile)
            outfile.close()
    else:
        with open(exercise_fp, 'r') as json_file:
            try:
                exercises_json = json.load(json_file)
            except Exception:
                sg.popup("Error Loading saved exercises",
                         "Deleting saved exercises file...")
                os.remove(exercise_fp)
            json_file.close()
    return exercises_json


def save_exercises_to_json(exercise_json):
    p = appdirs.user_data_dir('English_2_Prop_App')
    with open(os.path.join(p, SAVED_EX_FILE), 'w+') as outfile:
        json.dump(exercise_json, outfile)
        outfile.close()


def create_layout_add_exercise():
    input_layout = [[sg.Text("Exercise Creator")],
                    [sg.Text("English:"), sg.Multiline(tooltip="Enter the English sentence in this box", key='-INPUT_ENGLISH-',
                                                       size=(30, 2), do_not_clear=False)],
                    [sg.Text("Propositional Formula:"), sg.Multiline(tooltip="Enter the propositionak formula in this box", key='-INPUT_FORMULA-',
                                                                     size=(20, 2), do_not_clear=False)],
                    [sg.Button('Add Exercise', key='-ADD_EXERCISE-',
                               font=MENU_FONT, auto_size_button=True)],]

    return [[sg.Column(input_layout, element_justification='c')]]


def add_exercise_loop(win: sg.Window):
    exercises_json = load_saved_exercises()
    print(exercises_json)
    while True:
        ev, vals = win.read()
        print(ev, vals)
        if ev in [sg.WIN_CLOSED, 'Exit', ]:
            save_exercises_to_json(exercises_json)
            win.close()
            return
        elif ev == '-ADD_EXERCISE-':
            if (vals['-INPUT_ENGLISH-'] == '' or vals['-INPUT_FORMULA-'] == ''):
                sg.popup("Input sentence or formula is empty.")
                continue
            try:
                formula = Formula.parse(vals['-INPUT_FORMULA-'])
                sentence = vals['-INPUT_ENGLISH-']
                exercises_json['exercises'].append(
                    {"english": sentence, "formula": str(formula)})
                sg.popup("Exercise saved successfully!")
            except Exception as e:
                sg.popup(str(e), 'Error parsing')
                continue
            print(exercises_json)


def create_layout_game():
    input_buttons_layout = [[], []]
    label_val_map = {}
    for c in Connective:
        label_val_map[f"{c.name}: {c.value}"] = f'( {c.value} )'
    for x in ['(', ')']:
        label_val_map[x] = x

    print(label_val_map)
    for label, val in label_val_map.items():
        input_buttons_layout[0].append(
            sg.Button(label, font="Arial 16", key=f'INPUT_BUTTON_{val}'))
    for var in prop_letters[:MAX_PROPOSITIONS]:
        input_buttons_layout[1].append(
            sg.Button(var, key=f'INPUT_BUTTON_{var}'))

    game_layout = [[sg.Text(key='-QUESTION-', font='Helvetica 18', size=(30, 2))],
                   [sg.Multiline(tooltip="Enter your answer in this box", key='-ANSWER-',
                                 size=(20, 2), font='Helvetica 16')],
                   [sg.Frame(None, input_buttons_layout)],
                   [sg.Button('Submit Answer', key='-CHECK_ANSWER-',
                              font=MENU_FONT, auto_size_button=True)],]

    info_bar = [[sg.Button('Quit', key='-QUIT-'), sg.Text(
        'Question 0 of 10', key='-QUESTION_NUMBER-'), sg.Text('Score: 0', key='-SCORE-'),
        sg.Button("Next Question", key='-NEXT_QUESTION-', visible=False)]]
    game_layout += info_bar
    return [[sg.Column(game_layout, element_justification='c')]]


def insert_string(text: tk.Text, string):
    if text.tag_ranges('sel') == ():
        text.insert('insert', string)
    else:
        start, end = text.tag_ranges('sel')
        text.replace(start, end, string)


def game_loop(win: sg.Window, difficulty_str: str, num_questions: int, use_saved: bool):

    difficulty = {'Easy': 1, 'Normal': 2, 'Hard': 3}[difficulty_str]
    exercises = []
    """ 
    Load {num_questions} Saved Exercises from saved exercises file.
    If not enough saved exercises or {use_saved} is false, generate random exercises of specificed difficulty
    to make the difference.
    """
    if (use_saved):
        exercise_json = load_saved_exercises()
        for saved_exercise in random.sample(exercise_json['exercises'],
                                            min(num_questions, len(exercise_json['exercises']))):
            exercises.append(
                Exercise(formula_str=saved_exercise['formula'], english_repr=saved_exercise['english']))
    for _ in range(num_questions-len(exercises)):
        exercises.append(Exercise(difficulty))

    def load_exercise(qn_num, score,):
        exercise: Exercise = exercises[qn_num-1]
        win['-QUESTION_NUMBER-'].update(
            f"Question {qn_num} of {num_questions}")
        win['-SCORE-'].update(f"Score: {score}")
        win['-QUESTION-'].update(str(exercise), )
        win['-ANSWER-'].update(exercise.formula)
        for var in prop_letters[:MAX_PROPOSITIONS]:
            win[f'INPUT_BUTTON_{var}'].update(
                visible=True if (var in exercise.formula.variables()) else False)
        win['-NEXT_QUESTION-'].update(visible=False)
        win['-CHECK_ANSWER-'].update(disabled=False)
        return exercise

    qn_num = 1
    curr_score = 0
    curr_question = load_exercise(qn_num, curr_score)

    while True:
        ev, vals = win.read()
        print(ev, vals)
        if ev in [sg.WIN_CLOSED, '-QUIT-', 'Exit']:
            win.close()
            return
        if 'INPUT_BUTTON' in ev:
            print('button pressed')
            insert_string(win['-ANSWER-'].widget, ev.split('_')[-1])
        elif ev == '-CHECK_ANSWER-':
            if (vals['-ANSWER-'] == ''):
                sg.popup("Answer is empty.")
                continue
            try:
                input_str: str = vals['-ANSWER-']
                # Replace any whitespace in the string
                is_correct = curr_question.check_answer(
                    "".join(input_str.split()))

                if (is_correct):
                    print("Correct!")
                    curr_score += 10
                else:
                    print(curr_question.formula)
                    print("wrong")
                win['-CHECK_ANSWER-'].update(disabled=True)
                win['-NEXT_QUESTION-'].update(visible=True)

            except Exception as e:
                print(e)
                sg.popup("Answer is malformed")
        elif ev == '-NEXT_QUESTION-':
            qn_num += 1
            if (qn_num > num_questions):
                sg.popup(f"Congrats, your score is {curr_score}")
                win.close()
                return
            curr_question = load_exercise(qn_num, curr_score)


if __name__ == '__main__':
    sg.theme('Dark Blue 2')
    sg.set_options(font=('', 20), element_size=(60, 1))
    sg.DEFAULT_TEXT_JUSTIFICATION = 'l'
    # ----------- Create the 3 layouts this Window will display -----------
    layout_menu = [[sg.Column([[sg.Text(MENU_TITLE,)],
                               [sg.Button("Play Game", key='-PLAY-',
                                          font=MENU_FONT, auto_size_button=True)],
                               [sg.Button("Instructions", key='-INFO-',
                                          font=MENU_FONT, auto_size_button=True)],
                               [sg.Button("Add Exercises", key='-CREATE-', font=MENU_FONT, auto_size_button=True)]],
                              element_justification='c')]]

    # ----------- Create actual layout using Columns and a row of Buttons

    layout = [[sg.Column(layout_menu, key='-COL1-')]]

    window = sg.Window(MENU_TITLE, layout)
    while True:
        event, values = window.read()
        print(event, values)
        if event in (None, sg.WIN_CLOSED):
            break
        if event == '-PLAY-':
            e, vals_settings = sg.Window('Game Settings', [[sg.Text("Difficulty:"),
                                                            sg.Combo(['Easy', 'Normal', 'Hard'], default_value='Normal', readonly=True)],
                                                           [sg.Text("Number of Exercises:"),
                                                           sg.Combo([5, 10, 15], default_value=10, readonly=True)],
                                                           [sg.Checkbox(
                                                               "Prefer Saved Exercises")],
                                                           [sg.Button("Play!")]]).read(close=True)
            print(f"Read pop-up | {e} {vals_settings}")
            window.hide()
            win2 = sg.Window(
                'Game', layout=create_layout_game(), finalize=True)
            game_loop(win2, *(vals_settings[k] for k in vals_settings))
            print('back to main from play')
            window.UnHide()

        elif event == '-CREATE-':
            window.hide()
            win2 = sg.Window('Exercise Creator',
                             layout=create_layout_add_exercise(), finalize=True)
            add_exercise_loop(win2)
            print('back to main from create')
            window.UnHide()
    window.close()
