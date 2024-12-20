import requests
import json
import os

DATA_PATH = '../reviews.json'

if __name__ == '__main__':
    if os.path.exists(DATA_PATH) and False:
        with open(DATA_PATH, 'r', encoding='utf-8') as file:
            app_data = json.load(file)
    else:
        app_data = {'start_id': 0, 'reviews': []}

    session = requests.Session()
    fields_to_save = {'id', 'title', 'text', 'grade'}  # + dateCreate
    max_id = app_data['start_id']
    for page in range(1, 10):  # 101
        response = session.get(
            f'https://www.banki.ru/services/responses/list/ajax/?page={page}&is_countable=on&bank=promsvyazbank'
        )
        data = response.json()
        for item in data['data']:
            if item['id'] > app_data['start_id']:
                if item['id'] > max_id:
                    max_id = item['id']
                app_data['reviews'].append({key: value for key, value in item.items() if key in fields_to_save})
        if len(data['data']) and not data['hasMorePages'] or data['data'][0]['id'] < app_data['start_id']:
            break
        page += 1
    app_data['start_id'] = max_id

    with open(DATA_PATH, 'w', encoding='utf-8') as file:
        json.dump(app_data, file, indent=4, ensure_ascii=False)
    for patch in range(0, len(app_data['reviews']), 15):
        print(app_data['reviews'][patch: patch + 15])
