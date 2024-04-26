import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import *
from send_to_db import Task

# Определяем движок SQLAlchemy
engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

# Создаем сессию
Session = sessionmaker(bind=engine)
session = Session()

# Получаем все задачи из базы данных
tasks_from_db = session.query(Task).all()

# Преобразуем задачи в формат JSON
tasks_json = []
for task in tasks_from_db:
    tasks_json.append({
        "id": task.id,
        "task_creator": task.task_creator,
        "task_executor": task.task_executor,
        "project_name": task.project_name,
        "subproject_name": task.subproject_name,
        "task": task.task,
        "state": task.state,
        "comment": task.comment,
        "deadline": task.deadline
    })

# Сохраняем данные в файл
with open('get_from_db.json', 'w', encoding='windows-1251') as file:
    json.dump(tasks_json, file, ensure_ascii=False, indent=4)

# Закрываем сессию
session.close()
