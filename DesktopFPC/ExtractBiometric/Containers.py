import cv2
import uuid

def cap_n_write(record_time):
    DIMENSION = (800, 600)
    FPS = 30
    SLIDE_TIME_WINDOW = 10

    global_frame_counter = 0

    capture_video_stream = cv2.VideoCapture(0)

    while global_frame_counter != FPS * record_time:

        filename = str(uuid.uuid4()) + '.mp4'
        output_video_file = cv2.VideoWriter('../TempStorage/' + filename, cv2.VideoWriter_fourcc(*'XVID'),
                                            FPS, DIMENSION)
        local_frame_counter = 0

        while local_frame_counter != FPS * SLIDE_TIME_WINDOW:
            boolean_result, frame = capture_video_stream.read()

            if boolean_result:
                resized_frame = cv2.resize(frame, DIMENSION, interpolation=cv2.INTER_AREA)
                output_video_file.write(resized_frame)
                local_frame_counter += 1
            else:
                print('error') # вывод ошибки видеокамеры пользовтелю
                break

        output_video_file.release()
        # вызов нейросетевой обработки с передачей параметров : filename, DIMENSION,~(FPS)
        global_frame_counter += FPS * SLIDE_TIME_WINDOW

    capture_video_stream.release()


