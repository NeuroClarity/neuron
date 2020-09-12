from boto3.session import Session

class S3():
    def __init__(self, region):
        self.session = Session(region_name=region)
        self.client = self.session.client('s3')

        self.ANALYTICS_BUCKET = "nc-review-results"
        self.RAW_DATA_BUCKET = "nc-reviewer-raw-data"
        self.VIDEO_CONTENT_BUCKET = "nc-client-video-content"

    def upload_heatmap(self, key, data):
        return self.client.put_object(Bucket=self.ANALYTICS_BUCKET, Key=key, Body=data)

    def upload_emotion(self, key, data):
        return self.client.put_object(Bucket=self.ANALYTICS_BUCKET, Key=key, Body=data)

    def upload_engagement(self, key, data):
        return self.client.put_object(Bucket=self.ANALYTICS_BUCKET, Key=key, Body=data)

    def upload_user_video_content(self, key, data):
        return self.client.put_object(Bucket=self.VIDEO_CONTENT_BUCKET, Key=key, Body=bytes(data), ContentType="video/mp4")

    def download_user_content(self, key, file_path):
        self.client.download_file(Bucket=self.VIDEO_CONTENT_BUCKET, Key=key, Filename=file_path)

    def download_user_facial_video(self, key, file_path):
        self.client.download_file(Bucket=self.RAW_DATA_BUCKET, Key=key, Filename=file_path)

    def delete_user_video(self, key):
        self.client.delete_object(Bucket=self.RAW_DATA_BUCKET, Key=key)

    def download_eye_tracking_data(self, key, file_path):
        return self.client.download_file(Bucket=self.RAW_DATA_BUCKET, Key=key, Filename=file_path)

