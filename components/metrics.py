import json
import os

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS


class InfluxMetrics:
    def __init__(self, url: str, token: str, org: str, bucket: str):
        self.client = influxdb_client.InfluxDBClient(
            url=url,
            token=token,
            org=org
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.bucket = bucket
        self.org = org
        self.save_path = os.environ.get('METRICS_SAVE_PATH', 'metrics.json')
        if os.path.exists(self.save_path):
            with open(self.save_path, 'r', encoding='utf-8') as file:
                self.data = json.load(file)
        else:
            self.data = {'sum_index': 0, 'total_count': 0}

    def add_record(self, record):
        self.write_api.write(bucket=self.bucket, org=self.org, record=record)

    def calculate_index(self, claim_count: int, offer_count: int, gratitude_count: int):
        self.data['sum_index'] += claim_count + offer_count * 4 + gratitude_count * 10
        self.data['total_count'] += claim_count + offer_count * 0.5 + gratitude_count
        if self.data['total_count']:
            self.add_record(influxdb_client.Point("index").field("mark", self.data['sum_index'] /
                                                                 self.data['total_count']))
        with open(self.save_path, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)

    def update_metrics(self, claim_count: int, offer_count: int, gratitude_count: int, financial_claim_count: int,
                       financial_offer_count: int, worker_error_count: int, disagreement_count: int, bug_count: int,
                       speed_count: int, source_metrics: dict):
        self.add_record(influxdb_client.Point("count_diffs").tag("type", "claim_count").field("count", claim_count))
        self.add_record(influxdb_client.Point("count_diffs").tag("type", "offer_count").field("count", offer_count))
        self.add_record(influxdb_client.Point("count_diffs").tag("type", "gratitude_count")
                        .field("count", gratitude_count))
        self.add_record(influxdb_client.Point("count_diffs").tag("type", "total_count")
                        .field("count", claim_count + offer_count + gratitude_count))
        self.add_record(influxdb_client.Point("financial_count_diffs").tag("type", "claim_count")
                        .field("count", financial_claim_count))
        self.add_record(influxdb_client.Point("financial_count_diffs").tag("type", "offer_count")
                        .field("count", financial_offer_count))
        self.add_record(influxdb_client.Point("financial_count_diffs").tag("type", "non_claim_count")
                        .field("count", claim_count - financial_claim_count))
        self.add_record(influxdb_client.Point("financial_count_diffs").tag("type", "non_offer_count")
                        .field("count", offer_count - financial_offer_count))
        self.add_record(influxdb_client.Point("reason_count_diffs").tag("type", "worker_error")
                        .field("count", worker_error_count))
        self.add_record(influxdb_client.Point("reason_count_diffs").tag("type", "disagreement")
                        .field("count", disagreement_count))
        self.add_record(influxdb_client.Point("reason_count_diffs").tag("type", "bug").field("count", bug_count))
        self.add_record(influxdb_client.Point("reason_count_diffs").tag("type", "speed").field("count", speed_count))
        self.calculate_index(claim_count, offer_count, gratitude_count)
        for name, count in source_metrics.items():
            self.add_record(influxdb_client.Point("source_count_diffs").tag("source", name).field("count", count))
