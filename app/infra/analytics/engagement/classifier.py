import numpy as np
import json

class EngagementModel():
    def __init__(self):
        return

    def classify(self, data):
        data = data["data"]
        if not data:
            return

        data = data[0]
        eye_gaze_array = np.array([[d["X"], d["Y"]] for d in data["coordinates"]])
        engagement = np.ones([eye_gaze_array.shape[0], 1])

        for i in range(eye_gaze_array.shape[0]):
            if np.isnan(np.sum(eye_gaze_array[i])):
                engagement[i] = 0
        engagement_response_ma = self._get_moving_average(engagement, 3)
        engagement_response = {"Result": [i.tolist() for i in engagement_response_ma],
                               "ClassificationInterval":-1}


        return engagement_response

    def _get_moving_average(self, a, n=3) :
        ret = np.cumsum(a, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n

if __name__ == "__main__":
    with open("../eye_tracking/sample_data/eye_data.json") as f:
        my_data = json.load(f)

    model = EngagementModel()
    print(model.classify(my_data))

