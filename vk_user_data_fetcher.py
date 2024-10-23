import requests
import json

def vk_api_request(method, token, params):
    url = f"https://api.vk.com/method/{method}"
    params['access_token'] = token
    params['v'] = '5.131' 
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if 'error' in data:
            raise Exception(f"API Error: {data['error']['error_msg']}")
        return data['response']
    else:
        raise Exception(f"HTTP Error: {response.status_code}")

def get_user_data(token, user_id):
    try:
        user_info = vk_api_request('users.get', token, {'user_ids': user_id, 'fields': 'followers_count'})[0]
        print("Информация о пользователе получена успешно.")
    except Exception as e:
        print(f"Ошибка при получении информации о пользователе: {e}")
        return None

    try:
        followers = vk_api_request('users.getFollowers', token, {'user_id': user_id, 'count': 1000})
        followers_count = followers.get('count', 0)
        followers_list = followers.get('items', [])
        print(f"Фолловеры получены успешно: {followers_count} фолловеров.")
    except Exception as e:
        print(f"Ошибка при получении фолловеров: {e}")
        followers_count = 0
        followers_list = []

    try:
        subscriptions_list = []
        offset = 0
        count_per_request = 100

        while True:
            subscriptions = vk_api_request('users.getSubscriptions', token, {'user_id': user_id, 'extended': 1, 'offset': offset, 'count': count_per_request})
            items = subscriptions.get('items', [])
            subscriptions_list.extend(items)

            if len(items) < count_per_request:
                break

            offset += count_per_request

        subscriptions_count = len(subscriptions_list)
        print(f"Подписки получены успешно: {subscriptions_count} подписок.")
    except Exception as e:
        print(f"Ошибка при получении подписок: {e}")
        subscriptions_count = 0
        subscriptions_list = []

    groups = [sub for sub in subscriptions_list if sub.get('type') == 'group']
    groups_count = len(groups)
    print(f"Группы получены успешно: {groups_count} групп.")

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
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    token = input("Введите токен доступа: ")
    user_id = input("Введите VK User ID: ")
    
    output_file = input("Введите путь к файлу для сохранения данных (нажмите Enter для использования пути по умолчанию 'output.json'): ")
    
    if not output_file:
        output_file = "output.json"

    try:
        user_data = get_user_data(token, user_id)

        if user_data:
            save_to_json(user_data, output_file)
            print(f"Данные сохранены в файл {output_file}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == '__main__':
    main()
