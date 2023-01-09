{% if langeuage = 'en' %}
【Log Platform】{{ title }}  
Notice content：近{{ time_config.interval }}新增 pattern 统计  
Biz Name：{{ bk_biz_name }}  
Index Set Name：{{ index_set_name }}  
Log analysis：New pattern ({{ all_patterns.new_patterns.pattern_count }})个，日志总共出现 ({{ all_patterns.new_patterns.log_count }}) 条, 最多的 pattern 日志数量为 {{ all_patterns.new_patterns.max_num }} 条({{ percentage }}%)   
New {{ log_col_show_type }} Example:  
{% for pattern in new_patterns %}
{{ pattern.pattern }}  
{% endfor %}
[Log Detail]({{ log_search_url }})  
{% else %}
【日志平台】{{ title }}  
通知内容：近{{ time_config.interval }}新增 pattern 统计  
业务名称：{{ bk_biz_name }}  
索引集名称：{{ index_set_name }}  
日志分析：新增 pattern ({{ all_patterns.new_patterns.pattern_count }})个，日志总共出现 ({{ all_patterns.new_patterns.log_count }}) 条, 最多的 pattern 日志数量为 {{ all_patterns.new_patterns.max_num }} 条({{ percentage }}%)   
新增{{ log_col_show_type }}示例:  
{% for pattern in new_patterns %}
{{ pattern.pattern }}  
{% endfor %}
[日志详情]({{ log_search_url }})  
{% endif %}