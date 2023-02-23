import cv2
import os,sys
import uuid
from threading import Thread
import time

from ExtractBiometric.VideoProcessing import VideoProcessing
from evaluation import Evaluation
from errors import Error
from server_interaction import Violation,ServerData
from ExtractBiometric.Authentication.mouse import Mouse
from ExtractBiometric.Proctoring.WindowTracking import WindowFocusTrack
sys.path.append('TempStorage')
flag = 0
tid = 0

def cap_n_write(record_time,window_track):

    # DIMENSION = (320, 320)
    # FPS = 30
    # SLIDE_TIME_WINDOW = 10
    # screen_borders = [0,1,-10,10,-10,10]
    get_data = ServerData()

    image,DIMENSION,SLIDE_TIME_WINDOW,FPS, screen_borders= get_data.get()
    img_srv = cv2.imread(image)

    global_frame_counter = 0
    people_counter = 0
    mouse = Mouse()
    error = Error()



    capture_video_stream = cv2.VideoCapture(0)

    while global_frame_counter != FPS * record_time:


        filename = 'TempStorage/' + str(uuid.uuid4()) + '.mp4'

        output_video_file = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'XVID'),
                                            FPS, DIMENSION)
        local_frame_counter = 0

        while local_frame_counter != FPS * SLIDE_TIME_WINDOW:

            boolean_result, frame = capture_video_stream.read()
            if boolean_result:
                resized_frame = cv2.resize(frame, DIMENSION, interpolation=cv2.INTER_AREA)
                output_video_file.write(resized_frame)
                local_frame_counter += 1
            else:
                error.write_video()
                break

        output_video_file.release()


        result_biometric_processing = VideoProcessing(filename,DIMENSION,FPS,img_srv,global_frame_counter,
                                                      screen_borders)
        result_biometric_processing.video_processing_start()
        if result_biometric_processing.how_many_people_in_frame == 0:
            people_counter +=1
            if people_counter == (SLIDE_TIME_WINDOW // 3):
                error.no_people()

        if mouse.collection_check():
            mouse_result = mouse.result()
            local_evaluation(result_biometric_processing, window_track.result_tracking(), mouse_result)
        else:
            local_evaluation(result_biometric_processing, window_track.result_tracking())



        global_frame_counter += FPS * SLIDE_TIME_WINDOW


        if flag != 0:
            window_track.track_stop(tid)
            break
    capture_video_stream.release()

def inside_start(rec_time, name_ex):
    global tid
    global mouse
    window = WindowFocusTrack()

    th1 = Thread(target=cap_n_write,args=[rec_time,window])
    th2 = Thread(target=window.track_start,args=name_ex)
    th3 = Thread(target=mouse_tracking,args=mouse)

    thread_pool = [th1,th2,th3]
    for thread in thread_pool:
        thread.start()
    tid = th2.native_id

def exit_exam():
    global flag
    flag = 1

def local_evaluation(biometric_result, window_result, mouse_result=None):
    mark = Evaluation(biometric_result)
    if mouse_result is not None:
        mark.set_mouse(mouse_result)
    send_violation(mark.res_corr,window_result)

def mouse_tracking(mouse):
    mouse.collection()


def send_violation(res,window):
    violation = Violation(res,window)
    violation.send()


