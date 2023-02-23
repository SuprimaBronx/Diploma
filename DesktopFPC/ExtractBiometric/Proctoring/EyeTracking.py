import cv2
from .gaze_tracking import GazeTracking

class EyeTrack:
    def __init__(self, frame, screen_borders):
        self.frame = frame
        self.gaze = GazeTracking()
        self.screen_borders = screen_borders
        self.is_right = 0

    def eye_work(self):
        self.gaze.refresh(self.frame)
        is_work = self.gaze.pupils_located()
        cords = [self.gaze.pupil_left_coords(), self.gaze.pupil_right_coords()]
        if (cords[0][0] > self.screen_borders[0][0] and cords[0][1] > self.screen_borders[0][1]) or (
                cords[1][0] > self.screen_borders[1][0] and cords[1][1] > self.screen_borders[1][1]):
            self.is_right = 1
        else:
            self.is_right = 2


        return is_work, self.is_right