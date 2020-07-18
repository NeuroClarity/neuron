import threading
import time
import boto3
from neuron.messaging import QueueThread
from neuron.messaging import QueueName

session = boto3.session.Session(region_name="us-west-1")

def start_thread(queue):
    thread = QueueThread(session, queue)
    thread.start()
    return thread

if __name__ == '__main__':
    threads = []
    # start eye tracking consumer
    threads.append(start_thread(QueueName.EYE_TRACKING))
    # start eeg consumer
    threads.append(start_thread(QueueName.EEG))

    # consume forever
    while True:
        for thread in threads:
            if not thread.is_alive():
                print("Thread Crashed! Restarting thread", thread)
                thread.start()
        # sleep for 60 seconds before retrying
        time.sleep(60)

    
