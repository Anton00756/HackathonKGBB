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
    os.environ['GRPC_VERBOSITY'] = 'ERROR'
    os.environ['GLOG_minloglevel'] = '2'
    # hide warning from Yandex GPT manager

    with open(os.environ['PATH_TO_SOURCES'], 'r', encoding='utf-8') as file:
        sources_list = json.load(file)
    sources: dict[str, BaseSource] = {}
    for index, source in enumerate(sources_list['sources']):
        if os.path.exists(source['path']):
            if source['path'] not in sys.path:
                sys.path.append(source['path'])
            try:
                module = importlib.import_module(source['module'])
                sources[source.get('source_name_in_metrics', f'source_{index}')] = \
                    getattr(module, source['class'])(source.get('work_path', '.'))
            except ModuleNotFoundError:
                LOGGER.error(f'Module "{source["module"]}" was not found in path "{source["path"]}"')
            except AttributeError:
                LOGGER.error(f'Class "{source["class"]}" was not found in module "{source["module"]}"')
    reviews = []
    source_metrics = {}
    for metrics_name, source in sources.items():
        try:
            reviews.extend(source_reviews := source.get_new_reviews())
            source_metrics[metrics_name] = len(source_reviews)
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
                LOGGER.error(f'Reviewed: {number}/{len(reviews)}')
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
                               worker_error_count, disagreement_count, bug_count, speed_count, index=0,
                               source_metrics=source_metrics)
    except Exception:
        LOGGER.error(f'Error in reviews classification:\n{traceback.format_exc()}')
        exit(-1)

    for source in sources.values():
        try:
            source.update_last_review()
        except Exception:
            LOGGER.error(f'Error in last review updating of source "{source.__class__.__name__}":\n'
                         f'{traceback.format_exc()}')
