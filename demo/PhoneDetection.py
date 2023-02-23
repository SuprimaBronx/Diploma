import cv2



class PhoneDetection:

    def __init__(self, cfg,weights,classes_path,dimension,frame=0):

        self.frame = frame
        self.DIMENSION = [320,320]
        net = cv2.dnn.readNetFromDarknet(cfg, weights)
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
        self.model = cv2.dnn.DetectionModel(net)
        self.COLORS = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]
        self.model.setInputParams(size=self.DIMENSION, scale=1 / 255, swapRB=True)
        self.class_names = []
        with open('./phone_detection/classes.txt', "r") as f:
            self.class_names = [cname.strip() for cname in f.readlines()]


    def set_frame(self, frame):
        self.frame = frame

    def open_frame(self, frame):
        label = []
        frame = cv2.resize(frame, self.DIMENSION, interpolation=cv2.INTER_AREA)
        classes, scores, boxes = self.model.detect(frame, 0.7, 0.8)
        for (classid, score, box) in zip(classes, scores, boxes):
            label.append([self.class_names[classid], score])
        return label

    def object_definition(self, results):
        labels = results
        for i in range(len(labels)):
            if labels[i][0] == 'cell phone':
                return labels[i][1]
            else:
                continue
        return None

    def call(self,frame):
        img = frame
        results = self.open_frame(img)
        def_res = self.object_definition(results)
        return def_res