from app.analytics.eye_tracking.heatmap import Heatmapper
from app.analytics.eye_tracking.video import VideoHeatmapper

from PIL import Image

import os

import numpy as np



class Heatmap():
    def __init__(self):
        pass

    def generate_heatmap(self, video_path, eye_gaze_array):

        img_heatmapper = Heatmapper(point_diameter=400,  # the size of each point to be drawn
                                    point_strength=0.6,  # the strength, between 0 and 1, of each point to be drawn
                                    opacity=0.40,
                                    colours='default' )
        video_heatmapper = VideoHeatmapper(img_heatmapper)

        heatmap_video = video_heatmapper.heatmap_on_video_path(
            video_path=video_path,
            points=eye_gaze_array
        )

        heatmap_video.write_videofile('out.mp4', bitrate="5000k", fps=24) # TODO: This should actually be saving to S3


def main():
    from numpy import genfromtxt
    my_data = genfromtxt('sample_eye_data.csv', delimiter=' ')
    print(my_data.shape)

    my_data[:, 2] = my_data[:, 2] - 38734

    module = Heatmap()

    module.video_heatmap("1984.mp4", my_data)
