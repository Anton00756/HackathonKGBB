import json
import os

import requests

from base_source import BaseSource


class SravniRuSource(BaseSource):
    """URL: https://www.sravni.ru/bank/promsvjazbank/otzyvy/"""

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
        for page in range(10):
            response = self.session.get(
                f'https://www.sravni.ru/proxy-reviews/reviews?filterBy=withRates&locationRoute=&newIds=true&orderBy='
                f'byDate&pageIndex={page}&pageSize=10&rated=any&reviewObjectId=5bb4f769245bc22a520a62a5&reviewObject'
                f'Type=banks&specificProductId=&withVotes=true'
            )
            data = response.json()
            for item in data['items']:
                if item['id'] > self.app_data['start_id']:
                    if item['id'] > self.max_id:
                        self.max_id = item['id']
                    reviews.append(self.clean_text(item['text']))
            if not len(data['items']) or data['items'][0]['id'] < self.app_data['start_id']:
                break
        return reviews

    def update_last_review(self):
        self.app_data['start_id'] = self.max_id
        with open(self.data_path, 'w', encoding='utf-8') as file:
            json.dump(self.app_data, file, indent=4, ensure_ascii=False)
