from base_source import BaseSource


class TxtSource(BaseSource):
    def __init__(self, work_path: str = '.'):
        super().__init__(work_path)
        self.data_path = work_path

    def get_new_reviews(self) -> list[str]:
        with open(self.data_path, 'r', encoding='utf-8') as file:
            return list(map(self.clean_text, file.readlines()))

    def update_last_review(self):
        pass
