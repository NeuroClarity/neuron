from boto3.session import Session

ANALYTICS_BUCKET = ""
RAW_DATA_BUCKET = ""
VIDEO_CONTENT_BUCKET = ""

class S3():
    def __init__(self, region):
        self.session = Session(region_name=region)
        self.client = self.session.client('s3')

    def upload_heatmap(self, key, data):
        return self.client.put_object(Bucket=ANALYTICS_BUCKET, Key=key, Body=data)

    def get_orignal_video(self, key):
        return self.client.get_object(Bucket=VIDEO_CONTENT_BUCKET, Key=key)

    def get_eye_tracking_data(self, key):
        return self.client.get_object(Bucket=RAW_DATA_BUCKET, Key=key)
