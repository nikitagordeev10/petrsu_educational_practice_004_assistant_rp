# import json
# from datetime import datetime
#
#
# def txt_to_json():
#     file = 'text.txt'
#
#     with open(file, 'r', encoding='windows-1251') as file:
#         text = file.read()
#
#     projects = {}
#     current_project = None
#
#     for line in text.split('\n'):
#         line = line.strip()
#         if line.startswith('Проект:'):
#             if current_project:
#                 projects[current_project['project_name']] = current_project['task']
#             current_project = {'project_name': line.split(': ')[1], 'task': []}
#         elif line.startswith('Задача:'):
#             task = {'task': line.split(': ')[1]}
#         elif line.startswith('Подпроект:'):
#             task['subproject_name'] = line.split(': ')[1]
#         elif line.startswith('Ответственный:'):
#             task['task_executor'] = line.split(': ')[1]
#         elif line.startswith('Срок:'):
#             task['deadline'] = line.split(': ')[1]
#         elif line.startswith('Статус:'):
#             task['state'] = line.split(': ')[1]
#         elif line.startswith('Комментарий:'):
#             task['comment'] = line.split(': ')[1]
#         elif line.startswith('Руководитель:'):
#             task['task_creator'] = line.split(': ')[1]
#             current_project['task'].append(task)
#         elif line.startswith('Проект:') and current_project:
#             current_project['task'].append(task)
#
#     if current_project:
#         projects[current_project['project_name']] = current_project['task']
#
#     # дополнительно, при работе удалить
#     with open('txt_to_json.json', 'w', encoding='windows-1251') as json_file:
#         json.dump(projects, json_file, ensure_ascii=False, indent=4)
#
#     # json_data = json.dumps(projects, ensure_ascii=False, indent=4)
#     return projects
#
# txt_to_json()


import re
import json

# Открываем файл для чтения
with open("text.txt", "r", encoding="windows-1251") as file:
    lines = file.readlines()

# Инициализируем переменные для хранения данных
projects = []
current_project = None
current_subproject = None

# Проходим по строкам файла
for line in lines:
    # Удаляем "project_name" и "subproject_name" перед "tasks"
    line = re.sub(r'"project_name":\s".+",\n', '', line)
    line = re.sub(r'"subproject_name":\s".+",\n', '', line)

    # Ищем ключевые слова и информацию после них
    project_match = re.match(r"Проект:\s(.+)", line)
    subproject_match = re.match(r"Подпроект:\s(.+)", line)
    task_match = re.match(r"Задача:\s(.+)", line)
    executor_match = re.match(r"Ответственный:\s(.+)", line)
    deadline_match = re.match(r"Срок:\s(.+)", line)
    status_match = re.match(r"Статус:\s(.+)", line)
    comment_match = re.match(r"Комментарий:\s(.+)", line)

    # Если найдено ключевое слово, сохраняем соответствующую информацию
    if project_match:
        # Создаем новый проект
        current_project = {
            "project_name": project_match.group(1),
            "subproject_name": "-",
            "tasks": []
        }
        projects.append(current_project)
    elif subproject_match:
        # Создаем новый подпроект в текущем проекте
        current_subproject = {
            "subproject_name": subproject_match.group(1),
            "tasks": []
        }
        current_project["subproject_name"] = current_subproject["subproject_name"]
    elif task_match:
        # Создаем новую задачу в текущем проекте или подпроекте
        current_task = {
            "task": task_match.group(1),
            "project_name": current_project["project_name"],
            "subproject_name": current_subproject["subproject_name"] if current_subproject else "-"
        }
        current_project["tasks"].append(current_task)
    elif executor_match and current_task:
        current_task["task_executor"] = executor_match.group(1)
    elif deadline_match and current_task:
        current_task["deadline"] = deadline_match.group(1)
    elif status_match and current_task:
        current_task["state"] = status_match.group(1)
    elif comment_match and current_task:
        current_task["comment"] = comment_match.group(1)

# Записываем данные в файл JSON
with open("text.json", "w", encoding="windows-1251") as json_file:
    json.dump(projects, json_file, ensure_ascii=False, indent=4)
