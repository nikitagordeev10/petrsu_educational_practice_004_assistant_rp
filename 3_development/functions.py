import json
from datetime import datetime


def jsonify_txt():
    file = 'text.txt'

    with open(file, 'r', encoding='windows-1251') as file:
        text = file.read()

    projects = {}
    current_project = None

    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('Проект:'):
            if current_project:
                projects[current_project['project_name']] = current_project['tasks']
            current_project = {'project_name': line.split(': ')[1], 'tasks': []}
        elif line.startswith('Задача:'):
            task = {'task': line.split(': ')[1]}
        elif line.startswith('Подпроект:'):
            task['subproject_name'] = line.split(': ')[1]
        elif line.startswith('Ответственный:'):
            task['task_executor'] = line.split(': ')[1]
        elif line.startswith('Срок:'):
            task['deadline'] = line.split(': ')[1]
        elif line.startswith('Статус:'):
            task['state'] = line.split(': ')[1]
        elif line.startswith('Комментарий:'):
            task['comment'] = line.split(': ')[1]
        elif line.startswith('Руководитель:'):
            task['task_creator'] = line.split(': ')[1]
            current_project['tasks'].append(task)
        elif line.startswith('Проект:') and current_project:
            current_project['tasks'].append(task)

    if current_project:
        projects[current_project['project_name']] = current_project['tasks']

    # дополнительно, при работе удалить
    with open('projects.json', 'w', encoding='utf-8') as json_file:
        json.dump(projects, json_file, ensure_ascii=False, indent=4)

    # json_data = json.dumps(projects, ensure_ascii=False, indent=4)
    return projects

jsonify_txt()
