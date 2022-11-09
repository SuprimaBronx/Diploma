import cv2 as cv
import os
import sys
sys.path.append(os.path.join(sys.path[0], '../NeuralLib/FaceDetection/face_detection_yunet'))


class FaceDetection:

    def __init__(self, DIMENSION, score_thr=0.9, nms_thr=0.3, top_k=5000, backend_id=0, target_id=0):
        self.score_thr = score_thr
        self.DIMENSION = DIMENSION
        self.nms_thr = nms_thr
        self.top_k = top_k
        self.model_path = 'face_detection_yunet_2022mar.onnx'
        self.backend_id = backend_id
        self.target_id = target_id

        self.model_yunet = cv.FaceDetectorYN.create(
            model=self.model_path,
            config='',
            input_size=self.DIMENSION,
            score_threshold = self.score_thr,
            nms_threshold = self.nms_thr,
            top_k = self.top_k,
            backend_id = self.backend_id,
            target_id = self.target_id)

    def face_detector(self, frame):
        detected = self.model_yunet.detect(frame)
        return detected[1]
