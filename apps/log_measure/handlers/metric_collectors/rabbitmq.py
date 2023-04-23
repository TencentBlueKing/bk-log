# -*- coding: utf-8 -*-
from apps.log_measure.utils.metric import MetricUtils
from bk_monitor.constants import TimeFilterEnum
from bk_monitor.utils.metric import register_metric, Metric
from home_application.constants import QUEUES
from home_application.utils.rabbitmq import RabbitMQClient


class RabbitMQMetricCollector:
    @staticmethod
    @register_metric("rabbitmq", description="RabbitMQ", data_name="metric", time_filter=TimeFilterEnum.MINUTE5)
    def rabbitmq():
        metrics = []
        client = RabbitMQClient.get_instance()
        ping = client.ping()

        metrics.append(
            Metric(
                metric_name="up",
                metric_value=1 if ping["status"] else 0,
                timestamp=MetricUtils.get_instance().report_ts,
            )
        )

        if not ping["status"]:
            # 如果连 rabbitmq 都连不通就不用走下面的流程
            return metrics

        for queue_name in QUEUES:
            queue_metrics = client.get_queue_metrics(queue_name)
            for key, value in queue_metrics.items():
                metrics.append(
                    Metric(
                        metric_name=key,
                        metric_value=value,
                        dimensions={"queue_name": queue_name},
                        timestamp=MetricUtils.get_instance().report_ts,
                    )
                )
        return metrics
