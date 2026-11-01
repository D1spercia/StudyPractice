import json
import os
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "database.json"

MODEL_EXTENSIONS = [".fbx", ".obj", ".blend"]
TEXTURE_EXTENSIONS = [".png", ".jpg", ".tga"]
DOCUMENT_EXTENSIONS = [".txt", ".pdf"]

ALLOWED_EXTENSIONS = (
    MODEL_EXTENSIONS
    + TEXTURE_EXTENSIONS
    + DOCUMENT_EXTENSIONS
)


def load_database():
    try:
        with open(DATABASE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        print("Ошибка: файл базы данных не найден.")
        return None

    except json.JSONDecodeError:
        print("Ошибка: файл базы данных содержит некорректные данные.")
        return None


def save_database(database):
    with open(DATABASE_PATH, "w", encoding="utf-8") as file:
        json.dump(database, file, ensure_ascii=False, indent=4)


def get_next_id(records, field):
    return max(
        (item[field] for item in records),
        default=0
    ) + 1


def check_asset():
    database = load_database()

    if database is None:
        return

    # Ввод и проверка номера заказа
    try:
        order_id = int(input("Введите номер заказа: "))
    except ValueError:
        print("Ошибка: номер заказа должен быть целым числом.")
        return

    order = next(
        (item for item in database["ORDER"]
         if item["order_id"] == order_id),
        None
    )

    if order is None:
        print("Ошибка: заказ с таким номером не найден.")
        return

    # Ввод данных 3D-актива
    asset_name = input("Введите название 3D-актива: ").strip()
    folder_path = input("Введите путь к папке с файлами: ").strip()

    if not asset_name:
        print("Ошибка: название 3D-актива не может быть пустым.")
        return

    if not os.path.isdir(folder_path):
        print("Ошибка: указанная папка не существует.")
        return

    try:
        files = []

        for name in os.listdir(folder_path):
            full_path = os.path.join(folder_path, name)

            if os.path.isfile(full_path):
                extension = os.path.splitext(name)[1].lower()
                size = os.path.getsize(full_path)

                files.append({
                    "name": name,
                    "extension": extension,
                    "size": size
                })

        # Проверка пяти критериев
        has_model = any(
            file["extension"] in MODEL_EXTENSIONS
            for file in files
        )

        has_texture = any(
            file["extension"] in TEXTURE_EXTENSIONS
            for file in files
        )

        has_document = any(
            file["extension"] in DOCUMENT_EXTENSIONS
            for file in files
        )

        no_empty_files = all(
            file["size"] > 0
            for file in files
        )

        all_extensions_allowed = all(
            file["extension"] in ALLOWED_EXTENSIONS
            for file in files
        )

        results = [
            ("Наличие 3D-модели", has_model),
            ("Наличие текстур", has_texture),
            ("Наличие документации", has_document),
            ("Отсутствие пустых файлов", no_empty_files),
            ("Допустимые расширения файлов", all_extensions_allowed)
        ]

        # Определение итогового результата
        overall_status = (
            "Успешно"
            if all(status for name, status in results)
            else "Не пройдена"
        )

        # Создание записи 3D-актива
        asset_id = get_next_id(
            database["THREE_D_ASSET"], "asset_id"
        )

        asset = {
            "asset_id": asset_id,
            "order_id": order_id,
            "asset_name": asset_name,
            "directory_path": folder_path
        }

        database["THREE_D_ASSET"].append(asset)

        # Создание записи проверки
        check_id = get_next_id(
            database["CHECK"], "check_id"
        )

        check_record = {
            "check_id": check_id,
            "asset_id": asset_id,
            "check_date": datetime.now().isoformat(timespec="seconds"),
            "overall_status": overall_status
        }

        database["CHECK"].append(check_record)

        # Сохранение информации о файлах
        for file in files:
            file_id = get_next_id(
                database["FILE"], "file_id"
            )

            database["FILE"].append({
                "file_id": file_id,
                "check_id": check_id,
                "file_name": file["name"],
                "extension": file["extension"],
                "size_bytes": file["size"]
            })

        # Сохранение критериев проверки
        for criterion_name, status in results:
            criterion = next(
                (item for item in database["CRITERION"]
                 if item["criterion_name"] == criterion_name),
                None
            )

            if criterion is None:
                criterion_id = get_next_id(
                    database["CRITERION"], "criterion_id"
                )

                criterion = {
                    "criterion_id": criterion_id,
                    "criterion_name": criterion_name,
                    "criterion_description": criterion_name
                }

                database["CRITERION"].append(criterion)

            result_id = get_next_id(
                database["CHECK_RESULT"], "result_id"
            )

            database["CHECK_RESULT"].append({
                "result_id": result_id,
                "check_id": check_id,
                "criterion_id": criterion["criterion_id"],
                "result_status": status,
                "comment": (
                    "Критерий выполнен"
                    if status
                    else "Критерий не выполнен"
                )
            })

        # Сохранение базы данных
        save_database(database)

        # Вывод результатов
        print("\nНайденные файлы:")

        for file in files:
            print(
                file["name"],
                "-",
                file["size"],
                "байт"
            )

        print("\nРезультаты проверки:")

        for criterion_name, status in results:
            if status:
                print(criterion_name + ": выполнено")
            else:
                print(criterion_name + ": не выполнено")

        print("\nИтоговый статус:", overall_status)

    except PermissionError:
        print("Ошибка: нет доступа к содержимому папки.")

    except OSError:
        print("Ошибка при чтении файлов или сохранении данных.")


if __name__ == "__main__":
    check_asset()