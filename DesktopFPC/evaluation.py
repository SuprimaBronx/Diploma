class Evaluation():
    def __init__(self,frame_res):
        self.res_corr = 0
        self.fps = frame_res[0]
        self.mouse_res = None
        self.frame_res = frame_res[1:4]

    def set_mouse(self, mouse_res):
        self.mouse_res = mouse_res

    def global_corr(self):
        proct_score = self.proct_corr()
        auth_corr = self.auth_corr()
        self.res_corr = proct_score + auth_corr

    def proct_corr(self):
        result = 0
        FACE_DETECT = 2     #FD
        HEAD_ROTATE = 2.5   #HR
        PHONE_DETECT = 3.5  #PD
        PD_HR = 7
        PD_FD = 5.6
        FD_HR = 6.75
        PD_FD_HR = 10
        detect_face = [None,self.frame_res[0]]
        rotate_head = [None,self.frame_res[1]]
        phone_detect = [None,self.frame_res[2]]
        proct_systems = [detect_face,rotate_head,phone_detect]

        for i in range(len(proct_systems)):
            if proct_systems[i][1] is not None:
                proct_systems[0] = True


        for i in range(len(proct_systems)):
            if proct_systems[i][0] == True:






    def auth_corr(self):
        pass


