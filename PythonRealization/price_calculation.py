import json
from pathlib import Path


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


def calculate_order_cost():
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

    # Поиск позиции прайс-листа
    price_id = order["price_id"]

    price_item = next(
        (item for item in database["PRICE_LIST"]
         if item["price_id"] == price_id),
        None
    )

    if price_item is None:
        print("Ошибка: позиция прайс-листа не найдена.")
        return

    # Расчёт стоимости
    unit_price = price_item["base_price"]
    quantity = order["quantity"]
    total_price = unit_price * quantity

    # Сохранение стоимости в заказе
    order["unit_price"] = unit_price
    order["total_price"] = total_price

    try:
        save_database(database)
    except OSError:
        print("Ошибка: не удалось сохранить изменения.")
        return

    print("\nСтоимость заказа успешно рассчитана.")
    print("Номер заказа:", order_id)
    print("Стоимость одного объекта:", unit_price, "руб.")
    print("Количество объектов:", quantity)
    print("Общая стоимость:", total_price, "руб.")


if __name__ == "__main__":
    calculate_order_cost()