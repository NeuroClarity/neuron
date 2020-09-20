from app.infra.analytics.facial_encoding.classifier import EmotionModel
from app.infra.analytics.eye_tracking.video_heatmap import Heatmap
from app.infra.analytics.engagement.classifier import EngagementModel

from concurrent.futures import ThreadPoolExecutor
import logging
import json
import os

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

    def submit_analytics_job(self, study_id, content_video_key, eye_data, face_key, heatmap_key, emotion_key, engagement_key):
        # Gets data from s3 and starts generating the eye tracking heatmap in the background
        video_file_path = "{0}/original-video--{1}.mp4".format(self.output_dir, study_id)
        self.s3.download_user_content(content_video_key, video_file_path)
        self.thread_executor.submit(self._heatmap_task, study_id, video_file_path, eye_data, heatmap_key)

        # Gets data from s3 and submits a job to run the ML models on the facial video
        facial_file_path = "{0}/user-video--{1}.webm".format(self.output_dir, study_id)
        self.s3.download_user_facial_video(face_key, facial_file_path)
        self.thread_executor.submit(self._machine_learning_task, face_key, facial_file_path, emotion_key, engagement_key)
        return

    def _heatmap_task(self, study_id, video_file_path, eye_gaze_data, destination_key):
        try:
            video_save_path = self.heatmap_model.generate_heatmap(study_id, video_file_path, eye_gaze_data)
            with open(video_save_path, 'rb') as f:
                self.s3.upload_heatmap(destination_key, f)
            # remove the files after uploading to s3 to avoid clutter
            os.remove(video_save_path)
            os.remove(video_file_path)
            logging.info("Finished generating heatmap")
        except Exception as e:
            logging.error("Failed to generate heatmap:" + str(e))
        return

    def _machine_learning_task(self, face_video_key, video_file_path, emotion_key, engagement_key):
        success = True
        try:
            score, _ = self.emotion_model.classify_video(video_file_path)
            emotion_response = {'embedding': [i.tolist() for i in score]}
            self.s3.upload_emotion(emotion_key, json.dumps(emotion_response))
            logging.info("Finished emotion classification")
        except Exception as e:
            logging.error("Failed to complete emotion classification task" + str(e))
            success = False

        try:
            engagement = self.engagement_model.classify_video(video_file_path)
            self.s3.upload_engagement(engagement_key, json.dumps(engagement))
            logging.info("Finished engagement classification")
        except Exception as e:
            logging.error("Engagement generator failed due to the following error: " + str(e))
            success = False

        if success:
            # delete the user's webcam data from s3 if the analytics job is successful
            self.s3.delete_user_video(face_video_key)

        # delete the data from local filesystem
        os.remove(video_file_path)
        return


