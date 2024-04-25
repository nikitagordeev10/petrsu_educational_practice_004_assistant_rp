from libraries import *
from dbpswd import *

# Path to your file
file_path = "../3_development/text.txt"

# Function to parse date string into datetime format
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%d.%m.%Y")
    except ValueError:
        return None

# Function to read data from the file and load it into the database
def load_data_to_postgres(file_path):
    # Establish connection to the database
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST, port=PORT)
    cursor = conn.cursor()

    # Open the file and read data
    with open(file_path, "r", encoding="utf-16") as file:
        lines = file.readlines()
        project = ""
        for line in lines:
            line = line.strip()
            if line.startswith("Проект:"):
                project = line.split(":")[1].strip()
            elif line.startswith("Задача:"):
                task_name = line.split(":")[1].strip()
            elif line.startswith("Ответственный:"):
                responsible = line.split(":")[1].strip()
            elif line.startswith("Срок:"):
                deadline_str = line.split(":")[1].strip().split("(")[0].strip()
                deadline = parse_date(deadline_str)
            elif line.startswith("Статус:"):
                state = line.split(":")[1].strip() == "сделано"
            elif line.startswith("Комментарий:"):
                comment = line.split(":")[1].strip()

                # Insert data into the database
                cursor.execute("""
                    INSERT INTO task(task_name, subtask_name, task_description, created_at, deadline, state, comment)
                    VALUES (%s, %s, %s, NOW(), %s, %s, %s);
                """, (project, task_name, responsible, deadline, state, comment))
                conn.commit()

    # Close the connection
    cursor.close()
    conn.close()

# Call the function to load data
load_data_to_postgres(file_path)