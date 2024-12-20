import json
import os

import requests

from base_source import BaseSource


class BankiRuSource(BaseSource):
    def __init__(self, work_path: str = '.'):
        super().__init__(work_path)
        self.data_path = work_path
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r', encoding='utf-8') as file:
                self.app_data = json.load(file)
        else:
            self.app_data = {'start_id': 0}
        self.max_id = self.app_data['start_id']
        self.session = requests.Session()

    def get_new_reviews(self) -> list[str]:
        reviews = []
        for page in range(1, 10):
            response = self.session.get(
                f'https://www.banki.ru/services/responses/list/ajax/?page={page}&is_countable=on&bank=promsvyazbank'
            )
            data = response.json()
            for item in data['data']:
                if item['id'] > self.app_data['start_id']:
                    if item['id'] > self.max_id:
                        self.max_id = item['id']
                    reviews.append(self.clean_text(item['text']))
            if len(data['data']) and not data['hasMorePages'] or data['data'][0]['id'] < self.app_data['start_id']:
                break
        return reviews

    def update_last_review(self):
        self.app_data['start_id'] = self.max_id
        with open(self.data_path, 'w', encoding='utf-8') as file:
            json.dump(self.app_data, file, indent=4, ensure_ascii=False)
