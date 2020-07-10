import threading
import time
import json
import boto3
from .queue_types import QueueName

S3_RAW_DATA_BUCKET = "nc-reviewier-raw-data"
S3_RESULTS_BUCKET = "nc-review-results"

class QueueThread(threading.Thread):
    def __init__(self, aws_session, queue):
        super(QueueThread, self).__init__()
        self.sqs = aws_session.client('sqs', region_name="us-west-1") 
        #self.queueUrl = self.sqs.get_queue_url(QueueName=queue.value)
        self.queueUrl = "https://sqs.us-west-1.amazonaws.com/471943556279/nc-eye-tracking-data"
        self.s3 = aws_session.resource('s3')
        # TODO: This needs to be changed to the appropriate neuron classifier 
        if queue == QueueName.EYE_TRACKING: 
            self.processor = lambda x: x 
        elif queue == QueueName.EEG: 
            self.processor = lambda x: x 

    def run(self):
        print("Started consuming from queue", self.queueUrl)
        while (True):
            messages = self.sqs.receive_message(QueueUrl=self.queueUrl, MaxNumberOfMessages=10, VisibilityTimeout=60, WaitTimeSeconds=20)['Messages']
            if len(messages) > 0:
                print("Retrieved message from queue:", messages)
                for message in messages:
                    self.handler(message)
            else:
                # sleep for some time if there are no messages on the queue (this will prevent the number of requests from blowing up too much)
                print("No messages on the queue, going to sleep...")
                time.sleep(60)

    def handler(self, messages):
        # get data from S3
        key = message['MessageAttributes']['Key']
        data = self.get_data_from_key(key)
        # process data in neuron
        results = self.processor(data)
        # write results to S3
        self.publish_results_to_s3(key, results)
        self.sqs.delete_message(self.queueUrl, messages['ReceiptHandle'])

    def get_data_from_key(self, key):
        return self.s3.get_object(bucket=S3_RAW_DATA_BUCKET, key=key)

    def publish_results_to_s3(self, old_key, results):
        key = self._get_results_key_from_data_key(old_key)
        self.s3.put_object(body=json.dumps(results), bucket=self.bucket, key=key)
        return

    def _get_results_key_from_data_key(self, data_key):
        reviewerId = data_key.split("/")[0]
        videoId = data_key.split("/")[1]
        filename = data_key.split("/")[2]
        return "{}/{}/{}".format(videoId, reviewerId, filename)
