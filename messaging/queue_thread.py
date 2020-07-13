import sys
print(__file__)
sys.path.insert(0, '/Users/alfredoanderejr/Desktop/Brain/neuron')
print(sys.path)
import threading
import time
import json
#import boto3
from queue_types import QueueName
from eeg_ml_models.final_classifier import Final_classifier
import numpy as np



S3_RAW_DATA_BUCKET = "nc-reviewer-raw-data"
S3_RESULTS_BUCKET = "nc-review-results"

class QueueThread(threading.Thread):

    def __init__(self, aws_session, queue):
        super(QueueThread, self).__init__()
        self.sqs = aws_session.client('sqs')
        self.queueUrl = self.sqs.get_queue_url(QueueName=queue.value)['QueueUrl']
        self.s3 = aws_session.client('s3')
        # TODO: This needs to be changed to the appropriate neuron classifier
        if queue == QueueName.EYE_TRACKING:
            self.processor = lambda x: x
        elif queue == QueueName.EEG:
            classifier = Final_classifier()
            self.processor = classifier.predict

    def run(self):
        print("Started consuming from queue", self.queueUrl)
        while (True):
            try:
                messages = self.sqs.receive_message(QueueUrl=self.queueUrl, MessageAttributeNames=['Key'], MaxNumberOfMessages=10, VisibilityTimeout=60, WaitTimeSeconds=20)['Messages']
                if len(messages) > 0:
                    print("Retrieved messages from queue:", messages)
                    for message in messages:
                        self.handler(message)
                else:
                    # sleep for some time if there are no messages on the queue (this will prevent the number of requests from blowing up too much)
                    print("No messages on the queue, going to sleep...")
                    time.sleep(60)
            except Exception as e:
                print("ERROR: Uncaught exception while processing queue: {}".format(e))


    def handler(self, message):
        # get data from S3
        key = message['MessageAttributes']['Key']['StringValue']
        data = self.get_data_from_key(key)
        if not data:
            return

        # process data in neuron
        results = self.processor(data)
        # write results to S3
        self.publish_results_to_s3(key, results)
        self.sqs.delete_message(self.queueUrl, messages['ReceiptHandle'])

    def get_data_from_key(self, key):
        try:
            return self.s3.get_object(Bucket=S3_RAW_DATA_BUCKET, Key=key)
        except botocore.errorfactory.NoSuchKey:
            print("ERROR: Cannot find key {}".format(key))
        return None


    def publish_results_to_s3(self, old_key, results):
        key = self._get_results_key_from_data_key(old_key)
        self.s3.put_object(Body=json.dumps(results), Bucket=self.bucket, Key=key)
        return

    def _get_results_key_from_data_key(self, data_key):
        reviewerId = data_key.split("/")[0]
        videoId = data_key.split("/")[1]
        filename = data_key.split("/")[2]
        return "{}/{}/{}".format(videoId, reviewerId, filename)
