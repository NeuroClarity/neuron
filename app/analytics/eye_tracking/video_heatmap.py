
testing = False

if not testing:
    from app.analytics.eye_tracking.heatmap import Heatmapper
    from app.analytics.eye_tracking.video import VideoHeatmapper
else:
    from heatmap import Heatmapper
    from video import VideoHeatmapper

from PIL import Image

import os

import numpy as np

class Heatmap():
    def __init__(self):
        pass

    def generate_heatmap(self, video_path, eye_gaze_array):

        img_heatmapper = Heatmapper(point_diameter=90,  # the size of each point to be drawn
                                    point_strength=0.6,  # the strength, between 0 and 1, of each point to be drawn
                                    opacity=0.40,
                                    colours='default' )
        video_heatmapper = VideoHeatmapper(img_heatmapper)

        heatmap_video = video_heatmapper.heatmap_on_video_path(
            video_path=video_path,
            points=eye_gaze_array
        )

        video_save_path = 'out.mp4'

        heatmap_video.write_videofile(video_save_path, bitrate="5000k", fps=24) # TODO: This should actually be saving to S3

        return video_save_path


# TEST
if __name__ == '__main__':
    from numpy import genfromtxt
    my_data = genfromtxt('./interpolated_data.csv', delimiter=' ')
    my_data[:, 0] = (my_data[:, 0] / max(my_data[:, 0])) * 640
    my_data[:, 1] = (my_data[:, 1] / max(my_data[:, 1])) * 360
    my_data[:, 2] = my_data[:, 2]
    print(my_data)

    module = Heatmap()

    module.generate_heatmap("demo.mp4", my_data)

