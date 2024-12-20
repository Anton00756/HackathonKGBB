import random

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

bucket = "metrics"
org = "KGBB"
token = "influx_admin"
url = "http://localhost:8086"


class InfluxClient:
    def __init__(self):
        self.client = influxdb_client.InfluxDBClient(
            url=url,
            token=token,
            org=org
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def add_record(self, record):
        self.write_api.write(bucket=bucket, org=org, record=record)


if __name__ == '__main__':
    claim_count = random.randint(0, 5)  # Претензия
    offer_count = random.randint(0, 5)  # Предложение
    gratitude_count = random.randint(0, 5)  # Благодарность
    financial_claim_count = random.randint(0, claim_count)
    financial_offer_count = random.randint(0, offer_count)
    claim_and_offer_count = claim_count + offer_count
    worker_error_count = random.randint(0, claim_and_offer_count)
    disagreement_count = random.randint(0, claim_and_offer_count)
    bug_count = random.randint(0, claim_and_offer_count)
    speed_count = random.randint(0, claim_and_offer_count)
    index_strategy = random.randint(0, 10)
    if index_strategy < 1:
        index = 1
    elif index_strategy < 3:
        index = 10
    else:
        index = random.randint(1, 10)

    client = InfluxClient()
    client.add_record(influxdb_client.Point("count_diffs").tag("type", "claim_count").field("count", claim_count))
    client.add_record(influxdb_client.Point("count_diffs").tag("type", "offer_count").field("count", offer_count))
    client.add_record(influxdb_client.Point("count_diffs").tag("type", "gratitude_count")
                      .field("count", gratitude_count))
    client.add_record(influxdb_client.Point("count_diffs").tag("type", "total_count")
                      .field("count", claim_count + offer_count + gratitude_count))
    client.add_record(influxdb_client.Point("financial_count_diffs").tag("type", "claim_count")
                      .field("count", financial_claim_count))
    client.add_record(influxdb_client.Point("financial_count_diffs").tag("type", "offer_count")
                      .field("count", financial_offer_count))
    client.add_record(influxdb_client.Point("financial_count_diffs").tag("type", "non_claim_count")
                      .field("count", claim_count - financial_claim_count))
    client.add_record(influxdb_client.Point("financial_count_diffs").tag("type", "non_offer_count")
                      .field("count", offer_count - financial_offer_count))
    client.add_record(influxdb_client.Point("reason_count_diffs").tag("type", "worker_error")
                      .field("count", claim_count))
    client.add_record(influxdb_client.Point("reason_count_diffs").tag("type", "disagreement")
                      .field("count", offer_count))
    client.add_record(influxdb_client.Point("reason_count_diffs").tag("type", "bug").field("count", gratitude_count))
    client.add_record(influxdb_client.Point("reason_count_diffs").tag("type", "speed").field("count", index))
    client.add_record(influxdb_client.Point("index").field("mark", index))
