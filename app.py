import json
import os
import random

import appdirs
import PySimpleGUI as sg

from constants import *
from exercise import Exercise
from syntax import Connective, Formula, prop_letters


def load_saved_exercises() -> list[dict[str, str]]:
    """ Read the saved exercises file in the user's (OS-dependent) app data directory.

    If the file does not exist, create it.

    Return a List of Dicts of the form {"english": ..., "formula": ...}
    """
    p = appdirs.user_data_dir('English_2_Prop_App')
    print(p)
    if (not os.path.exists(p)):
        os.makedirs(p)
    exercises = []
    exercise_fp = os.path.join(p, SAVED_EX_FILE)
    if (not os.path.exists(exercise_fp)):
        with open(exercise_fp, 'w+') as outfile:
            json.dump(exercises, outfile)
            outfile.close()
    else:
        with open(exercise_fp, 'r') as json_file:
            try:
                exercises = json.load(json_file)
            except Exception as e:
                print(e)
                sg.popup("Error Loading saved exercises",
                         "Deleting saved exercises file...")
            finally:
                json_file.close()
                os.remove(exercise_fp)
    return exercises


def save_exercises_to_json(exercises: list):
    """Write a list of exercises to a JSON file in the user's AppData directory  """
    p = appdirs.user_data_dir('English_2_Prop_App')
    with open(os.path.join(p, SAVED_EX_FILE), 'w+') as outfile:
        json.dump(exercises, outfile, indent=4)
        outfile.close()


def insert_string(tk_text, string):
    """ 
    Insert a string at the cursor position of a tkinter Text element
    If part of the text is selected, replace selection with string instead. 
    """

    if tk_text.tag_ranges('sel') == ():
        tk_text.insert('insert', string)
    else:
        start, end = tk_text.tag_ranges('sel')
        tk_text.replace(start, end, string)


def pretty_print_exercise(text: sg.Multiline, exercise: Exercise):
    """ 
    Write an exercise to a Multiline Element.
    Color propositions according to a color gradient
    Propositions are enclosed by a pair of single apostrophe characters 
    """
    text.update("")
    is_prop = False
    prop_colors = iter(PROP_FONT_COLORS)
    for token in str(exercise).split("\'"):
        text.print(token, end='',
                   text_color='white' if not is_prop else next(prop_colors, 'White'))
        is_prop = not is_prop


def show_instructions(title='Instructions'):
    """ Create and show a popup with instructions on what a well-formed formula is"""
    layout = [[sg.Column([[sg.Text(f"{PHI} is a Well-Formed Formula iff", text_color='Gold')],
                          [sg.T(f"{PHI} ∈ [p,q,r ... z] [Proposition]")],
                          [sg.T(f"{PHI} = {repr(Connective.NOT)}{PHI} [Negation]")],
                          [sg.T(
                              f"{PHI} = ({PHI} {repr(Connective.AND)} {PHI})   [Conjunction]")],
                          [sg.T(
                              f"       ({PHI} {repr(Connective.OR)} {PHI})   [Disjunction]")],
                          [sg.T(
                              f"       ({PHI} {repr(Connective.IMPLIES)} {PHI})   [Implication]")],
                          [sg.T(
                              f"       ({PHI} {repr(Connective.IFF)} {PHI})   [Equivalence]")],
                          [sg.Push(), sg.Button("OK"), sg.Push()]
                          ])]]

    sg.Window(title=title, layout=layout,
              disable_close=False, keep_on_top=True).read(close=True)


def create_layout_add_exercise():
    """ Create and return a fresh loadout for the exercise editor """
    saved_ex_layout = [
        [sg.Multiline(key='-SAVED_ENGLISH-', size=(25, 2),
                      no_scrollbar=False, disabled=True, pad=((10, 10), (5, 0)), text_color='White')],
        [sg.Text(key='-SAVED_FORMULA-', )],
        [sg.Button("Delete", key='-DEL_EXERCISE-'), sg.Button("Previous", key='-PREV_EXERCISE-'),
         sg.Button("Next", key='-NEXT_EXERCISE-'),]
    ]
    add_ex_layout = [
        [sg.Text("English:"),
         sg.Multiline(tooltip="Enter the English sentence in this box", key='-INPUT_ENGLISH-',
                      size=(20, 2), do_not_clear=True)],
        [sg.Text("Formula:"), sg.Multiline(tooltip="Enter the propositional formula in this box", key='-INPUT_FORMULA-',
                                           size=(20, 2), do_not_clear=True)],
        [sg.Button("Help", key='-HELP_BUTTON-'), sg.Button('Add Exercise', key='-ADD_EXERCISE-'), sg.Button("Exit")],]
    layout = [sg.vtop([sg.Frame("Create Exercise", element_justification='c', layout=add_ex_layout),
                       sg.Frame(title="Saved", key='ex_frame',
                                layout=saved_ex_layout, expand_x=True),
                       ])]
    return [[sg.Column(layout, element_justification='c')]]


def add_exercise_loop(win: sg.Window):
    """ Event Handler for the exercise editor """
    exercises = load_saved_exercises()
    print(exercises)

    def update_saved_ex_view(index: int):
        win['-DEL_EXERCISE-'].update(visible=False if len(
            exercises) == 0 else True)
        win['-PREV_EXERCISE-'].update(visible=False if index <=
                                      0 else True)
        win['-NEXT_EXERCISE-'].update(visible=False if index >= len(exercises)-1
                                      else True)
        win['-SAVED_ENGLISH-'].update('' if len(exercises) == 0 else
                                      exercises[index]['english'])
        win['-SAVED_FORMULA-'].update('' if len(exercises) == 0 else
                                      exercises[index]['formula'])
        win['ex_frame'].update(
            "No Saved Exercises" if len(exercises) == 0 else
            f"Saved Exercises ({index+1} of {len(exercises)})")

    saved_ex_index = 0
    update_saved_ex_view(saved_ex_index)

    print(exercises)
    while True:
        print(saved_ex_index)
        ev, vals = win.read()
        print(ev, vals)
        if ev in [sg.WIN_CLOSED, 'Exit', ]:
            save_exercises_to_json(exercises)
            win.close()
            return
        elif ev == '-ADD_EXERCISE-':
            if (vals['-INPUT_ENGLISH-'] == '' or vals['-INPUT_FORMULA-'] == ''):
                sg.popup("Inputted sentence or formula is empty.")
                continue
            try:
                formula = Formula.parse(
                    "".join(vals['-INPUT_FORMULA-'].split()))
                sentence = vals['-INPUT_ENGLISH-']
                exercises.append(
                    {"english": sentence, "formula": str(formula)})
                win['-INPUT_ENGLISH-'].update("")
                win['-INPUT_FORMULA-'].update("")
                sg.popup("Exercise saved successfully!")
            except Exception as e:
                sg.popup(str(e), 'Error parsing')
                continue
            print(exercises)
        elif ev == '-NEXT_EXERCISE-':
            saved_ex_index += 1
        elif ev == '-PREV_EXERCISE-':
            saved_ex_index -= 1
        elif ev == '-DEL_EXERCISE-':
            exercises.pop(saved_ex_index)
            saved_ex_index = 0
            sg.popup("Deleted")
        elif ev == '-HELP_BUTTON-':
            show_instructions("Formula Guidelines")
        update_saved_ex_view(saved_ex_index)


def create_layout_game():
    """ Create and return a fresh layout for the propositional logic game """
    input_buttons_layout = [[], [], []]
    label_val_map = {}
    for c in Connective:
        label_val_map[f"{c.name} {c.value}"] = f'{c.value}'
    cnt = 0
    for label, val in label_val_map.items():
        input_buttons_layout[0 if cnt < 3 else 1].append(
            sg.Button(label, font="Verdana 14", key=f'INPUT_BUTTON_{val}'))
        cnt += 1
    for var in prop_letters[:MAX_PROPOSITIONS]+['(', ')']:
        input_buttons_layout[2].append(
            sg.pin(sg.Button(var, font='Verdana 14', key=f'INPUT_BUTTON_{var}')))
    input_buttons_layout[2].append(
        sg.Button('DEL', font='Verdana 14', key='-DEL_SELECTION-', tooltip='Delete Input'),)

    answer_frame = sg.Frame("Answer",
                            layout=[[sg.Multiline(tooltip="Enter your answer in this box", key='-ANSWER-',
                                                  size=(15, 1), no_scrollbar=True, font='Arial 20'),
                                     sg.Image(key='-ANSWER_FEEDBACK-')],
                                    [sg.Text(
                                        "", key='-SOLUTION-', text_color='Light Green', visible=True)],
                                    [sg.Button('Submit', key='-CHECK_ANSWER-',
                                               )]
                                    ], expand_y=True, element_justification='c')

    game_layout = [[sg.Frame(None, [[sg.Multiline(key='-QUESTION-', font='Helvetica 20',
                                                  size=(44, 3), disabled=True, background_color=sg.theme_background_color())]],
                             relief=sg.RELIEF_RAISED, border_width=3, pad=((0, 0), (10, 0)))],
                   sg.vtop([sg.Frame("Input Options", input_buttons_layout),
                            answer_frame,]),
                   [sg.Button('Quit', key='-QUIT-'),
                    sg.Button("Next Question", key='-NEXT_QUESTION-', visible=False)]]

    info_top = sg.Frame(title=None, expand_x=True, layout=[[sg.Text(
        'Question 0 of 10', font="Verdana 18 bold", key='-QUESTION_NUMBER-'), sg.Push(), sg.Text('Score: 0', key='-SCORE-')]])

    return [[sg.Column([[info_top]]+game_layout, element_justification='c')]]


def game_loop(win: sg.Window, difficulty_str: str, num_questions: int, use_saved: bool):
    """ Event Handler for the game section """
    difficulty = {'Easy': 1, 'Normal': 2, 'Hard': 3}[difficulty_str]
    exercises = []

    # Load saved exercises from saved exercises file.
    # If not enough saved exercises or {use_saved} is false, generate random exercises of specified difficulty
    # to make the difference.
    if (use_saved):
        saved_exercises = load_saved_exercises()
        for saved_exercise in random.sample(saved_exercises,
                                            min(num_questions, len(saved_exercises))):
            exercises.append(
                Exercise(formula_str=saved_exercise['formula'], english_repr=saved_exercise['english']))
    for _ in range(num_questions-len(exercises)):
        exercises.append(Exercise(difficulty))
    """ Get the next exercise and update the display elements accordingly """
    def load_next_exercise(qn_num):
        exercise: Exercise = exercises[qn_num-1]
        win['-QUESTION_NUMBER-'].update(
            f"Question {qn_num} of {num_questions}")
        pretty_print_exercise(win['-QUESTION-'], exercise)
        win['-ANSWER_FEEDBACK-'].update(data=None)
        win['-SOLUTION-'].update(visible=False)
        for var in prop_letters[:MAX_PROPOSITIONS]:
            win[f'INPUT_BUTTON_{var}'].update(
                visible=True if (var in exercise.formula.variables()) else False)
        win['-NEXT_QUESTION-'].update(visible=False)
        win['-CHECK_ANSWER-'].update(disabled=False)
        win['-ANSWER-'].update(value='', disabled=False)
        print("Solution:", exercise.formula)
        return exercise

    qn_num = 1
    curr_score = 0
    curr_question = load_next_exercise(qn_num)

    while True:
        ev, vals = win.read()
        print(ev, vals)
        if ev in [sg.WIN_CLOSED, '-QUIT-', 'Exit']:
            win.close()
            return
        # Handle input if user clicks an input button
        if 'INPUT_BUTTON' in ev:
            print('button pressed')
            insert_string(win['-ANSWER-'].widget, ev.split('_')[-1])
        elif ev == '-DEL_SELECTION-':
            tk_text = win['-ANSWER-'].widget
            if tk_text.tag_ranges('sel') == ():
                tk_text.delete('insert -1c')
            else:
                start, end = tk_text.tag_ranges('sel')
                tk_text.delete(start, end)
        # Validate the user's input is non-empty and well-formed
        # If so, check that is logically equivalent to the canonical formula and show the corresponding result
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
                    win['-SCORE-'].update(f"Score: {curr_score}")
                    win['-ANSWER_FEEDBACK-'].update(
                        data=CHECK, subsample=12)
                else:
                    win['-ANSWER_FEEDBACK-'].update(
                        data=sg.RED_X_BASE64, subsample=2)
                    print("wrong")

                win['-SOLUTION-'].update(value=f'Solution: {str(curr_question.formula)}',
                                         visible=True)

                win['-ANSWER-'].update(disabled=True)
                win['-CHECK_ANSWER-'].update(disabled=True)
                win['-NEXT_QUESTION-'].update(visible=True)

            except Exception as e:
                print(e)
                show_instructions("Answer is not well-formed")
        elif ev == '-NEXT_QUESTION-':
            qn_num += 1
            if (qn_num > num_questions):
                sg.popup(f"Congrats, your score is {curr_score}")
                win.close()
                return
            curr_question = load_next_exercise(qn_num)


if __name__ == '__main__':
    # sg.theme('Blue Purple')
    sg.theme('Dark Blue 2')
    sg.set_options(font=('Verdana', 18), element_size=(60, 1))
    sg.DEFAULT_TEXT_JUSTIFICATION = 'l'
    # Layout for the main menu
    layout_menu = [[sg.Column(
        [[sg.Text(APP_TITLE, key='-TITLE-', font=('Cambria', 40), text_color='Yellow')],
         [sg.Image(data=MAIN_MENU_ICON_B64, subsample=12)],
         [sg.Button("Play Game", key='-PLAY-',
                    font=MENU_FONT, auto_size_button=True, pad=((0, 0), (5, 15)))],
         [sg.Button("Exercise Editor", key='-CREATE-', font=MENU_FONT, auto_size_button=True)]],
        element_justification='c')]]
    layout = [[sg.Column(layout_menu, key='-COL1-')]]

    window = sg.Window(MENU_TITLE, layout, finalize=True)

    while True:
        # Event Handler for the main menu
        event, values = window.read()
        print(event, values)
        if event in (None, sg.WIN_CLOSED):
            break
        if event == '-PLAY-':
            ev, vals_settings = sg.Window('Game Settings', [[sg.Text("Difficulty:"),
                                                             sg.Combo(['Easy', 'Normal', 'Hard'], default_value='Normal', readonly=True)],
                                                            [sg.Text("Number of Exercises:"),
                                                            sg.Combo([5, 10, 15], default_value=10, readonly=True)],
                                                            [sg.Checkbox(
                                                                "Prefer Saved Exercises")],
                                                            [sg.Button("Play!")]]).read(close=True)
            if (ev != 'Play!'):
                continue
            print(f"Read pop-up | {ev} {vals_settings}")
            window.hide()
            win2 = sg.Window(
                'Game', layout=create_layout_game(), finalize=True)
            game_loop(win2, *(vals_settings[k] for k in vals_settings))
            print('back to main from play')
            window.UnHide()
        elif event == '-INFO-':
            show_instructions()
        elif event == '-CREATE-':
            window.hide()
            win2 = sg.Window('Exercise Creator',
                             layout=create_layout_add_exercise(), finalize=True)
            add_exercise_loop(win2)
            print('back to main from create')
            window.UnHide()
    window.close()
