# check_collector检查采集项是否正常采集

按照 **bkunifylogbeat -> gseAgent -> gseDS -> kafka -> transfer -> ES -> SAAS** 的顺序进行检查


## 各个检查项
### bkunifylogbeat
1. 编写检查配置项内容脚本
2. 调用JobAPI, 执行快速脚本, 获取脚本执行结果
3. 根据结果通过正则或者JSON序列化之后判断结果是否正常

### gseAgent
1. 同bkunifylogbeat的检查步骤
2. agent存活, 多agent
3. 采集器和agent的socket文件 ipc.state.report 脚本传, 在不在
4. agent 有没有托管 procinfo.json
5. ss 网络是否堵塞 -x -p | grep ipc.state.report

### gseDS
1. 根据zk地址获取相关信息, 判断zk服务是否正常
2. 根据data_id检查路由是否正确，配置是否正确

### Kafka
1. 调用KafkaConsumer, 看对应的topic里是否有对应的数据(可以建一个测试消费者)
2. topic partition 数量参考

### Transfer
1. 需要监控的同学提供相关Transfer相关接口, 根据接口返回判断
2. 对应指标采集回来 transfer指标

### ES检测
1. 调用ESClient, 获取其采集项对应的index以及alias别名是否正常
2. 后台任务维护 index和别名的关系, 当前的别名是否对应了物理索引, 对应错了就会写入/读写失败
3. index里，确认是否禁用_write开头的逻辑, 风险项
