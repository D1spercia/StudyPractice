import os

#Допустимые расширения
model_extensions = [".fbx", ".obj", ".blend"]
texture_extensions = [".png", ".jpg", ".tga"]
document_extensions = [".txt", ".pdf"]

allowed_extensions = (model_extensions + texture_extensions + document_extensions)

#Ввод пути к папке, которую надо проверить
folder_path = input("Введите путь к папке с 3D-активом: ")

if not os.path.isdir(folder_path):
    print("Ошибка: папка не существует")
else:
    try:
        file_names = os.listdir(folder_path)

        files = []

        for name in file_names:
            full_path = os.path.join(folder_path, name)

            if os.path.isfile(full_path):
                extension = os.path.splitext(name)[1].lower()
                size = os.path.getsize(full_path)

                files.append({"name": name, "extension": extension, "size": size})

        # Проверка пяти критериев
        has_model = any(file["extension"] in model_extensions for file in files)

        has_texture = any(file["extension"] in texture_extensions for file in files)

        has_document = any(file["extension"] in document_extensions for file in files)

        no_empty_files = all(file["size"] > 0 for file in files)

        all_extensions_allowed = all(file["extension"] in allowed_extensions for file in files)

        results = [
                ("Наличие 3D-модели", has_model), 
                ("Наличие текстур", has_texture),
                ("Наличие документации", has_document),
                ("Отсутствие пустых файлов", no_empty_files),
                ("Допустимые расширения файлов", all_extensions_allowed)
            ]

        #Вывод списка найденых файлов
        print("\nНайденные файлы")
        for file in files:
            print(
                file["name"],
                ":",
                file["size"],
                "байт"
            )

        print("\nРезультаты проверки: ")
        for name, status in results:
            if status:
                print(name + ": выполнено")
            else:
                print(name + ": не выполнено")

        #Определение общего статуса
        if all(status for name, status in results):
            print("\nИтоговый статус: Успешно")
        else:
            print("\nИтоговый статус: Не пройдено")

    except PermissionError:
        print("Ошибка: нет доступа к содержимому папки")
    except OSError:
        print("Ошибка при чтении содержимого папки")