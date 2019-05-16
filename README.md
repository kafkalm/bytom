# `基于大数据技术的大额交易对市场价格的画像设计`
##`模块介绍`
>1.bytom_crawler - 爬虫模块，收集大额交易与市场价格信息  
    [bytom_crawler 文档](#bytom_crawler)  
>
2.db - 采用MongoDB作为后台数据库，封装了MongoDB操作的方法  
    [MongoDB.py 接口文档](#mongodbpy)  
>
3.mykafka - 使用kafka推送消息，为实时数据提供高吞吐低延迟的平台，封装了kafka的各个模块  
    [kafka_client.py 接口文档](#kafka_clientpy)  

>4.Spark - SparkStreaming，SparkML组件的封装，为实时数据提供数据清洗、处理；对数据进行机器学习  
    [Spark 接口文档](#spark)  

>5.config - 配置文件  
  [config 文档](#config)  
  settings.ini 为配置文件;  
  config.py 为读取配置文件的函数

>3.log - 日志输出模块  
    提示信息会在控制台输出，并会保存到LOGS文件夹中对应日期的.log文件中  
>
4.LOGS - 存储日志的文件夹  
##`主要依赖`  
>- scrapy  
>- pymongo  
>- kafka-python  
>- pyspark  
>- kafka 2.20 Scala 2.12  
>- Spark 2.4.1 Hadoop 2.7
### `bytom_crawler`
>###### 1.settings 配置文件设置
\# MONGODB 相关配置  
MONGODB_URL = <mongodb_url\>  
MONGODB_DB = <db_name\>  
MONGODB_BATCH_SIZE = <int\>  

>\# kafka 相关配置  
KAFKA_CONF = {
    'bootstrap_servers':[str],  
    'batch_size': <int\>  
}

>\# 抓取日期配置  
START_TIME = 'YYYY-mm-dd'  
END_TIME = 'YYYY-mm-dd'  

>\# 是否生成任务  
GEN_SEEDS_FLAG = True  

>\# 货币名称  
CURRENCY_NAME = 'btm'  
>###### 2.spiders  
  - coinmetrics.py # coinmetrics api爬取
  - blockmeta.py # blockmeta api爬取
  - gate.py # gate api 爬取  
>###### 3.pipelines.py  
 - class KafkaPipeline(object)  
    将爬取到的信息直接通过kafka推送的管道类
 - class MongoDBPipeline(object)  
    将爬取到的信息保存到mongodb的管道类
### `MongoDB.py`  
>###### 1.导入封装的MongoDB类
    from db.MongoDB import MongoDBClient  

>######2.实例化
    mongodb = MongoDBClient(settings)  
    '''
    settings = {
            'MONGODB_URL': str, #MONGODB的URL地址
            'MONGODB_DB': str,  #数据库名
            'MONGODB_BATCH_SIZE' : INT #读取数量
        }
    '''

>######3.插入操作
   - mongodb.insert_one(collection,body)   #单条插入  
    1. collection:集合名(str)  
    2. body:插入的内容(dict)  
    
> - mongodb.insert_many(collection,body)   #批量插入
    1. collection:集合名(str)  
    2. body:插入的内容([dict] 字典组成的列表)  

> - return: True / False

>######4.查询操作
   - mongodb.find(collection,query)  
    1. collection:集合名(str)  
    2. query:查询条件(dict)  

> - return: 查询的结果(list)

>######5.更新操作
   - mongodb.update_one(collection,query,body)   #单条更新  
    1. collection:集合名(str)  
    2. query:查询条件(dict)
    3. body:插入的内容(dict)  
    
> - mongodb.update_many(collection,query,body)   #批量更新
    1. collection:集合名(str)
    2. query:查询条件(dict)  
    3. body:插入的内容([dict] 字典组成的列表)  

> - return: True / False

>######6.删除操作
   - mongodb.delete_one(collection,query)   #单条删除  
    1. collection:集合名(str)  
    2. query:查询条件(dict)  
    
> - mongodb.delete_many(collection,query)   #批量删除
    1. collection:集合名(str)  
    2. query:查询条件(dict)  

> - return: True / False
  
### `kafka_client.py`  
>###### 1.导入封装的kafkaProducer类
    from mykafka.kafka_client import MyKafkaProducer  

>######2.实例化
    producer = MyKafkaProducer(settings)
    '''
    settings = {
            'client_id': str, #客户端id 没有指定会自动生成
            'bootstrap_servers': 'host[:port]' or list of 'host[:port]', #broker的IP地址
            'batch_size': int, #读取/推送数量
            'value_serializer': callable #序列化函数
        }
    '''  

>######3.发送消息
   - producer.sendMsg(topic,msg)  
    1. topic:指定的主题(str)  
    2. msg:发送的消息(byte)  
  
>######4.推送到Broker
   - producer.flushMsg()  
    #将缓存区内的消息都推送到Broker  
### `Spark`
>####`SparkStreaming`  
>###### 1.导入封装的sparkstreaming类
    from Spark.spark_streaming.spark_streaming import SparkStreaming  

>######2.实例化
    sparkstreaming = SparkStreaming(spark_settings,mongodb_settings)  
    '''
    spark_settings = {
            'spark_cores_max' : int , # 运行Spark核心最大数量
            'appName' : str , # 名称
            'batchDuration' : int , # Spark Streaming批次间隔
            'brokers' : str , # kafka brokers ip地址 "host:port,host:port,..."
            'topics' : list , # kafka topic [ topic(str) ]
        }
    mongodb_settings = {
          'MONGODB_URL': str, #MONGODB的URL地址
          'MONGODB_DB': str,  #数据库名
          'MONGODB_BATCH_SIZE' : INT #读取数量
        }
    '''
>####`SparkML`

### `config`  
>###### 1.settings.ini 配置文件字段说明  
>[db]  
>MONGODB_URL =  
>MONGODB_DB =  
>MONGODB_BATCH_SIZE =  

>[Log]  
>LOG_SAVE_PATH = #LOG日志文件保存路径  

>[kafka]  
>CLIENT_ID =  
>BOOTSTRAP_SERVERS =  
>BATCH_SIZE =  
>VALUE_SERIALIZER =  

>[Spark]  
>SPARK_CORES_MAX =  
>APPNAME =  
>BATCHDURATION =  
>BROKERS =  
>TOPICS =  
>###### 2.config.py 读取配置文件函数使用
>- get_config(section,opition)  
    1. section:指定的配置节(str)  
    2. opition:配置字段(str)  