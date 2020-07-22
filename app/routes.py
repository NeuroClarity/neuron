from flask import Flask, request, jsonify
from app.analytics.facial_encoding.classifier import EmotionModel
from app.analytics.eye_tracking.video_heatmap import Heatmap

app = Flask(__name__)

@app.route('/api/video/heatmap', methods=['POST'])
def generate_heatmap():
    s3 = boto3.resource('s3')

    json_data = request.get_json()
    print(json_data)
    video_path = json_data['videoKey']
    video_file = json_data['eye_gaze_data']

    video_file = "FILLER" # TODO: This should be pulling from S3
    eye_gaze_array = "FILLER" # TODO: This should be pulling from S3

    model = Heatmap()
    score, predicted = model.generate_heatmap(video_file, eye_gaze_array)

    emotion_response = {'emotion': {
                        'embedding': score,
                        'emotion': predicted
                        },
    }

    data = open(video_path, 'rb')
    s3.Bucket('my-bucket').put_object(Key='videoKeyHeatmap.jpg', Body=data) # Edit to work specifically with s3

    return jsonify(emotion_response)

@app.route('/api/video/emotion', methods=['POST'])
def classify_emotion():

    json_data = request.get_json()
    print(json_data)
    video_path = json_data['dataKey'] 

    video_file = "FILLER" # TODO: This should be pulling from S3 with video_path

    model = EmotionModel() 
    score, predicted = model.classify_video(video_file)

    save_path = 'sample_output.npy'
    #np.save(save_path, score) # This should save the video to save_path path to S3
    emotion_response = {'emotion': {
                        'embedding_path': save_path,
                        'emotion': predicted
                        },
    }

    return jsonify(emotion_response)

def main():
    # Upload a new file
    data = open('test.jpg', 'rb')
    s3.Bucket('my-bucket').put_object(Key='test.jpg', Body=data)
