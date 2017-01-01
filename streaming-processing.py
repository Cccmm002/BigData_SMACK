import atexit
import argparse
import logging
import json
import time
from kafka import KafkaProducer
from kafka.errors import KafkaError, KafkaTimeoutError
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

logging.basicConfig(format='%(asctime)-15s %(message)s')
logger = logging.getLogger('stream-processing')
logger.setLevel(logging.DEBUG)

kafka_producer = None
topic = None
kafka_broker = None
target_topic = None


def shutdown_hook(producer):
    try:
        logger.info('Flushing pending messages to kafka, timeout is set to 10s')
        producer.flush(10)
        logger.info('Finish flushing pending messages to kafka')
    except KafkaError as kafka_error:
        logger.warning('Failed to flush pending messages to kafka, caused by: {0}'.format(kafka_error))
    finally:
        try:
            logger.info('Closing kafka connection')
            producer.close(10)
        except Exception as e:
            logger.warning('Failed to close kafka connection, caused by: {0}'.format(e))


def process_stream(stream):

    def send_to_kafka(rdd):
        results = rdd.collect()
        for r in results:
            data = json.dumps(
                {
                    'symbol': r[0],
                    'timestamp': time.time(),
                    'average': r[1]
                }
            )
            try:
                logger.info('Sending average price {0} to kafka'.format(data))
                kafka_producer.send(target_topic, value=data.encode('utf-8'))
            except KafkaError as error:
                logger.warning('Failed to send average stock price to kafka, caused by: {0}'.format(error))
            except Exception as e:
                logger.warning('Error: {0}'.format(e))

    def pair(data):
        record = json.loads(data[1])[0]
        result = (record.get('StockSymbol'), (float(record.get('LastTradePrice')), 1))
        return result

    stream.map(pair).reduceByKey(lambda a, b: (a[0] + b[0], a[1] + b[1])).map(
        lambda d: (d[0], d[1][0] / d[1][1])).foreachRDD(send_to_kafka)


if __name__ == '__main__':
    # - setup commanline
    parser = argparse.ArgumentParser()
    parser.add_argument('topic', help='original topic name')
    parser.add_argument('target_topic', help='target topic to send data to')
    parser.add_argument('kafka_broker', help='location of kafka')

    args = parser.parse_args()
    kafka_broker = args.kafka_broker
    topic = args.topic
    target_topic = args.target_topic

    kafka_producer = KafkaProducer(bootstrap_servers=kafka_broker)

    # Create a local StreamingContext with two working threads and batch interval of 5 second
    sc = SparkContext("local[2]", "StockAveragePrice")
    sc.setLogLevel('ERROR')
    ssc = StreamingContext(sc, 5)

    kafkaStream = KafkaUtils.createDirectStream(ssc, [topic], {'metadata.broker.list': kafka_broker})
    # kafkaStream.foreachRDD(process)
    process_stream(kafkaStream)

    atexit.register(shutdown_hook, kafka_producer)

    ssc.start()
    ssc.awaitTermination()
