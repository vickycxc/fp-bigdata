from time import sleep
from json import dumps
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))

dataset = 'dataset/enexis_electricity_01012010.csv'

with open(dataset) as f:
    content = f.readlines()
    for x in content:
        producer.send('numtest', value=x)
        print x
        sleep(0.1)


# you may also want to remove whitespace characters like `\n` at the end of each line
# content = [x.strip() for x in content] 

# for e in range(1000):
