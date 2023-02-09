【日志平台】{{ title }}  
**通知内容**：近<font color="info">{{ time_config.interval }}</font>新增 pattern 统计  
**业务名称**：{{ bk_biz_name }}  
**索引集名称**：{{ index_set_name }}  
**日志分析**：新增 pattern <font color="info">({{ all_patterns.new_patterns.pattern_count }})</font>个，日志总共出现 <font color="info">({{ all_patterns.new_patterns.log_count }})</font> 条, 最多的 pattern 日志数量为 <font color="info">({{ all_patterns.new_patterns.max_num }})</font> 条<font color="info">({{ all_patterns.new_patterns.percentage }}%)</font>   
**新增{{ log_col_show_type }}示例**:  
{% for pattern in all_patterns.new_patterns.data %}
><font color="warning">[{{loop.index}}]</font> <font color="warning">(数量:{{pattern.count}})</font> {{ pattern.pattern }}
{% endfor %}
[日志详情]({{ log_search_url }})