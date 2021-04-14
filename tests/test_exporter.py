from os import environ

from boxkite.monitoring.exporter.fluentd_exporter import BEDROCK_FLUENTD_ADDR
from boxkite.monitoring.service import ModelMonitoringService
from tests.mockserver import MockRecvServer


def test_fluent_sender():
    server = MockRecvServer(port=24224)
    environ[BEDROCK_FLUENTD_ADDR] = "localhost"
    service = ModelMonitoringService()

    pid = service.log_prediction(
        request_body="test", features=[2.0, 1.2, 0.8], output="dog"
    )
    service._log_exporter._sender.close()

    item = server.get_received()[0]
    assert item[1] == item[2]["created_at"]
    server.close()
