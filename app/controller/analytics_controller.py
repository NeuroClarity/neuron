from app.infra.analytics.facial_encoding.classifier import EmotionModel
from app.infra.analytics.eye_tracking.video_heatmap import Heatmap
from app.infra.analytics.engagement.classifier import EngagementModel

from concurrent.futures import ThreadPoolExecutor
import logging
import json

NUM_THREADS = 1

class AnalyticsController():
    def __init__(self, s3, output_dir):
        # configure instantiate models
        self.heatmap_model = Heatmap(output_dir)
        self.emotion_model = EmotionModel()
        self.engagement_model = EngagementModel()
        self.output_dir = output_dir

        self.s3 = s3

        # Job Pool -- only increase the number of threads if we have more compute to handle requests
        self.thread_executor = ThreadPoolExecutor(NUM_THREADS)

    def submit_analytics_job(self, content, eye_data, face_data, heatmap_key, emotion_key, engagement_key):
        self.generate_heatmap(content, eye_data, heatmap_key)

        facial_file_path = "{0}/user-video.webm".format(self.output_dir)
        self.s3.download_user_facial_video(face_data, facial_file_path)
        self.classify_emotion(facial_file_path, emotion_key)
        self.classify_engagement(facial_file_path, engagement_key)
        return

    """
    Gets data from s3 and starts generating the eye tracking heatmap in the background
    """
    def generate_heatmap(self, video_key, eye_gaze_data, destination_key):
        video_file_path = "./{0}/original-video.mp4".format(self.output_dir)
        self.s3.download_user_content(video_key, video_file_path)

        self.thread_executor.submit(self._heatmap_task, video_file_path, eye_gaze_data, destination_key)
        return

    def _heatmap_task(self, video_file_path, eye_gaze_data, destination_key):
        try:
            video_save_path = self.heatmap_model.generate_heatmap(video_file_path, eye_gaze_data)
            with open(video_save_path, 'rb') as f:
                self.s3.upload_heatmap(destination_key, f)
            logging.info("Finished generating heatmap")
        except Exception as e:
            logging.error("Failed to generate heatmap:" + str(e))
        return

    """
    Gets data from s3 and runs the classification algorithm in the background
    """
    def classify_emotion(self, video_file_path, destination_key):
        self.thread_executor.submit(self._emotion_task, video_file_path, destination_key)
        return

    def _emotion_task(self, video_file_path, destination_key):
        try:
            score, _ = self.emotion_model.classify_video(video_file_path)
            emotion_response = {'embedding': [i.tolist() for i in score]}
            self.s3.upload_emotion(destination_key, json.dumps(emotion_response))
            logging.info("Finished emotion classification")
        except Exception as e:
            logging.error("Failed to complete emotion classification task" + str(e))
        return

    """
    Gets data from s3 and starts engagement classification algorithm in the background
    """
    def classify_engagement(self, video_file_path, destination_key):
        self.thread_executor.submit(self._engagement_task, video_file_path, destination_key)
        return

    def _engagement_task(self, video_file_path, destination_key):
        try:
            engagement = self.engagement_model.classify_video(video_file_path)
            self.s3.upload_engagement(destination_key, json.dumps(engagement))
            logging.info("Finished engagement classification")
        except Exception as e:
            logging.error("Engagement generator failed due to the following error: " + str(e))
        return

