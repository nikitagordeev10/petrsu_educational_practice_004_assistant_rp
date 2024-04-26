from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


from config import *
from functions import jsonify_txt

# Определяем движок SQLAlchemy
engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}'
                       f'@{DB_HOST}:{DB_PORT}/{DB_NAME}')
Base = declarative_base()

# Определяем модели SQLAlchemy
class Task(Base):
    __tablename__ = 'simple_table'
    id = Column(Integer, primary_key=True)
    task_creator = Column(String)
    task_executor = Column(String)
    project_name = Column(String)
    subproject_name = Column(String)
    task = Column(String)
    state = Column(String)
    comment = Column(String)
    deadline = Column(String)

# Создаем таблицы в базе данных
Base.metadata.create_all(engine)

# Создаем сессию
Session = sessionmaker(bind=engine)
session = Session()


# Функция для добавления задач в базу данных
def add_task(task_creator, task_executor, task, state, comment, deadline):
    new_task = Task(task_creator=task_creator, task_executor=task_executor,
                    task=task, state=state, comment=comment, deadline=deadline)
    session.add(new_task)
    try:
        session.commit()
        return new_task
    except Exception as e:
        session.rollback()  # roll back the transaction if any exception occurs
        print(f"An error occurred: {str(e)}")
        return None


## получение json из файла txt
tasks_data = jsonify_txt()


print(tasks_data)
if tasks_data is not None:
    for project, tasks in tasks_data.items():
        for task_data in tasks:
            add_task(**task_data)
else:
    print("Не предоставлены данные о задачах или данные пусты.")

# Закрываем сессию
session.close()
