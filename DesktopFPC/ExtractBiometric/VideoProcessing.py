import cv2 as cv
import sys
from random import randint
import multiprocessing as mpc

from Authentication.FaceDetection import YuNet

from Authentication.FaceRecognition import FaceRecognition
from Proctoring.HeadRotation import HeadRotation
from Proctoring.PhoneDetection import PhoneDetection
sys.path.append('../TempStorage' )



class VideoProcessing:

    def __init__(self, filename, DIMENSION, FPS, img_srv,frames, screen_borders):
        self.DIMENSION = DIMENSION
        self.FPS = FPS
        self.path_to_video = filename #  передать передачу
        self.how_many_people_in_frame = 0
        self.img_srv = img_srv
        self.frame_count = frames
        self.screen_borders = screen_borders
        self.window_auth_score = 0
        self.score = 0
        self.threads = [[0],1]
        self.counter = []
        cfg_path = 'Proctoring/phone_detection/yolov4-tiny.cfg'
        weights_path = 'Proctoring/phone_detection/yolov4-tiny.weights'
        classes = 'Proctoring/phone_detection/classes.txt'
        self.phone = PhoneDetection(cfg_path,weights_path,classes,self.DIMENSION)
        self.head = HeadRotation(self.screen_borders)

    def video_processing_start(self):
        tm = cv.TickMeter()
        capture_video = cv.VideoCapture(self.path_to_video)
        when_check_face = randint(0, self.frame_count)
        frame_counter = 0
        x_count = 0
        while True:
            capture_result, frame = capture_video.read()

            tm.start()
            if capture_result:
                frame = cv.resize(frame, self.DIMENSION, interpolation=cv.INTER_AREA)
                face_det_ret = self.face_detection(frame)
                if frame_counter == when_check_face:
                    face_recog_ret, conf_recog = self.face_recognition(face_det_ret, frame,
                                                                       self.img_srv)  # 1 - yes. 0 - no
                    # x_count +=45
                    self.counter.append(abs(conf_recog))
                    self.window_auth_score = face_recog_ret,conf_recog

                frame_copy = frame.copy()

                # cv.imshow('frame', frame)
                # cv.waitKey(1)
                x = self.head_rotation(frame)
                y = self.phone_detector(frame_copy)
                tm.stop()

                self.score = [tm.getFPS(),x,y,self.window_auth_score]
                print(self.score)
                frame_counter += 1
            else:
                print('error')
                capture_video.release()
                print('done')
                f = 0
                for i in range(len(self.counter)):
                    f += self.counter[i]
                f = f / len(self.counter)
                print(f)
                return self.score




    def face_detection(self, frame):
        result_detect = YuNet(modelPath='Authentication/face_detection_yunet/face_detection_yunet_2022mar.onnx',inputSize=self.DIMENSION).infer(frame)
        self.how_many_people_in_frame = result_detect.shape[0]
        return result_detect

    def face_recognition(self,result_of_detection,frame, img_srv):
        result_recognition, conf = FaceRecognition(model_path='Authentication/face_recognition_sface/face_recognition_sface_2021dec.onnx').rec_match(frame,result_of_detection, img_srv)
        return result_recognition, conf

    def head_rotation(self, frame):
        self.head.set_frame(frame)
        result_rotation = self.head.rotation_result()
        return result_rotation
        # self.threads[1] = result_rotation

    def phone_detector(self, frame):
        self.phone.set_frame(frame)
        result_phone = self.phone.call()
        return result_phone
        # self.threads[2] = result_phone


DIMENSION = (128,96)
FPS = 30
SLIDE_TIME_WINDOW = 10
img_srv = cv.imread('../1.jpg')  # получить изображение с сервера
screen_borders = [0,1,-10,10,-10,10] # получить координаты монитора с сервера (для глаз(0,1) и для направления лица(2-5))

qw = VideoProcessing('../TempStorage/1/dcb0d311-909d-4b92-b4bb-0bfd51e2dc28.mp4',DIMENSION,FPS,img_srv,300,
                                                      screen_borders)
qw.video_processing_start()





