import os

def print_structure(startpath):
    # СПИСОК ТОГО, ЧТО СКРЫВАЕМ:
    exclude_dirs = {'venv', 'env', '.git', '__pycache__', '.idea', 'media'}
    
    for root, dirs, files in os.walk(startpath):
        # Фильтруем папки на лету
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f'{indent}{os.path.basename(root)}/')
        
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            # Не показываем сам этот скрипт и базу данных, чтобы не мешались
            if f not in ['check_structure.py', 'db.sqlite3']:
                print(f'{subindent}{f}')

if __name__ == "__main__":
    print_structure('.')
    input("\nНажми Enter, чтобы выйти...")