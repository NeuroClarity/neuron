from flask import Flask, request, jsonify
from video_heatmap import Heatmap

app = Flask(__name__)


@app.route('/api/heatmap', methods=['POST'])
def ping():

    s3 = boto3.resource('s3')

    json_data = request.get_json()
    print(json_data)
    video_path = json_data['videoKey']
    video_file = json_data['eye_gaze_data']

    video_file = "FILLER" # TODO: This should be pulling from S3
    eye_gaze_array = "FILLER" # TODO: This should be pulling from S3

    Net = Heatmap()
    score, predicted = Net.video_heatmap(video_file, eye_gaze_array)

    emotion_response = {'emotion': {
                        'embedding': score,
                        'emotion': predicted
                        },
    }

    data = open(video_path, 'rb')
    s3.Bucket('my-bucket').put_object(Key='videoKeyHeatmap.jpg', Body=data) # Edit to work specifically with s3

    return jsonify(emotion_response)


# Upload a new file
data = open('test.jpg', 'rb')
s3.Bucket('my-bucket').put_object(Key='test.jpg', Body=data)
