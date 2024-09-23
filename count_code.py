import os


def count_lines_in_file(file_path):
    """Возвращает количество строк в указанном файле."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return sum(1 for line in file)


def count_lines_in_directory(directory, exclude_dirs):
    """Рекурсивно подсчитывает количество строк кода в указанной директории, исключая определенные папки."""
    total_lines = 0
    for root, dirs, files in os.walk(directory):
        # Удаляем из обхода папки, которые нужно исключить
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith(('.py', '.js', '.html', '.css', '.java', '.cpp', '.h')):
                try:
                    total_lines += count_lines_in_file(file_path)
                except Exception as e:
                    print(f"Не удалось обработать файл {file_path}: {e}")
    return total_lines


if __name__ == "__main__":
    # Получаем путь к директории, в которой находится этот скрипт
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Список папок, которые нужно исключить из обхода
    exclude_dirs = {'.venv', '.git', '.idea', '__pycache__'}

    total_lines = count_lines_in_directory(script_directory, exclude_dirs)
    print(f"Общее количество строк кода: {total_lines}")