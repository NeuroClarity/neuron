
"""
visualize results for test image
"""
import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F
import os
import json
from torch.autograd import Variable

from skimage import io
from skimage.transform import resize

TESTING = True

if not TESTING:
    from app.analytics.facial_encoding.transforms import transforms
    from app.analytics.facial_encoding.models import *
    MODEL_PATH = "./app/analytics/facial_encoding/weights/PrivateTest_model.t7"
else:
    from transforms import transforms
    from models import *
    MODEL_PATH = "./weights/PrivateTest_model.t7"

class EmotionModel():
    """ Emotion model takes in a picture, recognizes a face within the picture, and predicts what type of
        emotion that face conveys between 'Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral'.

    """

    def __init__(self):

        self.net = VGG('VGG19')
        checkpoint = torch.load(MODEL_PATH, map_location=torch.device('cpu'))
        self.net.load_state_dict(checkpoint['net'])
        self.net.eval()

        self.past_score = []
        self.past_predicted = ''

        self.class_names = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']


    def forward(self, frame):
        """ forward runs a forward pass though the model
            Input:
                frame - a picture of variable size with a face on it.
            Output:
                score - NumPy array where each value represents the probaility of each of hte 7 possible emotions
                predicted - A string representing the emotion with the highest probaility.
            """

        # Extracting the face
        image = frame
        #image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = faceCascade.detectMultiScale(
            image,
            scaleFactor=1.3,
            minNeighbors=3,
            minSize=(30, 30)
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            image = image[y:y + h, x:x + w]


        cut_size = 48

        transform_test = transforms.Compose([
            transforms.TenCrop(cut_size),
            transforms.Lambda(lambda crops: torch.stack([transforms.ToTensor()(crop) for crop in crops])),
        ])


        def rgb2gray(rgb):
            return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])

        if len(image)<5 or len(faces)==0:
            return self.past_score, self.past_predicted

        gray = rgb2gray(image)

        gray = resize(gray, (48,48), mode='symmetric').astype(np.uint8)

        img = gray[:, :, np.newaxis]

        img = np.concatenate((img, img, img), axis=2)
        img = Image.fromarray(img)
        inputs = transform_test(img)



        ncrops, c, h, w = np.shape(inputs)

        inputs = inputs.view(-1, c, h, w)
        inputs = Variable(inputs, volatile=True)
        outputs = self.net(inputs)

        outputs_avg = outputs.view(ncrops, -1).mean(0)  # avg over crops

        score = F.softmax(outputs_avg).data
        _, predicted = torch.max(outputs_avg.data, 0)
        predicted = self.class_names[predicted]
        print("strongest emotion", predicted)

        # Save in case next frame does not get a face
        self.past_score = score
        self.past_predicted = predicted

        return score, predicted


    def classify_video(self, video_file):
        """ Breaks up a video into its respective frames and runs each frame through the model.

            Input:
                video_file - the path to a video file

            Output:
                score - time series NumPy array where columns (dim 1) represents the 7 possible emotions
                    and the rows (dim 0) represent the proability of each emotion over time.
                predicted - A list of strings of same length as score.dim1 and each string representents the
                    emotion with the highest probability at that point in time.
        """
        if type(video_file) == type("string"):
            vid = cv2.VideoCapture(video_file)
        else:
            vid = cv2.VideoCapture(video_file)

        length = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))

        i=0
        score = []
        predicted = []
        for _ in range(length):
            # Capture the video frame
            ret, frame = vid.read()
            if ret == False:
                break

            if not i % 20:

                t_score, t_predicted = self.forward(frame)
                score.append(np.array(t_score))
                predicted.append(t_predicted)
            i+=1
        score = np.array(score)

        return score, predicted


### TESTS
if __name__ == '__main__':
    model = EmotionModel()
    score, predicted = model.classify_video("demo_video.mp4")
    print("types:", type(score), type(predicted))
    print(score.shape, len(predicted))
    assert(score.shape[0] == len(predicted))
    with open("emotion_data.json", "w+") as f:
        json.dump({"embedding": [i.tolist() for i in score]}, f)

    print("Finished writing results to emotion_data.json")
