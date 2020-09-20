from flask import request
import logging
import json
import os

from app.controller.analytics_controller import AnalyticsController
from app.controller.data_controller import DataController
from app.infra.storage.storage import S3

from app import app

# create directory to temporarily store videos before upload
OUTPUT_DIR = "./tmp"
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

s3 = S3("us-west-1")
analytics_controller = AnalyticsController(s3, OUTPUT_DIR)
data_controller = DataController(s3, OUTPUT_DIR)

# log to std out
logging.basicConfig(level=logging.INFO)

@app.route('/api/ping', methods=['GET'])
def ping():
    return "Success."


@app.route('/api/image/convert', methods=['POST'])
def convert_image():
    success = False
    try:
        json_data = request.get_json()
        logging.info("Received incoming request: " + str(json_data))

        image_content_key = json_data['imageContentKey']
        destination_key = json_data['destinationKey']
        length = json_data['length']

        filename = image_content_key.rsplit("/", 1)[-1]
        destination_path = "{0}/{1}".format(OUTPUT_DIR, filename)
        data_controller.convert_image_to_video(image_content_key, destination_path, length, destination_key)

        success = True
    except Exception as e:
        logging.error("Failed to convert image:" + str(e))

    return {"Success": success}


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

        # TODO: this is jank, the study_id should instead be passed in as input
        study_id = content_video_key.split("/")[0]

        # make async calls to start analysis
        analytics_controller.submit_analytics_job(
                study_id,
                content_video_key, 
                eye_gaze_data, face_video_key, 
                heatmap_destination_key, emotion_destination_key, engagement_destination_key)

        success = True
    except Exception as e:
        logging.error("Analytics job failed:" + str(e))

    return {"Success": success}

