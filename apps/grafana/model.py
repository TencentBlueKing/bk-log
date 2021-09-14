from django.db import models
from django.utils.translation import ugettext_lazy as _


class TraceDatasourceMap(models.Model):
    bk_biz_id = models.IntegerField("业务id")
    index_set_id = models.IntegerField(_("trace索引集id"))
    datasource_id = models.IntegerField(_("数据源id"), unique=True)
