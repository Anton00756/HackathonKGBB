import enum

from yandex_cloud_ml_sdk import YCloudML


class ReviewType(str, enum.Enum):
    FINANCIAL_CLAIM = 'Финансовая претензия'
    FINANCIAL_OFFER = 'Финансовое предложение'
    GRATITUDE = 'Благодарность'
    NON_FINANCIAL_CLAIM = 'Нефинансовая претензия'
    NON_FINANCIAL_OFFER = 'Нефинансовое предложение'


class ReviewReason(str, enum.Enum):
    WORKER_ERROR = 'Ошибка сотрудника'
    CLIENT_DISAGREEMENT = 'Несогласие клиента с тарифами, условиями обслуживания'
    BUG = 'Технический сбой'
    SPEED = 'Скорость обслуживания'


class Classifier:
    def __init__(self, folder_id, auth):
        self.__sdk = YCloudML(folder_id=folder_id, auth=auth)
        self.__type_classifier = self.__sdk.models.text_classifiers("yandexgpt").configure(
            task_description="Определи тип отзыва",
            labels=list(ReviewType)
        )
        self.__reason_classifier = self.__sdk.models.text_classifiers("yandexgpt").configure(
            task_description="Определи причину отзыва",
            labels=list(ReviewReason)
        )

    def get_review_type(self, text: str) -> ReviewType:
        return ReviewType(max(self.__type_classifier.run(text), key=lambda item: item.confidence).label)

    def get_reason(self, text: str) -> ReviewReason:
        return ReviewReason(max(self.__reason_classifier.run(text), key=lambda item: item.confidence).label)
