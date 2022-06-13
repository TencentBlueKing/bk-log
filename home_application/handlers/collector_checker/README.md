# check_collector检查采集项是否正常采集

按照 **bkunifylogbeat -> gseAgent -> gseDS -> kafka -> transfer -> ES -> SAAS** 的顺序进行检查

## 代码逻辑
- home_application/handlers/check_collector.py handler函数, 命令行/接口入口
- home_application/handlers/collector_checker/base.py 请求, 结果, 建议基类
- home_application/handlers/collector_checker/*.py 各个检查步骤, 检查和返回均集成基类


## 各个检查项
### bkunifylogbeat
1. 编写检查配置项内容脚本
2. 调用JobAPI, 执行快速脚本, 获取脚本执行结果
3. 根据结果通过正则或者JSON序列化之后判断结果是否正常

### gseAgent
同bkunifylogbeat的检查步骤

### gseDS
1. 根据zk地址获取相关信息, 判断zk服务是否正常(路由是否正确，配置是否正确)

### Kafka
1. 调用KafkaConsumer, 看对应的topic里是否有对应的数据(可以建一个测试消费者)

### Transfer
1. 需要监控的同学提供相关Transfer相关接口, 根据接口返回判断

### ES检测
1. 调用ESClient, 获取其采集项对应的index以及alias别名是否正常
