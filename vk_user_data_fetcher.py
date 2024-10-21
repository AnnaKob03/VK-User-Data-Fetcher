import vk_api
import json
import os

def get_user_data(vk, user_id):
    # Получаем основную информацию о пользователе
    try:
        user_info = vk.users.get(user_ids=user_id, fields='followers_count')[0]
        print("Информация о пользователе получена успешно.")
    except vk_api.exceptions.ApiError as e:
        print(f"Ошибка при получении информации о пользователе: {e}")
        return None

    try:
        # Получаем список фолловеров
        followers = vk.users.getFollowers(user_id=user_id, count=1000)  # Ограничение на 1000
        followers_count = followers.get('count', 0)
        followers_list = followers.get('items', [])
        print(f"Фолловеры получены успешно: {followers_count} фолловеров.")
    except vk_api.exceptions.ApiError as e:
        if e.code == 7:
            print("Недостаточно прав для получения фолловеров.")
            followers_count = 0
            followers_list = []
        else:
            raise e

    try:
        # Получаем все подписки с использованием offset
        subscriptions_list = []
        offset = 0
        count_per_request = 100  # Максимум элементов за один запрос

        while True:
            subscriptions = vk.users.getSubscriptions(user_id=user_id, extended=1, offset=offset, count=count_per_request)
            items = subscriptions.get('items', [])
            subscriptions_list.extend(items)

            if len(items) < count_per_request:
                break  # Все подписки получены

            offset += count_per_request

        subscriptions_count = len(subscriptions_list)
        print(f"Подписки получены успешно: {subscriptions_count} подписок.")
    except vk_api.exceptions.ApiError as e:
        if e.code == 7:
            print("Недостаточно прав для получения подписок.")
            subscriptions_count = 0
            subscriptions_list = []
        else:
            raise e

    try:
        groups = [sub for sub in subscriptions_list if sub.get('type') == 'group']
        groups_count = len(groups)
        print(f"Группы получены успешно: {groups_count} групп.")
    except vk_api.exceptions.ApiError as e:
        if e.code == 7:
            print("Недостаточно прав для получения групп.")
            groups_count = 0
            groups = []
        else:
            raise e

    return {
        "user_info": user_info,
        "followers_count": followers_count,
        "followers": followers_list,
        "subscriptions_count": subscriptions_count,
        "subscriptions": subscriptions_list,
        "groups_count": groups_count,
        "groups": groups
    }

def save_to_json(data, file_path):
    # Сохранение данных в JSON
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    # Запрашиваем токен и ID пользователя через ввод
    token = input("Введите токен доступа: ")
    user_id = input("Введите VK User ID: ")
    
    # Запрашиваем путь для сохранения файла
    output_file = input("Введите путь к файлу для сохранения данных (нажмите Enter для использования пути по умолчанию 'output.json'): ")
    
    # Если пользователь не ввел путь, используем путь по умолчанию
    if not output_file:
        output_file = "output.json"

    try:
        # Создание сессии VK API с использованием токена
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()

        # Получаем данные о пользователе
        user_data = get_user_data(vk, user_id)

        if user_data:
            save_to_json(user_data, output_file)
            print(f"Данные сохранены в файл {output_file}")

    except vk_api.exceptions.ApiError as e:
        print(f"Произошла ошибка при работе с VK API: {e}")
    except ValueError as e:
        print(f"Ошибка данных: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == '__main__':
    main()
