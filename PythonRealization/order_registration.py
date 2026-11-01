import json
from pathlib import Path
from datetime import datetime

# Путь к JSON-файлу
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "database.json"


# Загрузка данных из JSON
def load_database():
    try:
        with open(DATABASE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        print("Ошибка: файл database.json не найден.")
        return None

    except json.JSONDecodeError:
        print("Ошибка: файл database.json содержит некорректные данные.")
        return None


# Сохранение данных в JSON
def save_database(database):
    with open(DATABASE_PATH, "w", encoding="utf-8") as file:
        json.dump(database, file, ensure_ascii=False, indent=4)


# Основная программа
def register_order():

    database = load_database()

    if database is None:
        return

    print("Регистрация нового заказа")

    # Ввод данных клиента
    while True:
        client_name = input("Введите имя клиента: ").strip()
        contact_info = input("Введите контактные данные: ").strip()

        if client_name and contact_info:
            break

        print("Ошибка: необходимо заполнить все данные клиента.")

    # Ввод типа 3D-актива
    asset_type = input(
        "Введите тип актива (3D-модель / Текстура): "
    ).strip()

    # Ввод сложности
    complexity = input(
        "Введите сложность (Простая / Средняя / Сложная): "
    ).strip()

    # Ввод количества объектов
    while True:
        try:
            quantity = int(input("Введите количество объектов: "))

            if quantity > 0:
                break

            print("Количество должно быть больше нуля.")

        except ValueError:
            print("Ошибка: введите целое число.")

    # Ввод срока выполнения
    while True:
        deadline_input = input(
            "Введите срок выполнения (ГГГГ-ММ-ДД): "
        )

        try:
            deadline = datetime.strptime(
                deadline_input, "%Y-%m-%d"
            )

            if deadline.date() < datetime.now().date():
                print("Ошибка: срок не может быть в прошлом.")
                continue

            break

        except ValueError:
            print("Ошибка: неверный формат даты.")

    # Поиск позиции в прайс-листе
    selected_price = None

    for item in database["PRICE_LIST"]:
        if (item["asset_type"] == asset_type and
                item["complexity"] == complexity):

            selected_price = item
            break

    if selected_price is None:
        print("Ошибка: подходящая позиция в прайс-листе не найдена.")
        return

    # Поиск клиента по контактным данным
    client_id = None

    for client in database["CLIENT"]:
        if client["contact_info"] == contact_info:
            client_id = client["client_id"]
            break

    # Создание нового клиента, если он отсутствует
    if client_id is None:

        client_id = max(
            (client["client_id"] for client in database["CLIENT"]),
            default=0
        ) + 1

        new_client = {
            "client_id": client_id,
            "client_name": client_name,
            "contact_info": contact_info
        }

        database["CLIENT"].append(new_client)

    

    # Генерация уникального номера заказа
    order_id = max(
        (order["order_id"] for order in database["ORDER"]),
        default=0
    ) + 1

    # Получение начального этапа заказа
    initial_stage = None

    for stage in database["ORDER_STAGE"]:
        if stage["stage_name"] == "Новый заказ":
            initial_stage = stage
            break

    if initial_stage is None:
        print("Ошибка: начальный этап заказа не найден.")
        return

    # Формирование записи заказа
    new_order = {
        "order_id": order_id,
        "client_id": client_id,
        "price_id": selected_price["price_id"],
        "stage_id": initial_stage["stage_id"],
        "quantity": quantity,
        "unit_price": None,
        "total_price": None,
        "order_date": datetime.now().isoformat(timespec="seconds"),
        "deadline": deadline.isoformat(timespec="seconds"),
        "status": "Новый"
    }

    # Добавление заказа в базу данных
    database["ORDER"].append(new_order)

    # Сохранение изменений
    try:
        save_database(database)

    except OSError:
        print("Ошибка: не удалось сохранить данные в JSON-файл.")
        return

    # Вывод результата
    print("\n=== Заказ успешно зарегистрирован ===")
    print("Номер заказа:", order_id)
    print("Клиент:", client_name)
    print("Контактные данные:", contact_info)
    print("Тип актива:", asset_type)
    print("Сложность:", complexity)
    print("Количество объектов:", quantity)
    print("Срок выполнения:", deadline.date())
    print("Начальный этап:", initial_stage["stage_name"])
    print("Статус:", new_order["status"])
    print("Номер позиции прайс-листа:", selected_price["price_id"])


# Запуск программы
if __name__ == "__main__":
    register_order()
