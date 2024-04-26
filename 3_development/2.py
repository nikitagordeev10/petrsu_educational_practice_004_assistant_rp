def parse_tasks(text):
    projects = {}
    current_project = None
    current_subtitle = None

    lines = text.strip().split('\n')
    for line in lines:
        if line.startswith('Заголовок:'):
            current_project = re.search(r'Заголовок: (.+)', line).group(1)
            projects[current_project] = []
        elif line.startswith('Подзаголовок:'):
            current_subtitle = re.search(r'Подзаголовок: (.+)', line).group(1)
            projects[current_project].append({current_subtitle: []})
        elif line.startswith('Задача:'):
            task = re.search(r'Задача: (.+)', line).group(1)
            responsible_match = re.search(r'Ответственный: (.+)', lines[lines.index(line) + 1])
            responsible = responsible_match.group(1) if responsible_match else None
            deadline_match = re.search(r'Срок: (.+)', lines[lines.index(line) + 2])
            deadline = deadline_match.group(1) if deadline_match else None
            if current_subtitle:
                projects[current_project][-1][current_subtitle].append({
                    "Задача": task,
                    "Ответственный": responsible,
                    "Срок": deadline
                })
            else:
                projects[current_project].append({
                    "Задача": task,
                    "Ответственный": responsible,
                    "Срок": deadline
                })

    return projects

if __name__ == "__main__":
    with open('status_4.txt', 'r', encoding='utf-8') as file:
        text = file.read()

    parsed_data = parse_tasks(text)
    with open('status_5.json', 'w', encoding='utf-8') as json_file:
        json.dump(parsed_data, json_file, indent=2, ensure_ascii=False)