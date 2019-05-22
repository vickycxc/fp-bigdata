from kafka import KafkaConsumer
from json import loads

consumer = KafkaConsumer(
    'numtest',
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id='my-group',
     value_deserializer=lambda x: loads(x.decode('utf-8')))

message_buffer = []
buffer_size = 10
batch = 0
counter = 0

for message in consumer:
    if counter >= buffer_size:
        output.close()
        counter = 0
        batch+=1
    if counter == 0:
        output = open('consumer/output_'+str(batch)+'.csv','a+')
    output.write(str(message.value))
    counter +=1
    print(counter)