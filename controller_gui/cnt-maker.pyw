#! /usr/bin/env python3

from datetime import datetime
import os
import sys
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List
import cv2
import threading as th  # Pythonのスレッドは他の言語でいうところのスレッドとは異なる
import numpy as np
import pump_factory


# variables
root: tk.Tk = None
rect_pos: List[int] = [0, 0, 0, 0]  # [x1,y1, x2, y2]
is_started_drawing_rect: bool = False
is_finished_drawing_rect: bool = False
is_finished_confirm_rectpos: bool = False
is_mainthread_closing: bool = False
elapssed_time_tk: ttk.Label = None
elapssed_total_time_tk: ttk.Label = None
status_text_tk: ttk.Label = None
status_count_tk: ttk.Label = None
recent_dropped_time: float = 0.0
elapssed_total_time: float = 0.0
start_measure_time: float = 0.0

registered: bool = False
in_progress: bool = False
auto_reset: bool = False
is_wanna_bgreset: bool = False
is_wanna_counter_reset: bool = False
counter: int = 0
wait_cnt: int = 0
white_sum: int = 0
background: np.ndarray = None
image_binarized: np.ndarray = None
image_cropped: np.ndarray = None

pump: pump_factory.Pump = None
pump_ratio: int = 0

lock: th.Lock = th.Lock()

# consts
WINDOW_NAME_CROP = 'Crop'
WINDOW_NAME_RAWCROPPED = 'Cropped'
WINDOW_NAME_BINARY = 'Binary'
TRACKBAR_NAME_THRESHOLD = 'Threshold'
START_MEASUREMENT_THRESHOLD = 500
DETECT_DROP_THRESHOLD = 0.5
BGRESET_DURATION = 500
SRCTYPE_CAMERA = 0
SRCTYPE_FILE = 1
STATUS_WAITING_FOR_DROP = 0
STATUS_DROPPING = 1
STATUS_BGRESET = 2
STATUS_WAITING_FOR_SETBG = 3


def show_inputsrc_diag():
    # False:use the connected camera as a video source
    # True:use a video file as a video source
    root = tk.Tk()
    root.withdraw()
    ret = messagebox.askyesnocancel('入力ソースの選択', 'カメラからの映像を入力ソースとしますか？\nはい：カメラを入力ソースとする．\nいいえ：動画ファイルを入力ソースとする．')
    if ret == True:
        return (0, SRCTYPE_CAMERA)
    elif ret == False:
        init_dir_path = os.path.abspath((os.path.dirname(__file__)))
        dir_path = filedialog.askopenfile(initialdir=init_dir_path)
        if dir_path:
            return (dir_path.name, SRCTYPE_FILE)
        else:
            messagebox.showinfo('終了', 'ファイルが選択されなかったためプログラムを終了します．')
            sys.exit(0)
    else:
        sys.exit(0)


def designate_coords(e, x, y, flags, param):
    global is_started_drawing_rect, is_finished_drawing_rect
    if e == cv2.EVENT_LBUTTONDOWN:
        rect_pos[0] = x
        rect_pos[1] = y
        rect_pos[2] = x
        rect_pos[3] = y
        is_started_drawing_rect = True
        is_finished_drawing_rect = False
    elif e == cv2.EVENT_LBUTTONUP:
        rect_pos[2] = x
        rect_pos[3] = y
        is_started_drawing_rect = False
        is_finished_drawing_rect = True
    elif e == cv2.EVENT_MOUSEMOVE and is_started_drawing_rect:
        rect_pos[2] = x
        rect_pos[3] = y


def update_trackbar(val):
    # dummy
    pass


def info_window_thread() -> tk.Tk:
    global elapssed_time_tk, status_text_tk, status_count_tk, elapssed_total_time_tk

    root = tk.Tk()
    root.title('Processing Status')
    root.resizable(width=False, height=False)

    # Status Frame
    status_frame = ttk.Labelframe(root, text='Status')
    status_frame.pack(padx=5, pady=5)
    status_text_tk = ttk.Label(status_frame, font=('', 15))
    change_status_text(STATUS_WAITING_FOR_SETBG)
    status_text_tk.grid(row=0, column=0, columnspan=2, sticky=tk.W+tk.E)

    ttk.Label(status_frame, font=('', 15), text='Drop Count:').grid(row=1, column=0, sticky=tk.W)
    status_count_tk = ttk.Label(status_frame, font=('', 15), text=0)
    status_count_tk.grid(row=1, column=1, sticky=tk.E)

    ttk.Label(status_frame, font=('', 15), text='Elapssed Time(Recent)[s]:').grid(row=2, column=0, sticky=tk.W)
    elapssed_time_tk = ttk.Label(status_frame, font=('', 15), text='0.0')
    elapssed_time_tk.grid(row=2, column=1, sticky=tk.E)

    ttk.Label(status_frame, font=('', 15), text='Elapssed Time(Total)[s]:').grid(row=3, column=0, sticky=tk.W)
    elapssed_total_time_tk = ttk.Label(status_frame, font=('', 15), text='0.0')
    elapssed_total_time_tk.grid(row=3, column=1, sticky=tk.E)

    # Pump Frame
    pump_frame = ttk.Labelframe(root, text='Peristaltic Pump Control')
    pump_frame.pack(padx=5, pady=5)

    ttk.Label(pump_frame, font=('', 10), text='Pump Ratio(0~100%)').pack(padx=5, pady=5)
    bar_duty_ratio = ttk.Scale(
        pump_frame,
        orient=tk.HORIZONTAL,
        length=400,
        from_=0,
        to=100
    )
    bar_duty_ratio.pack(padx=5, pady=5, side=tk.RIGHT)

    duty_box = ttk.Entry(pump_frame, width=6, font=('', 10))
    duty_box.insert(tk.END, '0')
    duty_box.pack(padx=5, pady=5, side=tk.RIGHT)

    def change_pwm_slider(e):
        global pump_ratio
        pump_ratio = int(bar_duty_ratio.get())
        duty_box.delete(0, tk.END)
        duty_box.insert(tk.END, str(pump_ratio))
    bar_duty_ratio.config(command=change_pwm_slider)

    def press_enter(e):
        global pump_ratio
        duty: int = 0
        try:
            duty = int(duty_box.get())
            if 0 <= duty and 100 < duty:
                raise ValueError('Invalid Value')
            bar_duty_ratio.config(value=duty)
            pump_ratio = duty
        except:
            # catch atoi error and invalid input value error.
            duty_box.delete(0, tk.END)
            duty_box.insert(tk.END, int(bar_duty_ratio.get()))

    duty_box.bind('<KeyPress-Return>', press_enter)

    # button Frame
    button_frame = ttk.Frame(root)
    button_frame.pack(padx=5, pady=5)

    def reset_counter():
        global is_wanna_counter_reset
        is_wanna_counter_reset = True
    ttk.Button(button_frame, text='Reset Counter', command=reset_counter).pack(side=tk.LEFT, padx=5, pady=5)

    def set_background():
        global is_wanna_bgreset
        is_wanna_bgreset = True
    ttk.Button(button_frame, text='Set this image as a reference', command=set_background).pack(side=tk.LEFT, padx=5, pady=5)

    return root


def change_status_text(status):
    global status_text_tk, is_mainthread_closing

    if status == STATUS_WAITING_FOR_DROP:
        status_text_tk.config(foreground='green', text='Waiting for drop')
    elif status == STATUS_DROPPING:
        status_text_tk.config(foreground='orange', text='Measuring the drop now...')
    elif status == STATUS_BGRESET:
        status_text_tk.config(foreground='blue', text='Updating the reference image')
    elif status == STATUS_WAITING_FOR_SETBG:
        status_text_tk.config(foreground='black', text='Please press "Set this image as a reference"')


def close_window():
    global root, is_mainthread_closing, info_window, pump
    is_mainthread_closing = True
    pump.close()
    root.destroy()
    root.quit()


def img_show():
    global root
    # show images
    lock.acquire()
    if image_binarized is not None:
        cv2.imshow(WINDOW_NAME_BINARY, image_binarized)

    if image_cropped is not None:
        cv2.imshow(WINDOW_NAME_RAWCROPPED, image_cropped)

    key = cv2.waitKey(1)
    lock.release()
    # if close the windows, then end these processing
    if key == 27 or is_mainthread_closing:
        cv2.destroyAllWindows()
        return

    root.after(16, img_show)


def measuring(cap, src, src_type):
    global registered, in_progress, present_sum, counter, status_count_tk, \
        recent_dropped_time, auto_reset, elapssed_total_time, wait_cnt, white_sum,\
        is_wanna_bgreset, background, elapssed_time_tk, elapssed_total_time_tk, \
        start_measure_time, is_wanna_counter_reset, image_binarized, image_cropped, \
        pump

    # setup log writer
    now = datetime.now()
    result_writer = open(f'result/{now.strftime("%Y%m%d-%H%M%S")}-result.csv', 'w', encoding='utf-8', newline='\n')
    result_writer.write(f'Executed time, {now}\n')

    # setup pump control
    pump = pump_factory.create_pump()
    # Main loop
    while not is_mainthread_closing:
        ret, frame = cap.read()
        if not ret:
            break

        x1 = min(rect_pos[1], rect_pos[3])
        x2 = max(rect_pos[1], rect_pos[3])
        y1 = min(rect_pos[0], rect_pos[2])
        y2 = max(rect_pos[0], rect_pos[2])
        if src_type == SRCTYPE_CAMERA:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            frame = frame[x1:x2, y1:y2]

        lock.acquire()
        image_cropped = frame
        lock.release()

        # process some reset flag
        if is_wanna_bgreset:
            background = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            registered = True
            is_wanna_bgreset = False
            change_status_text(STATUS_BGRESET)

        if is_wanna_counter_reset:
            counter = 0
            status_count_tk.config(text=str(counter))
            elapssed_total_time = 0.0
            elapssed_time_tk.config(text=str(0.0))
            elapssed_total_time_tk.config(text=str(0.0))
            is_wanna_counter_reset = False

        if registered:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            mask = cv2.absdiff(gray, background)
            lock.acquire()
            _, image_binarized = cv2.threshold(mask, cv2.getTrackbarPos(TRACKBAR_NAME_THRESHOLD, WINDOW_NAME_BINARY),
                                               255, cv2.THRESH_BINARY)  # ここTHRESH_BINARY_INVにしてどうなのか気になる
            lock.release()

            pix_sum = np.sum(image_binarized)
            white_sum = pix_sum/255
            if white_sum >= START_MEASUREMENT_THRESHOLD:
                present_sum = white_sum
                change_status_text(STATUS_DROPPING)
                in_progress = True

            if counter >= 1:
                now = time.time()
                td = now - recent_dropped_time
                elapssed_time_tk.config(text='{:4.2f}'.format(td))
                td = now - start_measure_time
                elapssed_total_time_tk.config(text='{:4.2f}'.format(td))

            if in_progress:
                if white_sum/present_sum <= DETECT_DROP_THRESHOLD:
                    change_status_text(STATUS_WAITING_FOR_DROP)
                    counter += 1

                    if counter == 1:
                        elapssed_total_time = 0.0
                        elapssed_time_tk.config(text=str(0.0))
                        elapssed_total_time_tk.config(text=str(0.0))
                        start_measure_time = time.time()
                        result_writer.write(f'{counter}, 0\n')
                    else:
                        td = time.time() - recent_dropped_time
                        result_writer.write(f'{counter}, {td}\n')

                    status_count_tk.config(text=str(counter))
                    in_progress = False
                    recent_dropped_time = time.time()

            # 定期リセット
            if wait_cnt >= BGRESET_DURATION:
                wait_cnt = 0
                auto_reset = True
            wait_cnt += 1

            if auto_reset and white_sum <= 400:  # BGRESET_TORELANCE
                background = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # weight = 0.025
                # background = (1-weight)*cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)+weight*background# weightedAccumulate
                change_status_text(STATUS_BGRESET)
                auto_reset = False

        if src_type == SRCTYPE_FILE:
            time.sleep(0.0016)

        # pump control
        pump.change_ratio(pump_ratio)


def main():
    global is_finished_confirm_rectpos, is_finished_drawing_rect, root, info_window

    src, src_type = show_inputsrc_diag()
    cap = None
    if src_type == SRCTYPE_CAMERA:
        cap = cv2.VideoCapture(0)
        if cap.isOpened() is False:
            raise IOError
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 120)
        cap.set(cv2.CAP_PROP_BRIGHTNESS, 50)
    else:
        cap = cv2.VideoCapture(src)

    # TODO
    # frame size setup
    if src_type == SRCTYPE_CAMERA:
        cv2.namedWindow(WINDOW_NAME_CROP, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
        cv2.setMouseCallback(WINDOW_NAME_CROP, designate_coords)

    while (not is_finished_confirm_rectpos) and src_type == SRCTYPE_CAMERA:
        ret, frame = cap.read()

        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        if is_started_drawing_rect:
            frame = cv2.rectangle(frame, (rect_pos[0], rect_pos[1]), (rect_pos[2], rect_pos[3]), color=(0x28, 0x70, 0xFF), thickness=3)

        if is_finished_drawing_rect:
            ret = messagebox.askyesno('確認', '切り抜き範囲はこれでよろしいですか？')
            if ret:
                is_finished_confirm_rectpos = True
            else:
                is_finished_drawing_rect = False

        cv2.imshow(WINDOW_NAME_CROP, frame)
        if cv2.waitKey(1) == 27:
            messagebox.showinfo('終了', '終了します．')
            cv2.destroyWindow(WINDOW_NAME_CROP)
            sys.exit(0)

    if src_type == SRCTYPE_CAMERA:
        cv2.destroyWindow(WINDOW_NAME_CROP)

    # init info window(due to tkinter, main thread must be assigned UI thread)
    # this line must be executed before starting image processing process
    root = info_window_thread()

    # init opencv window
    info_window = th.Thread(target=measuring, args=(cap, src, src_type), daemon=True)
    info_window.start()

    # setup windows
    cv2.namedWindow(WINDOW_NAME_RAWCROPPED, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.namedWindow(WINDOW_NAME_BINARY, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.createTrackbar(TRACKBAR_NAME_THRESHOLD, WINDOW_NAME_BINARY, 25, 255, update_trackbar)
    root.after(16, img_show)

    root.protocol('WM_DELETE_WINDOW', close_window)
    root.mainloop()


if __name__ == '__main__':
    main()
