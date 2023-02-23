import cv2 as cv
import sys
from random import randint
import multiprocessing as mpc

from face_detection_yunet.yunet import YuNet
from evaluation import Evaluation
from face_recognition_sface.sface import SFace
from HeadRotation import HeadRotation
from PhoneDetection import PhoneDetection
sys.path.append('../TempStorage' )


class VideoProcessing:

    def __init__(self, filename, DIMENSION, FPS, img_srv,resdet1,frames, screen_borders):
        self.DIMENSION = DIMENSION
        self.FPS = FPS
        self.path_to_video = filename #  передать передачу
        self.how_many_people_in_frame = 0
        self.img_srv = img_srv
        self.img_srv_res = resdet1
        self.frame_count = frames
        self.screen_borders = screen_borders
        self.window_auth_score = 0
        self.score = 0
        self.qqq = 0
        self.threads = [[0],1]
        self.counter = []
        cfg_path = 'phone_detection/yolov4-tiny.cfg'
        weights_path = 'phone_detection/yolov4-tiny.weights'
        classes = 'phone_detection/classes.txt'
        self.phone = PhoneDetection(cfg_path,weights_path,classes,self.DIMENSION)
        self.head = HeadRotation(self.screen_borders)


    def video_processing_start(self):
        tm = cv.TickMeter()
        xc = cv.TickMeter()
        capture_video = cv.VideoCapture(self.path_to_video)
        when_check_face = randint(0, self.frame_count)
        frame_counter = 0
        x_count = 0
        while True:
            capture_result, frame = capture_video.read()

            tm.start()
            xc.start()
            if capture_result:
                frame = cv.resize(frame, self.DIMENSION, interpolation=cv.INTER_AREA)
                face_det_ret = self.face_detection(frame)
                if frame_counter == x_count:
                    face_recog_ret, conf_recog = self.face_recognition(face_det_ret, frame,
                                                                       self.img_srv)  # 1 - yes. 0 - no
                    x_count +=45
                    self.counter.append(abs(conf_recog))
                    self.window_auth_score = face_recog_ret,conf_recog

                frame_copy = frame.copy()
                if frame_counter == 50:
                    print('50')
                x = self.head_rotation(frame)
                y = self.phone_detector(frame)
                tm.stop()
                q = None
                if face_det_ret is not None:
                    q = True

                self.score = [tm.getFPS(),q,x,y,self.window_auth_score]
                self.evaluation = Evaluation( self.score)
                self.qqq += self.evaluation.global_corr()
                self.visualise(frame)
                xc.stop()
                print(tm.getFPS(),self.qqq, x)
                frame_counter += 1
            else:
                capture_video.release()
                print('done')

                f = 0
                for i in range(len(self.counter)):
                    f += self.counter[i]
                f = f / len(self.counter)
                x = self.evaluation.auth_cor(f)
                self.qqq += x
                print(self.qqq)
                return self.score




    def face_detection(self, frame):
        result_detect = YuNet(modelPath='face_detection_yunet/face_detection_yunet_2022mar.onnx',inputSize=self.DIMENSION).infer(frame)
        self.how_many_people_in_frame = result_detect.shape[0]
        return result_detect

    def face_recognition(self,result_of_detection,frame, img_srv):
        result_recognition, conf = SFace(modelPath='face_recognition_sface/face_recognition_sface_2021dec.onnx').match(frame,result_of_detection, img_srv,self.img_srv_res)
        return result_recognition, conf

    def head_rotation(self, frame):
        self.head.set_frame(frame)
        result_rotation = self.head.rotation_result()
        return result_rotation
        # self.threads[1] = result_rotation

    def phone_detector(self, frame):

        result_phone = self.phone.call(frame)
        return result_phone
        # self.threads[2] = result_phone

    def visualise(self,image):
        cv.putText(image, 'fps:'+str(int(self.score[0])), (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv.putText(image, 'hr:'+str(self.score[2]), (120, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv.putText(image, str(round(self.score[4][1],3)), (10, 60), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv.putText(image, str(round(self.qqq,2)), (10, 450), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv.putText(image, 'ph: '+ str(self.score[3]), (10, 90), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv.putText(image, 'fc: '+str(self.score[1]), (10, 120), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv.imshow('frame', image)
        cv.waitKey(1)


DIMENSION = (640,480)
FPS = 30
SLIDE_TIME_WINDOW = 10
img_srv = cv.imread('photo/1.jpg')  # получить изображение с сервера
img_srv = cv.resize(img_srv,[640,480],interpolation=cv.INTER_AREA)
result_detect1 = YuNet(modelPath='face_detection_yunet/face_detection_yunet_2022mar.onnx',inputSize=DIMENSION).infer(img_srv)
screen_borders = [0,1,-10,10,-4,15] # получить координаты монитора с сервера (для глаз(0,1) и для направления лица(2-5))

qw = VideoProcessing('photo/1.mp4',DIMENSION,FPS,img_srv,result_detect1,300,
                                                      screen_borders)
qw.video_processing_start()





