import importlib
import json
import os
import sys
import traceback

from dotenv import load_dotenv

import utils
from components.classifier import Classifier, ReviewReason, ReviewType
from components.metrics import InfluxMetrics
from components.sources.base_source import BaseSource

load_dotenv('../.env')
LOGGER = utils.get_logger()

if __name__ == '__main__':
    with open(os.environ['PATH_TO_SOURCES'], 'r', encoding='utf-8') as file:
        sources_list = json.load(file)
    sources: list[BaseSource] = []
    for source in sources_list['sources']:
        if os.path.exists(source['path']):
            if source['path'] not in sys.path:
                sys.path.append(source['path'])
            try:
                module = importlib.import_module(source['module'])
                sources.append(getattr(module, source['class'])(source.get('work_path', '.')))
            except ModuleNotFoundError:
                LOGGER.error(f'Module "{source["module"]}" was not found in path "{source["path"]}"')
            except AttributeError:
                LOGGER.error(f'Class "{source["class"]}" was not found in module "{source["module"]}"')
    reviews = []
    for source in sources:
        try:
            reviews.extend(source.get_new_reviews())
        except Exception:
            LOGGER.error(f'Error in reviews loading of source "{source.__class__.__name__}":\n{traceback.format_exc()}')
    LOGGER.info(f'Reviews for classification: {len(reviews)}')
    claim_count = offer_count = gratitude_count = financial_claim_count = financial_offer_count = worker_error_count = \
        disagreement_count = bug_count = speed_count = 0
    try:
        classifier = Classifier(folder_id=os.environ['YANDEX_GPT_FOLDER_ID'], auth=os.environ['YANDEX_GPT_TOKEN'])
        for number, review in enumerate(reviews, 1):
            if (review_type := classifier.get_review_type(review)) == ReviewType.GRATITUDE:
                gratitude_count += 1
                continue
            if review_type == ReviewType.FINANCIAL_CLAIM:
                financial_claim_count += 1
                claim_count += 1
            elif review_type == ReviewType.FINANCIAL_OFFER:
                financial_offer_count += 1
                offer_count += 1
            elif review_type == ReviewType.NON_FINANCIAL_CLAIM:
                claim_count += 1
            else:
                offer_count += 1
            if (reason := classifier.get_reason(review)) == ReviewReason.WORKER_ERROR:
                worker_error_count += 1
            elif reason == ReviewReason.CLIENT_DISAGREEMENT:
                disagreement_count += 1
            elif reason == ReviewReason.BUG:
                bug_count += 1
            else:
                speed_count += 1
            LOGGER.error(f'Reviewed: {number}/{len(reviews)}')

        metrics = InfluxMetrics(os.environ['INFLUX_URL'], os.environ['INFLUX_TOKEN'], os.environ['INFLUX_ORG'],
                                os.environ['INFLUX_BUCKET'])
        # TODO: вычисление индекса
        metrics.update_metrics(claim_count, offer_count, gratitude_count, financial_claim_count, financial_offer_count,
                               worker_error_count, disagreement_count, bug_count, speed_count, index=0)
    except Exception:
        LOGGER.error(f'Error in reviews classification:\n{traceback.format_exc()}')
        exit(-1)

    for source in sources:
        try:
            source.update_last_review()
        except Exception:
            LOGGER.error(f'Error in last review updating of source "{source.__class__.__name__}":\n'
                         f'{traceback.format_exc()}')
