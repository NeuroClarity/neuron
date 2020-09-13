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
from torchvision.transforms import Compose, CenterCrop, ToTensor, Normalize
from torchvision.models import squeezenet1_1
from skimage import io
from skimage.transform import resize

TESTING = True

if not TESTING:
    MODEL_PATH = "./app/analytics/facial_encoding/weights/PrivateTest_model.t7"
else:
    import matplotlib.pyplot as plt
    MODEL_PATH = "./weights/PrivateTest_model.t7"


class Model:
    def __init__(self):

        self.device = torch.device('cpu')
        self.load_path = "models/model_params.pt"

        model_conv = squeezenet1_1(pretrained=False)

        model_conv.classifier = nn.Sequential(
            nn.Dropout(p=0.5),
            nn.Conv2d(512, 2, kernel_size=1),
            nn.ReLU(inplace=True),
            nn.AvgPool2d(13),
        )
        for param in model_conv.parameters():
                    param.requires_grad = False

        model_conv = model_conv.to(self.device)

        model_conv.load_state_dict(torch.load(self.load_path))
        model_conv.eval()
        self.model = model_conv
        self.data_transform = Compose([CenterCrop(256),
                                          ToTensor(),
                                          Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])



    def inference(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = self.data_transform(image)
        image = image.unsqueeze(0)
        image = image.to(self.device)
        outputs = self.model.forward(image.float())
        outputs = outputs / outputs.sum(1)
        return outputs


class EngagementModel():
    """ Engagement model takes in a picture, recognizes a face within the picture, and predicts the
    level of engagement within that picture.
    """
    def __init__(self):

        self.model = Model()

        self.past_score = []
        self.past_predicted = ''

        self.class_names = ['Unenaged', 'Engaged']


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

        #FPS = vid.get(cv2.CAP_PROP_FRAME_COUNT)
        FPS = 30

        i=0
        score = []
        while (vid.isOpened()):
            # Capture the video frame
            ret, frame = vid.read()
            if ret == False:
                break

            if not i % 1:
                t_score = self.model.inference(frame)
                score.append(np.array(t_score))
            i+=1

        score = np.array(score)

        return score


### TESTS
if __name__ == '__main__':
    model = EngagementModel()
    score = model.classify_video("test_video_data/facial-video-data2.webm")
    print("types:", type(score))
    print(score.shape)
    plt.plot(score[:, :, 1])
    plt.show()
    with open("emotion_data.json", "w+") as f:
        json.dump({"embedding": [i.tolist() for i in score]}, f)

    print("Finished writing results to emotion_data.json")
