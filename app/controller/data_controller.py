import app.utils.video_utils as video_utils

class DataController():
    def __init__(self, s3):
        self.s3 = s3

    def convert_image_to_video(self, img_key, img_path, dest_key):
        self.s3.download_user_content(img_key, img_path)
        video_bytes = video_utils.get_video_from_image(img_path)
        self.s3.upload_user_video_content(dest_key, video_bytes)
        return

