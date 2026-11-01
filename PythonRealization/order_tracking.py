import json
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "database.json"


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


def track_order():
    database = load_database()

    if database is None:
        return

    try:
        order_id = int(input("Введите номер заказа: "))
    except ValueError:
        print("Ошибка: номер заказа должен быть целым числом.")
        return

    # Поиск заказа
    order = next(
        (item for item in database["ORDER"]
         if item["order_id"] == order_id),
        None
    )

    if order is None:
        print("Ошибка: заказ с таким номером не найден.")
        return

    # Получение текущего этапа
    current_stage = next(
        (item for item in database["ORDER_STAGE"]
         if item["stage_id"] == order["stage_id"]),
        None
    )

    if current_stage is None:
        print("Ошибка: текущий этап заказа не найден.")
        return

    print("\nТекущий этап:", current_stage["stage_name"])
    print("Статус заказа:", order["status"])
    print("Срок выполнения:", order["deadline"])

    if current_stage["stage_name"] == "Завершён":
        print("\nЗаказ уже завершён.")
        return

    # Вывод доступных этапов
    print("\nДоступные этапы:")

    for stage in database["ORDER_STAGE"]:
        print(stage["stage_id"], "-", stage["stage_name"])

    try:
        new_stage_id = int(input("\nВведите номер нового этапа: "))
    except ValueError:
        print("Ошибка: номер этапа должен быть целым числом.")
        return

    # Поиск выбранного этапа
    new_stage = next(
        (item for item in database["ORDER_STAGE"]
         if item["stage_id"] == new_stage_id),
        None
    )

    if new_stage is None:
        print("Ошибка: выбранный этап не существует.")
        return

    # Обновление этапа
    order["stage_id"] = new_stage_id

    if new_stage["stage_name"] == "Завершён":
        order["status"] = "Завершён"
    else:
        deadline = datetime.fromisoformat(order["deadline"])
        current_date = datetime.now()

        if current_date > deadline:
            order["status"] = "Просрочен"
        else:
            order["status"] = "В работе"

    # Сохранение изменений
    try:
        save_database(database)
    except OSError:
        print("Ошибка: не удалось сохранить изменения.")
        return

    print("\nИнформация о заказе обновлена.")
    print("Новый этап:", new_stage["stage_name"])
    print("Статус заказа:", order["status"])


if __name__ == "__main__":
    track_order()