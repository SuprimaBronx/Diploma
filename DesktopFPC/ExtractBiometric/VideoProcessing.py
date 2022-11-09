import cv2 as cv
import sys
from FaceDetection import FaceDetection
from Authentication.FaceRecognition import FaceRecognition
sys.path.append('../TempStorage' )


class VideoProcessing:

    def __init__(self, filename, DIMENSION, FPS):
        self.DIMENSION = DIMENSION
        self.FPS = FPS
        self.path_to_video = '../TempStorage/' + filename


    def video_processing_start(self):

        capture_video = cv.VideoCapture(self.path_to_video)
        # w = int(capture_video.get(cv.CAP_PROP_FRAME_WIDTH))
        # h = int(capture_video.get(cv.CAP_PROP_FRAME_HEIGHT))
        # print(v,h)

        while True:
            capture_result, frame = capture_video.read()

            if capture_result:
                face_det_ret = self.face_detection(frame)
                face_recog_ret = self.face_recognition(face_det_ret)  # распознавать только иногда сделать



            else:
                print('error - cant read video frame')


    def face_detection(self, frame):
        result_detect = FaceDetection(self.DIMENSION).face_detector(frame)
        return result_detect
    def face_recognition(self,result_of_detection):
        result_recognition = FaceRecognition().recognition()
        pass