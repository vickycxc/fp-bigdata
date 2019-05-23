from time import sleep
from json import dumps
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))

dataset = 'producer/dataset.csv'

with open(dataset) as f:
    content = f.readlines()
    for x in content:
        producer.send('electric', value=x)
        print x
        sleep(0.001)
