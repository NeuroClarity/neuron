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

# instantiate models
heatmap_model = Heatmap()
emotion_model = EmotionModel()

# define infra
s3 = S3("us-west-1")
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# Job Pool
NUM_THREADS = 2
thread_executor = ThreadPoolExecutor(NUM_THREADS)

@app.route('/api/video/heatmap', methods=['POST'])
def generate_heatmap():
    try:
        json_data = request.get_json()
        logging.info("Received incoming request: " + json_data)
        video_key = json_data['videoKey']
        eye_gaze_key = json_data['eyeGazeKey']

        video_file_path = "./download2.mp4"
        eye_gaze_path = "./download.csv"
        s3.download_original_video(video_key, video_file_path)
        s3.download_eye_tracking_data(eye_gaze_key, eye_gaze_path)

        eye_gaze_array = genfromtxt(eye_gaze_path, delimiter=' ')

        destination_key = json_data["destinationKey"]
        thread_executor.submit(generate_heatmap_task, video_file_path, eye_gaze_array, destination_key)
        thread_executor.submit(generate_engagement, eye_gaze_array, destination_key)
    except Exception as e:
        logging.error("Heatmap failed to generate due to the following error: " + e)
        return {"Success": False}

    return {"Success": True}


def generate_engagement(eye_gaze_data, destination_key):
    try:
        engagement = np.array([1, eye_gaze_data.shape[1]])
        for i in range(eye_gaze_data.shape[1]):
            if not eye_gaze_data[i].all():
                engagement[i] = 1
        engagement_response = {"engagement": [i.tolist() for i in engagement]}

        s3.upload_engagement(destination_key, json.dumps(emotion_response))
    except Exception as e:
        logging.error("engagement generator failed due to the following error: " + e)
        return {"Success": False}

    return {"Success": True}


def generate_heatmap_task(video_file_path, eye_gaze_data, destination_key):
    try:
        video_save_path = heatmap_model.generate_heatmap(video_file_path, eye_gaze_array)
        with open(video_save_path, 'rb') as f:
            s3.upload_heatmap(destination_key, f)
    except Exception as e:
        logging.error(e)

    return

@app.route('/api/video/emotion', methods=['POST'])
def classify_emotion():
    try:
        json_data = request.get_json()
        logging.info("Received incoming request: " + json_data)
        video_key = json_data['videoKey']

        video_file_path = "./download.mp4"
        s3.download_original_video(video_key, video_file_path)

        destination_key = json_data["destinationKey"]
        thread_executor.submit(classify_emotion_task, video_file_path, destination_key)
    except Exception as e:
        logging.error("Failed to classify emtion due to the following error: " + e)
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

