import numpy as np
import os
import json

from moviepy.editor import VideoFileClip
from PIL import Image

testing = False

if not testing:
    from app.infra.analytics.eye_tracking.heatmap import Heatmapper
    from app.infra.analytics.eye_tracking.video import VideoHeatmapper
else:
    from heatmap import Heatmapper
    from video import VideoHeatmapper

class Heatmap():
    def __init__(self, output_dir):
        self.output_dir = output_dir
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
    def moving_average(self, a, n=3) :
        ret = np.cumsum(a, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n

    def generate_heatmap(self, study_id, video_path, eye_gaze_json):
        base_video = VideoFileClip(video_path, verbose=False)
        width, height = base_video.size
        eye_gaze_array = self.preprocess_data(eye_gaze_json, width, height)
        # moving average over eye signal
        ma_window = 100
        x_ma = self.moving_average(eye_gaze_array[:, 0], ma_window)
        y_ma = self.moving_average(eye_gaze_array[:, 1], ma_window)
        eye_gaze_array[:-ma_window+1, 0] = x_ma
        eye_gaze_array[:-ma_window+1, 1] = y_ma
        img_heatmapper = Heatmapper(point_diameter=int(max(width, height) / 6.5),  # the size of each point to be drawn
                                    point_strength=0.15,  # the strength, between 0 and 1, of each point to be drawn
                                    opacity=0.40,
                                    colours='default' )
        video_heatmapper = VideoHeatmapper(img_heatmapper)
        heatmap_video = video_heatmapper.heatmap_on_video_path(
            video=base_video,
            points=eye_gaze_array
        )

        print("writing heatmap to disk")
        video_save_path = '{0}/heatmap-result--{1}.mp4'.format(self.output_dir, study_id)
        heatmap_video.write_videofile(video_save_path, bitrate="1200k", fps=24, verbose=False, logger=None, threads=4) # TODO: This should actually be saving to S3

        return video_save_path

    def preprocess_data(self, json_data, videoWidth, videoHeight):
        data_list = json_data["data"]
        results = []
        collection_frequency = 5 # one sample every 8ms

        # interpolate data 
        # iterate through the list of reviewers
        for data in data_list:
            try:
                screenWidth = data["screenWidth"]
                screenHeight = data["screenHeight"]
                coordinates = data["coordinates"]
                # iterate through each coordinate
                for index in range(len(coordinates)):
                    x = coordinates[index]["X"]
                    y = coordinates[index]["Y"]
                    time = coordinates[index]["Time"] * 1000
                    if index == len(coordinates) - 1:
                        results.append([(x / screenWidth) * videoWidth, (y / screenHeight) * videoHeight, time])
                        break

                    xn = coordinates[index + 1]["X"]
                    yn = coordinates[index + 1]["Y"]
                    timen = coordinates[index + 1]["Time"] * 1000
                    gap = (timen - time)
                    func_x = lambda coord: ((xn - x) / gap) * coord + x
                    func_y = lambda coord: ((yn - y) / gap) * coord + y
                    for i in range(0, int(gap), collection_frequency):
                        # Normalize the data according to the size of the video
                        results.append([(func_x(i) / screenWidth) * videoWidth, (func_y(i) / screenHeight) * videoHeight, time + i])
            except Exception as e:
                continue


        return np.array(results)

# TEST
if __name__ == '__main__':
    with open("sample_data/eye-tracking-data-multiple.json") as f:
        my_data = json.load(f)
    module = Heatmap("./sample_output")
    module.generate_heatmap("./sample_data/demo.mp4", my_data)

