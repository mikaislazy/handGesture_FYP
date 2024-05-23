# handGestureData.py
import json

def load_question(gesture_name, json_file):
    questions = []
    options = []
    with open(json_file, 'r') as f:
        question_bank = json.load(f)
        q_opt = question_bank[gesture_name]["questions"]
        for task in q_opt:
            questions.append(task['question'])
            options.append(task['options'])
    return questions, options

def load_answer(gesture_name, json_file):
    answers = []
    with open(json_file, 'r') as f:
        answers_bank = json.load(f)
        q_a = answers_bank[gesture_name]["answers"]
        for ans in q_a:
            answers.append(ans["correct_option"])
    return answers

GESTURES = [
    'HuoYanYin',
    'ChanDingYin',
    'MiTuoDingYin',
    'Retsu',
    'Rin',
    'Zai',
    'Zen',
    'ZhiJiXiangYin',
    'TaiJiYin'
]
