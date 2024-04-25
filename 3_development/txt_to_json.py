from libraries import *

def txt_to_json():
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
                projects[current_project['task_name']] = current_project['tasks']
            # Start a new project
            current_project = {'task_name': line.split(': ')[1], 'tasks': []}
        elif line.startswith('Задача:'):
            # Start a new task
            task = {'task_description': line.split(': ')[1]}
        elif line.startswith('Подзадача:'):
            task['subtask_name'] = line.split(': ')[1]
        elif line.startswith('Ответственный:'):
            task['task_executor_id'] = line.split(': ')[1]
        elif line.startswith('Срок:'):
            task['deadline'] = line.split(': ')[1]
        elif line.startswith('Статус:'):
            task['state'] = line.split(': ')[1]
        elif line.startswith('Комментарий:'):
            task['comment'] = line.split(': ')[1]
            # Append the task to the current project
            current_project['tasks'].append(task)
        elif line.startswith('Проект:') and current_project:
            # Save the current task before starting a new project
            current_project['tasks'].append(task)

    # Append the last project
    if current_project:
        projects[current_project['task_name']] = current_project['tasks']

    # Save data to JSON file
    with open('projects.json', 'w', encoding='utf-8') as json_file:
        json.dump(projects, json_file, ensure_ascii=False, indent=4)

    return projects

txt_to_json()