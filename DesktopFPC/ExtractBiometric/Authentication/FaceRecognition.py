import cv2 as cv


class FaceRecognition:

    def __init__(self, model_path,disType=0, backend_id=0, target_id=0):
        self.model_path = model_path
        self.backend_id = backend_id
        self.dis_type = disType
        self.target_id = target_id
        self.rec_model = cv.FaceRecognizerSF.create(
            model=self.model_path,
            config="",
            backend_id=self.backend_id,
            target_id=self.target_id)

        self._threshold_cosine = 0.363

    def preprocess(self,frame,detect_box_face):
        if detect_box_face is None:
            return frame
        else:
            return self.rec_model.alignCrop(frame, detect_box_face)

    def vector_extraction(self, frame, result_of_detection):
        face_aligned = self.preprocess(frame, result_of_detection)
        face_vector = self.rec_model.feature(face_aligned)
        return face_vector


    def rec_match(self,frame, result_detect, img_srv):
        face1 = self.vector_extraction(frame, result_detect)
        face2 = self.vector_extraction(img_srv, result_detect)

        # only cos dis type

        if self.dis_type == 0:
            score_cosin = self.rec_model.match(face1[0][:-1], face2[0][:-1], self.dis_type)
            return 1 if score_cosin >= self._threshold_cosine else 0, score_cosin



