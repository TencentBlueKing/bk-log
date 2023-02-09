【Log Platform】{{ title }}  
**Notice content**：<font color="info">{{ time_config.interval }}</font> new pattern statistics  
**Biz Name**：{{ bk_biz_name }}  
**Index Set Name**：{{ index_set_name }}  
**Log analysis**：New pattern <font color="info">({{ all_patterns.new_patterns.pattern_count }})</font>，Number <font color="info">({{ all_patterns.new_patterns.log_count }})</font>, The max count of pattern logs: <font color="info">({{ all_patterns.new_patterns.max_num }})</font> <font color="info">({{ all_patterns.new_patterns.percentage }}%)</font>   
**New {{ log_col_show_type }} Example**:  
{% for pattern in all_patterns.new_patterns.data %}
><font color="warning">[{{loop.index}}]</font> {{ pattern.pattern }} <font color="warning">(Count：{{pattern.count}})</font>
{% endfor %}
[Log Detail]({{ log_search_url }})  
