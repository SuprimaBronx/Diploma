import time

from windowlocker import LLISTEN


class WindowFocusTrack:
    def __init__(self):
        self.event = 0
        self.use = LLISTEN()


    def track_start(self):
        self.use.listen()

    def track_stop(self,tid):
        self.use.set_stop_flag(tid)

    def result_tracking(self):
        get_raw = self.use.collection
        result = self.check_result(get_raw)
        return result

    def check_result(self,raw_data):
        summ = 0
        if raw_data is not None:
            for i in range(len(raw_data)):
                string = raw_data[i][1] + raw_data[i][2]
                if 'тест' not in string:
                    summ += raw_data[i][0]
                else:
                    continue
        return summ



