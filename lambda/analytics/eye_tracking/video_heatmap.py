from .heatmap import Heatmapper
from .video import VideoHeatmapper

from PIL import Image

import os
import json

from moviepy.editor import VideoFileClip
import numpy as np

class Heatmap():
    def __init__(self):
        pass

    """
    Accepts JSON data in the form of: 
    {
        screenWidth: int,
        screenHeight: int, 
        collectionInterval: int, 
        coordinates: [
        {
            "X": int,
            "Y": int
        },
        {
            "X": int,
            "Y": int
        }]
    }
    """
    def generate_heatmap(self, video_path, eye_gaze_json):
        base_video = VideoFileClip(video_path, verbose=False)
        width, height = base_video.size
        eye_gaze_array = self.preprocess_data(eye_gaze_json, width, height)

        img_heatmapper = Heatmapper(point_diameter=90,  # the size of each point to be drawn
                                    point_strength=0.6,  # the strength, between 0 and 1, of each point to be drawn
                                    opacity=0.40,
                                    colours='default' )
        video_heatmapper = VideoHeatmapper(img_heatmapper)
        heatmap_video = video_heatmapper.heatmap_on_video_path(
            video=base_video,
            points=eye_gaze_array
        )

        video_save_path = './videos/heatmap-result.mp4'
        heatmap_video.write_videofile(video_save_path, bitrate="5000k", fps=24, verbose=False, logger=None) # TODO: This should actually be saving to S3

        return video_save_path

    def preprocess_data(self, json_data, videoWidth, videoHeight):
        data = json_data["coordinates"]
        results = []
        count = 0

        # interpolate data (one data point for each millisecond)
        gap = json_data["collectionInterval"]
        for index in range(len(data)):
            x = data[index]["X"]
            y = data[index]["Y"]
            if index != len(data) - 1:
                xn = data[index + 1]["X"]
                yn = data[index + 1]["Y"]
                func_x = lambda coord: ((xn - x) / gap) * coord + x
                func_y = lambda coord: ((yn - y) / gap) * coord + y
                for i in range(int(gap)):
                    results.append([func_x(i), func_y(i), i + count])
            else:
                results.append([x, y, count])
            count += int(gap)

        results = np.array(results)
        # Normalize the data according to the size of the video
        # TODO: replace normalization numbers with the size of the video
        results[:, 0] = (results[:, 0] / json_data["screenWidth"]) * videoWidth
        results[:, 1] = (results[:, 1] / json_data["screenHeight"]) * videoHeight
        return results

# TEST
if __name__ == '__main__':
    with open("sample_data/eye_data.json") as f:
        my_data = json.load(f)

    module = Heatmap()
    module.generate_heatmap("demo.mp4", my_data)

