import os
from dataclasses import asdict

from fluent.asyncsender import FluentSender

from spanlib.infrastructure.kubernetes.env_var import (
    BEDROCK_ENDPOINT_ID,
    BEDROCK_FLUENTD_ADDR,
    BEDROCK_FLUENTD_PREFIX,
    POD_NAME,
)

from .type import LogExporter, PredictionContext


class FluentdExporter(LogExporter):
    def __init__(self, **kwargs):
        """Initializes an async fluentd sender using default Bedrock environment variables.

        Callers may override kwargs to pass additional configurations to the fluentd sender.
        """
        # Environment variables will be injected by model server chart
        pod_name = os.environ.get(POD_NAME, "unknown-pod")
        endpoint_id = os.environ.get(BEDROCK_ENDPOINT_ID, "unknown-endpoint")
        fluentd_prefix = os.environ.get(BEDROCK_FLUENTD_PREFIX, "models.predictions")

        fluentd_server = os.environ.get(
            BEDROCK_FLUENTD_ADDR, "fluentd-logging.core.svc.cluster.local"
        ).split(":")
        fluentd_port = int(fluentd_server[1]) if len(fluentd_server) > 1 else 24224

        self._sender: FluentSender = FluentSender(
            tag=f"{fluentd_prefix}.{endpoint_id}.{pod_name}",
            host=fluentd_server[0],
            port=fluentd_port,
            queue_circular=True,
            **kwargs,
        )

    def emit(self, prediction: PredictionContext):
        """
        Exports the full prediction context asynchronously to fluentd.

        :param prediction: The completed prediction
        :type prediction: PredictionContext
        """
        data = asdict(prediction)
        data["entity_id"] = str(prediction.entity_id)
        # fluentd's msgpack version does not yet support serializing datetime
        data["created_at"] = int(prediction.created_at.timestamp())
        # TODO: Supports bytes type which is not json serializable
        self._sender.emit_with_time(label=None, timestamp=data["created_at"], data=data)
