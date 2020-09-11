import cv2
import numpy as np
import glob
import sys

def img_to_vid(file_path, frames_for_video):
    img_array = []
    for i in range(int(frames_for_video)):
        img = cv2.imread(file_path)
        height, width, layers = img.shape
        size = (width,height)
        img_array.append(img)

    out = cv2.VideoWriter('project.avi',cv2.VideoWriter_fourcc(*'DIVX'), 15, size)

    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()

## TEST
if __name__=="__main__":
    file_path = sys.argv[1]
    frames_for_video = sys.argv[2]
    img_to_vid(file_path, frames_for_video)
