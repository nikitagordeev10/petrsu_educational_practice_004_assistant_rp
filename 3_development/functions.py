import json


def jsonify_txt():
    file = 'text.txt'

    with open(file, 'r', encoding='windows-1251') as file:
        text = file.read()

    projects = {}
    current_project = None

    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('Проект:'):
            # If it's a new project, save the current project (if any)
            if current_project:
                projects[current_project['Проект']] = current_project['Задачи']
            # Start a new project
            current_project = {'Проект': line.split(': ')[1], 'Задачи': []}
        elif line.startswith('Задача:'):
            # Start a new task
            task = {'Задача': line.split(': ')[1]}
        elif line.startswith('Ответственный:'):
            task['Ответственный'] = line.split(': ')[1]
        elif line.startswith('Срок:'):
            task['Срок'] = line.split(': ')[1]
            # Append the task to the current project
            current_project['Задачи'].append(task)
        elif line.startswith('Проект:') and current_project:
            # Save the current task before starting a new project
            current_project['Задачи'].append(task)

    # Append the last project
    if current_project:
        projects[current_project['Проект']] = current_project['Задачи']


    # json_data = json.dumps(projects, ensure_ascii=False, indent=4)
    return projects
