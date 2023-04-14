from django.utils.translation import ugettext as _


BK_CUSTOM_REPORT = "bk_custom_report"
CONFIG_OTLP_FIELD = "otlp"


def render_otlp_report_config() -> str:
    """
    feature_key: bk_custom_report
    {
        "otlp": {
            云区域id
            "0": ["grpc: http://xxxx.xxx.xxx:4317"]
        }
    }
    :return:
    """
    from apps.feature_toggle.handlers.toggle import FeatureToggleObject

    bk_custom_report = FeatureToggleObject.toggle(BK_CUSTOM_REPORT)
    if not bk_custom_report:
        return ""
    config = bk_custom_report.feature_config
    service_list = [
        str(_("    云区域ID {cloud_id} {service}").format(cloud_id=cloud_id, service=service))
        for cloud_id, services in config.get(CONFIG_OTLP_FIELD, {}).items()
        for service in services
    ]
    return "\n".join(service_list)
