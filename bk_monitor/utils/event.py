import arrow
from django.conf import settings


class BkMonitorEvent:
    def __init__(self, data_name: str, event_name: str, reporter):
        self._reporter = reporter
        self._data_name = data_name
        self._event_name = event_name
        self._dimensions = {}
        self._content = ""
        self._target = getattr(settings, "APP_CODE", "")
        self._timestamp = arrow.now().timestamp * 1000

    def set_dimension(self, key, value) -> "BkMonitorEvent":
        self._dimensions[key] = value
        return self

    def set_dimensions(self, dimensions: dict) -> "BkMonitorEvent":
        if dimensions:
            self._dimensions = dimensions
        return self

    def set_content(self, content: str) -> "BkMonitorEvent":
        self._content = content

    def delay(self):
        # Not yet
        pass

    def build_bkmonitor_event(self) -> dict:
        return {
            "event_name": self._event_name,
            "event": {"content": self._content},
            "target": self._target,
            "dimension": self._dimensions,
            "timestamp": self._timestamp,
        }

    def __call__(self):
        self._reporter.trigger_event(self._data_name, self.build_bkmonitor_event())


class EventTrigger:
    def __init__(self, data_name: str, event_name: str, reporter):
        self._data_name = data_name
        self._event_name = event_name
        self._reporter = reporter

    def trigger(self) -> "BkMonitorEvent":
        return BkMonitorEvent(data_name=self._data_name, event_name=self._event_name, reporter=self._reporter)

    def __call__(self, content: str, dimensions: dict = None, delay: bool = False):
        event = self.trigger()
        event.set_content(content)
        event.set_dimensions(dimensions)
        event()
