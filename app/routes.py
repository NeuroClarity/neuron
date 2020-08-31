from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor
import logging
import json

from app.analytics.facial_encoding.classifier import EmotionModel
from app.analytics.eye_tracking.video_heatmap import Heatmap
from app.analytics.engagement.classifier import EngagementModel
from app.infra.storage.storage import S3
from app import app

# instantiate models
heatmap_model = Heatmap()
emotion_model = EmotionModel()
engagement_model = EngagementModel()

# define infra
s3 = S3("us-west-1")
logging.basicConfig(level=logging.INFO)
#logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# Job Pool
NUM_THREADS = 3
thread_executor = ThreadPoolExecutor(NUM_THREADS)

@app.route('/api/video/analytics_job', methods=['POST'])
def analytics_job():
    success = False
    try:
        json_data = request.get_json()
        logging.info("Received incoming request: " + str(json_data))

        content_video_key = json_data['contentVideoKey']
        face_video_key = json_data['faceVideoKey']
        eye_gaze_data = json_data['eyeGazeData']

        heatmap_destination_key = json_data["heatmapDestinationKey"]
        emotion_destination_key = json_data["emotionDestinationKey"]
        engagement_destination_key = json_data["engagementDestinationKey"]

        # make async calls to start analysis
        generate_heatmap(content_video_key, eye_gaze_data, heatmap_destination_key)
        classify_emotion(face_video_key, emotion_destination_key)
        classify_engagement(eye_gaze_data, engagement_destination_key)

        success = True
    except Exception as e:
        logging.error("Analytics job failed:" + str(e))

    return {"Success": success}

"""
Gets data from s3 and starts generating the eye tracking heatmap in the background
"""
def generate_heatmap(video_key, eye_gaze_data, destination_key):
    video_file_path = "./videos/original-video.mp4"
    s3.download_original_video(video_key, video_file_path)

    thread_executor.submit(_heatmap_task, video_file_path, eye_gaze_data, destination_key)
    return

def _heatmap_task(video_file_path, eye_gaze_data, destination_key):
    try:
        video_save_path = heatmap_model.generate_heatmap(video_file_path, eye_gaze_data)
        with open(video_save_path, 'rb') as f:
            s3.upload_heatmap(destination_key, f)
        logging.info("Finished generating heatmap")
    except Exception as e:
        logging.error("Failed to generate heatmap:" + str(e))
    return

"""
Gets data from s3 and runs the classification algorithm in the background
"""
def classify_emotion(video_key, destination_key):
    video_file_path = "./videos/user-video.webm"
    s3.download_user_video(video_key, video_file_path)

    thread_executor.submit(_emotion_task, video_file_path, destination_key)
    return

def _emotion_task(video_file_path, destination_key):
    try:
        score, _ = emotion_model.classify_video(video_file_path)
        emotion_response = {'embedding': [i.tolist() for i in score]}
        s3.upload_emotion(destination_key, json.dumps(emotion_response))
        logging.info("Finished emotion classification")
    except Exception as e:
        logging.error("Failed to complete emotion classification task" + str(e))
    return

"""
Gets data from s3 and starts engagement classification algorithm in the background
"""
def classify_engagement(eye_gaze_data, destination_key):
    thread_executor.submit(_engagement_task, eye_gaze_data, destination_key)
    return

def _engagement_task(eye_gaze_data, destination_key):
    try:
        engagement = engagement_model.classify(eye_gaze_data)
        s3.upload_engagement(destination_key, json.dumps(engagement))
        logging.info("Finished engagement classification")
    except Exception as e:
        logging.error("Engagement generator failed due to the following error: " + str(e))
    return

