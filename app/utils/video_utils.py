import cv2
import numpy as np
import glob
import sys
import os

LENGTH = 8 # length of resulting video in seconds
FPS = 30 # frames per second of resulting video
TARGET_WIDTH = 640

def get_video_from_image(file_path, output_dir):
    img = cv2.imread(file_path)
    height, width, layers = img.shape

    # downsample the image
    ratio = TARGET_WIDTH / width
    width, height = int(width * ratio), int(height * ratio) 
    img = cv2.resize(img, dsize=(width, height), interpolation=cv2.INTER_CUBIC)
    height, width, layers = img.shape
    size = (width,height)

    NUM_FRAMES = FPS * LENGTH
    img_array = []
    for _ in range(NUM_FRAMES):
        img_array.append(img)

    output_file = "{0}/user_content.mp4".format(output_dir)
    output_file_2 = "{0}/user_content2.mp4".format(output_dir)
    out = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*"mp4v"), FPS, size)

    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()

    # This is required to convert to a format that is readable by the browser
    print("Converting mp4 to browser interpretable format...")
    os.system("ffmpeg -hide_banner -loglevel warning -y -i {0} -vcodec libx264 {1}".format(output_file, output_file_2))

    with open(output_file_2, "rb") as f:
        content = f.read()

    return content

# TEST
if __name__=="__main__":
    file_path = sys.argv[1]
    get_video_from_image(file_path, './tmp')
