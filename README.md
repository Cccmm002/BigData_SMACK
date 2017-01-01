# BigData_SMACK
An experimental big data project analyzing stock prices. Using Docker, Zookeeper, Kafka, Spark, Cassandra and other frameworks.

SMACK ports list:
* Kafka broker: 9092

Web Server ports list:
* Flask server: 5000
* Log.io log viewer: 28778

Spark run command line:
```bash
spark-submit --jars spark-streaming-kafka-0-8-assembly_2.11-2.1.0.jar streaming-processing.py stock-analyzer average-stock-price kafka-ip:9092
```
You need to firstly download spark streaming jar package for kafka. The instruction is on <http://spark.apache.org/docs/latest/streaming-kafka-0-8-integration.html>. 
