import threading
import time
from messaging.rabbit_thread import RabbitThread
from messaging.rabbit_config import RabbitQueue

RABBIT_HOST = ""
RABBIT_PORT = 5672
# these will be configured via environment variables at a later time
RABBIT_USERNAME = ""
RABBIT_PASSWORD = ""

def start_thread(queue):
    thread = RabbitThread(RABBIT_USERNAME, RABBIT_PASSWORD, RABBIT_HOST, RABBIT_PORT, queue)
    thread.start()
    return thread

if __name__ == '__main__':
    threads = []
    # start eye tracking consumer
    threads.append(start_thread(RabbitQueue.EYE_TRACKING))
    # start eeg consumer
    threads.append(start_thread(RabbitQueue.EEG))

    # consume forever
    while True:
        for thread in threads:
            if not thread.is_alive():
                print("Thread Crashed! Restarting thread", thread)
                thread.start()
        # sleep for 60 seconds before retrying
        time.sleep(60)

    
