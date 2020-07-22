from flask import Flask, request, jsonify
from predictor import Emotion_model

app = Flask(__name__)


@app.route('/api/videoEmotionPredict', methods=['POST'])
def ping():

    json_data = request.get_json()
    print(json_data)
    video_path = json_data['dataKey'] 

    videp_file = "FILLER" # TODO: This should be pulling from S3 with video_path

    Net = Emotion_model()
    score, predicted = Net.video_predictor(video_file)

    save_path = 'sample_output.npy'
    #np.save(save_path, score) # This should save the video to save_path path to S3
    emotion_response = {'emotion': {
                        'embedding_path': save_path,
                        'emotion': predicted
                        },
    }

    return jsonify(emotion_response)