from flask import Flask, request, jsonify
from numpy import genfromtxt
from concurrent.futures import ThreadPoolExecutor
import json
import cv2
import logging

from app.analytics.facial_encoding.classifier import EmotionModel
from app.analytics.eye_tracking.video_heatmap import Heatmap
from app.infra.storage.storage import S3
from app import app

import numpy as np

# instantiate models
heatmap_model = Heatmap()
emotion_model = EmotionModel()

# define infra
s3 = S3("us-west-1")
#logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# Job Pool
NUM_THREADS = 2
thread_executor = ThreadPoolExecutor(NUM_THREADS)

@app.route('/api/video/analytics_job', methods=['POST'])
def analytics_job():
    try:
        json_data = request.get_json()
        logging.info("Received incoming request: " + str(json_data))

        content_video_key = json_data['contentVideoKey']
        eye_gaze_data = json_data['eyeGazeData']
        face_video_key = json_data['faceVideoKey']

        heatmap_destination_key = json_data["heatmapDestinationKey"]
        emotion_destination_key = json_data["emotionDestinationKey"]
        #engagement_destination_key = json_data["engagementDestinationKey"]

        generate_heatmap(content_video_key, eye_gaze_data, heatmap_destination_key)
        classify_emotion(face_video_key, emotion_destination_key)
        #generate_engagement(eye_gaze_key, engagement_destination_key)

        return {"success": True}

    except Exception as e:
        logging.error("analytics job failed:" + str(e))
        return {"success": False}

def generate_heatmap(video_key, eye_gaze_data, destination_key):
    try:
        video_file_path = "./download2.mp4"
        s3.download_original_video(video_key, video_file_path)

        thread_executor.submit(generate_heatmap_task, video_file_path, eye_gaze_data, destination_key)
    except Exception as e:
        logging.error("Heatmap failed to generate due to the following error: " + str(e))
        return {"Success": False}

    return {"Success": True}

def generate_engagement(eye_gaze_key, destination_key):
    try:
        eye_gaze_path = "./download.csv"
        s3.download_eye_tracking_data(eye_gaze_key, eye_gaze_path)
        eye_gaze_array = genfromtxt(eye_gaze_path, delimiter=' ')

        engagement = np.ones([1, eye_gaze_array.shape[1]])
        for i in range(eye_gaze_array.shape[1]):
            if not eye_gaze_array[i].all():
                engagement[i] = 0
        engagement_response = {"engagement": [i.tolist() for i in engagement]}

        s3.upload_engagement(destination_key, json.dumps(engagement_response))
    except Exception as e:
        logging.error("Engagement generator failed due to the following error: " + str(e))
        return {"Success": False}

    return {"Success": True}

def generate_heatmap_task(video_file_path, eye_gaze_data, destination_key):
    try:
        video_save_path = heatmap_model.generate_heatmap(video_file_path, eye_gaze_data)
        with open(video_save_path, 'rb') as f:
            s3.upload_heatmap(destination_key, f)
    except Exception as e:
        logging.error(e)

    return

def classify_emotion(video_key, destination_key):
    try:

        video_file_path = "./download.mp4"
        s3.download_user_video(video_key, video_file_path)

        thread_executor.submit(classify_emotion_task, video_file_path, destination_key)
    except Exception as e:
        logging.error("Failed to classify emotion due to the following error: " + str(e))
        return {"Success": False}

    return {"Success": True}

def classify_emotion_task(video_file_path, destination_key):
    try:
        score, _ = emotion_model.classify_video(video_file_path)
        emotion_response = {'embedding': [i.tolist() for i in score]}
        s3.upload_emotion(destination_key, json.dumps(emotion_response))
    except Exception as e:
        logging.error(e)
    return

