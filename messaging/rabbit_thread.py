import threading
import pika
from .rabbit_config import RabbitQueue

class RabbitThread(threading.Thread):
    def __init__(self, username, password, endpoint, port, queue):
        super(RabbitThread, self).__init__()
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host=endpoint, 
                    port=port, 
                    virtual_host="/",
                    credentials=pika.PlainCredentials(username, password)))
        self.channel = connection.channel()
        # checks if queue exists, but does not create
        self.queue = queue
        self.channel.queue_declare(self.queue.value, passive=True)

    def run(self):
        channel.basic_consume(self.handler, queue=self.queue.value)
        channel.start_consuming()
        print("Started consuming from queue", self.queue.value)

    def handler(self):
        if self.queue == RabbitQueue.EYE_TRACKING:
            # call neuron's appropriate classification functions
            pass
        elif self.queue == RabbitQueue.EEG:
            # call neuon's appropriate classification functions
            pass
        return

