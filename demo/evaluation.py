class Evaluation():
    def __init__(self,frame_res):
        self.res_corr = 0
        self.fps = frame_res[0]
        self.mouse_res = None
        self.frame_res = frame_res[1:4]
        self.auth = frame_res[4]
        self.result = 0

    def set_mouse(self, mouse_res):
        self.mouse_res = mouse_res

    def global_corr(self):
        proct_score = self.proct_corr()
        self.res_corr = proct_score
        return self.res_corr


    def proct_corr(self):

        is_on = []
        FACE_DETECT = 2     #FD
        HEAD_ROTATE = 2.5   #HR
        PHONE_DETECT = 3.5  #PD
        PD_HR = 7
        PD_FD = 5.6
        FD_HR = 6.75
        PD_FD_HR = 10
        multi = [[['pd','hr'],PD_HR], [['pd', 'fd'],PD_FD], [['fd', 'hr'],FD_HR]]


        check = []

        detect_face = ['fd',self.frame_res[0],FACE_DETECT]
        rotate_head = ['hr',self.frame_res[1],HEAD_ROTATE]
        phone_detect = ['pd',self.frame_res[2],PHONE_DETECT]
        proct_systems = [detect_face,rotate_head,phone_detect]
        if proct_systems[0][1] is not None:
            proct_systems[0][1] = None
        if proct_systems[1][1] is 'Forward':
            proct_systems[1][1] = None

        for i in range(len(proct_systems)):
            if proct_systems[i][1] is not None:
                is_on.append(proct_systems[i][0])

        if len(is_on) == 1:
            for i in range(len(proct_systems)):
                if is_on[0] == proct_systems[i][0]:
                    self.result = proct_systems[i][2] / self.fps
        elif len(is_on) == 2:
            for i in range(len(multi)):
                if is_on in multi[i]:
                    self.result = multi[i][1] / self.fps
        elif len(is_on) == 3:
            self.result = PD_FD_HR/self.fps
        else:
            pass
        return self.result

    def auth_cor(self,f):
        if f < 0.363:
            self.result = 47
        return self.result






