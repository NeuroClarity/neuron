
testing = False

if not testing:
    from app.analytics.eye_tracking.heatmap import Heatmapper
    from app.analytics.eye_tracking.video import VideoHeatmapper
else:
    from heatmap import Heatmapper
    from video import VideoHeatmapper

from PIL import Image

import os
import json

from moviepy.editor import VideoFileClip
import numpy as np

class Heatmap():
    def __init__(self):
        pass

    """
    Accepts JSON data in the following form. Each list of coordinates corresponds to one user: 
    {
        data: [
            {
                screenWidth: int,
                screenHeight: int, 
                collectionInterval: int, 
                coordinates: [
                        "X": int,
                        "Y": int
                    },
                    {
                        "X": int,
                        "Y": int
                    }],
            },
            {
                screenWidth: int,
                screenHeight: int, 
                collectionInterval: int, 
                coordinates: [
                        "X": int,
                        "Y": int
                    },
                    {
                        "X": int,
                        "Y": int
                    }],
            }
        ]

    }
    """
    def generate_heatmap(self, video_path, eye_gaze_json):
        base_video = VideoFileClip(video_path, verbose=False)
        width, height = base_video.size
        eye_gaze_array = self.preprocess_data(eye_gaze_json, width, height)

        img_heatmapper = Heatmapper(point_diameter=60,  # the size of each point to be drawn
                                    point_strength=0.1,  # the strength, between 0 and 1, of each point to be drawn
                                    opacity=0.75,
                                    colours='default' )
        video_heatmapper = VideoHeatmapper(img_heatmapper)
        heatmap_video = video_heatmapper.heatmap_on_video_path(
            video=base_video,
            points=eye_gaze_array
        )

        video_save_path = './content/heatmap-result.mp4'
        heatmap_video.write_videofile(video_save_path, bitrate="5000k", fps=24, verbose=False, logger=None) # TODO: This should actually be saving to S3

        return video_save_path

    def preprocess_data(self, json_data, videoWidth, videoHeight):
        data_list = json_data["data"]
        results = []

        # interpolate data (one data point for each millisecond)
        for data in data_list:
            count = 0
            screenWidth = data["screenWidth"]
            screenHeight = data["screenHeight"]
            gap = data["collectionInterval"]
            coordinates = data["coordinates"]
            for index in range(len(coordinates)):
                x = coordinates[index]["X"]
                y = coordinates[index]["Y"]
                if index != len(coordinates) - 1:
                    xn = coordinates[index + 1]["X"]
                    yn = coordinates[index + 1]["Y"]
                    func_x = lambda coord: ((xn - x) / gap) * coord + x
                    func_y = lambda coord: ((yn - y) / gap) * coord + y
                    for i in range(int(gap)):
                        # Normalize the data according to the size of the video
                        results.append([(func_x(i) / screenWidth) * videoWidth, (func_y(i) / screenHeight) * videoHeight, i + count])
                else:
                    results.append([(x / screenWidth) * videoWidth, (y / screenHeight) * videoHeight, count])
                count += int(gap)

        return np.array(results)

# TEST
if __name__ == '__main__':
    with open("sample_data/eye-tracking-data-multiple.json") as f:
        my_data = json.load(f)

    module = Heatmap()
    module.generate_heatmap("./sample_data/demo.mp4", my_data)

