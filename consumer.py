from kafka import KafkaConsumer
from json import loads

consumer = KafkaConsumer(
    'electric',
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id='my-group',
     value_deserializer=lambda x: loads(x.decode('utf-8')))

message_buffer = []
buffer_size = 1000
batch = 0
counter = 0

for message in consumer:
    if counter >= buffer_size:
        output.close()
        counter = 0
        batch+=1
    if counter == 0:
        output = open('consumer/output'+str(batch)+'.csv','a+')
        # output.write(',net_manager,purchase_area,street,zipcode_from,zipcode_to,city,num_connections,delivery_perc,perc_of_active_connections,type_conn_perc,type_of_connection,annual_consume,annual_consume_lowtarif_perc,smartmeter_perc')
    output.write(str(message.value))
    counter +=1
    