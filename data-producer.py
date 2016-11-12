# - get data and write to kafka
import argparse
import atexit
import logging
import json
import time
from kafka import KafkaProducer
from kafka.errors import (KafkaTimeoutError, KafkaError)
from googlefinance import getQuotes
from apscheduler.schedulers.background import BackgroundScheduler
from flask import (Flask, jsonify)

logger_format = '%(asctime)-15s %(message)s'
logging.basicConfig(format=logger_format)
logger = logging.getLogger('data-producer')
# - DEBUG INFO WARNING ERROR
logger.setLevel(logging.DEBUG)

schedule = BackgroundScheduler()
schedule.add_executor('threadpool')
schedule.start()

app = Flask(__name__)
kafka_broker = '127.0.0.1:9092'
kafka_topic = 'stock-analyzer'

producer = ''

symbols = set()


def shutdown_hook():
    # - close kafka producer
    # - scheduler
    logger.info('shutdown kafka producer')
    producer.flush(10)
    producer.close()
    logger.info('shutdown scheduler')
    schedule.shutdown()


def fetch_price(symbol):
    try:
        logger.debug('Start to fetch stock price %s', symbol)
        stock_price = json.dumps(getQuotes(symbol))
        producer.send(topic=kafka_topic, value=stock_price, timestamp_ms=time.time())
        logger.debug('Finish write to kafka')
    except KafkaTimeoutError as timeout_error:
        logger.warn('Failed to send stock price for %s, cauesd by %s', symbol, timeout_error.message)
    except Exception as e:
        logger.error('Failed to send stock info, because %s', e.message)


@app.route('/', methods=['GET'])
def default():
    return jsonify('ok'), 200


@app.route('/<symbol>', methods=['POST'])
def add_stock(symbol):
    if not symbol:
        return jsonify({
                'error': 'Stock symbol cannot be empty'
            }), 400
    if symbol in symbols:
        pass
    else:
        symbols.add(symbol)
        schedule.add_job(fetch_price, 'interval', [symbol], seconds=2, id=symbol)
    return jsonify(list(symbols)), 200


@app.route('/<symbol>', methods=['DELETE'])
def del_route(symbol):
    if not symbol:
        return jsonify({
                'error': 'Stock symbol cannot be empty'
            }), 400
    if symbol not in symbols:
        pass
    else:
        symbols.remove(symbol)
        schedule.remove_job(symbol)
    return jsonify(list(symbols)), 200

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('kafka_broker', help="the address of kafka broker, with port number")
    parser.add_argument('topic_name', help="the certain topic name of kafka")
    parser.add_argument('flask_port', type=int, help="the port assigned for flask")
    args = parser.parse_args()
    kafka_topic = args.topic_name
    kafka_broker = args.kafka_broker
    producer = KafkaProducer(bootstrap_servers=kafka_broker)
    atexit.register(shutdown_hook)
    app.run(host='0.0.0.0', port=args.flask_port, debug=True)
