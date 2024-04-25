from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

from config import *
from functions import jsonify_txt

# Define the SQLAlchemy engine
engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}'
                       f'@{DB_HOST}:{DB_PORT}/{DB_NAME}')
Base = declarative_base()


# Define the SQLAlchemy models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    telegram_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)

    role = relationship("Role", back_populates="users")


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)  # Change here
    role_name = Column(String, nullable=False)

    users = relationship("User", back_populates="role")


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    task_creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    task_executor_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    task_name = Column(String, nullable=False)
    subtask_name = Column(String)
    task_description = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    deadline = Column(DateTime)
    state = Column(Boolean)
    comment = Column(Text)

    task_executor = relationship("User", foreign_keys=[task_executor_id])
    task_creator = relationship("User", foreign_keys=[task_creator_id])


class TaskAssignment(Base):
    __tablename__ = 'task_assignments'
    task_id = Column(Integer, ForeignKey('tasks.id'), primary_key=True)
    task_executor_id = Column(Integer, ForeignKey('users.id'), primary_key=True)


# Create the tables in the database
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()


# Function to add users to the database
def add_user(username, role_id, telegram_id):
    user = User(username=username, role_id=role_id, telegram_id=telegram_id, created_at=datetime.now())
    session.add(user)
    session.commit()
    return user


# Function to add tasks to the database
def add_task(task_creator_id, task_executor_id, task_name, subtask_name=None, task_description=None, deadline=None,
             state=None, comment=None):
    task = Task(task_creator_id=task_creator_id, task_executor_id=task_executor_id, task_name=task_name,
                subtask_name=subtask_name, task_description=task_description, deadline=deadline,
                state=state, comment=comment)
    session.add(task)
    session.commit()
    return task


# Function to add roles to the database
def add_role(role_name):
    role = session.query(Role).filter_by(role_name=role_name).first()
    if not role:
        role = Role(role_name=role_name)
        session.add(role)
        session.commit()
    return role


# Define roles
roles_data = [
    {"role_name": "creator"},
    {"role_name": "executor"}
]

# Add roles to the database
for role_data in roles_data:
    add_role(**role_data)
session.commit()

# Example data for users and tasks (replace it with your actual data)
users_data = [
    {"username": "creator1", "role_id": 1, "telegram_id": 123456},
    {"username": "executor1", "role_id": 2, "telegram_id": 987654}
]

## получение json из файла txt
tasks_data = jsonify_txt()

# Add users and tasks to the database
for user_data in users_data:
    add_user(**user_data)

print(tasks_data)
if tasks_data is not None:
    for project, tasks in tasks_data.items():
        for task_data in tasks:
            task_data["task_creator_id"] = 1  # Assuming the creator's ID is 1
            add_task(**task_data)
else:
    print("No tasks data provided or data is empty.")

# Close the session
session.close()
