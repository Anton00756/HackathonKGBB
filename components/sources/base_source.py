import re
from abc import ABC, abstractmethod


class BaseSource(ABC):
    def __init__(self, work_path: str = '.'):
        pass

    @abstractmethod
    def get_new_reviews(self) -> list[str]:
        pass

    @abstractmethod
    def update_last_review(self):
        pass

    @staticmethod
    def clean_text(text: str) -> str:
        text = text.replace("\\", " ").replace(u"╚", " ").replace(u"╩", " ")
        text = text.lower()
        for block in ['<p>', '</p>', '<li>', '</li>', '<ul>', '</ul>']:
            text = re.sub(block, '', text)
        text = re.sub(r'\-\s\r\n\s{1,}|\-\s\r\n|\r\n', '', text)
        text = re.sub(r'[.,:;_%©?*,!@#$%^&()\d]|[+=]|[|]|/|"|\s{2,}|-</p><p></p>', ' ', text)
        return ' '.join(text.split())
