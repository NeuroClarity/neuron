from flask import Flask, request, jsonify
from app.analytics.facial_encoding.classifier import EmotionModel
from app.analytics.eye_tracking.video_heatmap import Heatmap
from app.infra.storage.storage import S3
from app import app
from numpy import genfromtxt

import json
import cv2




# instantiate models
heatmap_model = Heatmap()
emotion_model = EmotionModel()

# define infra
s3 = S3("us-west-1")

@app.route('/api/video/heatmap', methods=['POST'])
def generate_heatmap():

    json_data = request.get_json()
    print("Received incoming request:", json_data)

    video_key = json_data['videoKey']
    eye_gaze_key = json_data['eyeGazeKey']

    video_file_path = "./download2.mp4"
    eye_gaze_path = "./download.csv"

    s3.download_original_video(video_key, video_file_path)
    s3.download_eye_tracking_data(eye_gaze_key, eye_gaze_path)

    eye_gaze_array = genfromtxt(eye_gaze_path, delimiter=' ')

    video_save_path = heatmap_model.generate_heatmap(video_file_path, eye_gaze_array)

    with open(video_save_path, 'rb') as f:
        print(f)
        s3.upload_heatmap(json_data["destinationKey"], f)

    return "success"



@app.route('/api/video/emotion', methods=['POST'])
def classify_emotion():

    json_data = request.get_json()
    print("Received incoming request:", json_data)

    video_key = json_data['videoKey']

    video_file_path = "./download.mp4"

    s3.download_original_video(video_key, video_file_path)

    score, _ = emotion_model.classify_video(video_file_path)

    save_path = 'sample_output.npy'

    emotion_response = {'embedding': [i.tolist() for i in score]}
    emotion_response = json.dumps(emotion_response)

    s3.upload_emotion(json_data["destinationKey"], emotion_response)
    return emotion_response



def main():


    # Upload a new file
    data_key_1 = 'dev-testing/IMG_1980.m4v'
    data_key_2 = 'testing/sample_eye_data.csv'
