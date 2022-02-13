import os
from tkinter import filedialog, messagebox
from turtle import bgcolor, width
import cv2
import tkinter as tk
from tkinter import ttk
import threading as th

# ref:https://qiita.com/KentoSugiyama7974/items/b1a30a25dc4af7f1cdfe

# consts
CAMERA = 1
MOV_FILE = 2


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        # variables declartion
        self.registered = False
        self.present_sum = 0
        self.white_sum = 0
        self.in_progress = False
        self.counter = 0
        self.wait_cnt = 0
        self.auto_reset = False
        self.target_flowrate = 0
        self.is_simulation = False
        self.video_file_path = tk.StringVar()
        self.cap = None
        self.is_running = False
        self.thread_vidplay = None
        self.sem = th.Lock()

        # set title
        self.master.title("CNT Film Maker")

        # app name
        self.app_title = tk.Label(
            self.master, text="CNT Film Maker", font=("", 15, "bold")
        )
        self.app_title.pack()

        self.frame_control = ttk.LabelFrame(root, text='Control')
        self.frame_control.pack(padx=5, pady=5)

        # ratio control describe text
        self.duty_desctext = ttk.Label(
            self.frame_control, text="PWM Duty Ratio[0~100%]")
        self.duty_desctext.grid(row=0, column=0, padx=5, pady=5)

        # Peristaltic Pump PWM Ratio
        self.duty_ratio = tk.IntVar()
        self.bar_duty_ratio = ttk.Scale(
            self.frame_control,
            variable=self.duty_ratio,
            command=self.change_pwm_slider,
            orient=tk.HORIZONTAL,
            length=500,
            from_=0,
            to=100,
            takefocus=True,
        )
        self.bar_duty_ratio.grid(row=0, column=1, padx=5, pady=5)

        # duty input box
        self.duty_box = ttk.Entry(self.frame_control, width=10, font=("", 20))
        self.duty_box.insert(tk.END, "0")
        self.duty_box.bind("<KeyPress-Return>", self.press_enter_dutybox)
        vcmd = (self.duty_box.register(self.validation), "%P", "%S", "%d")  # validator
        self.duty_box.config(validate="key", validatecommand=vcmd)
        self.duty_box.grid(row=0, column=2, padx=5, pady=5)

        # input source
        self.input_desctext = ttk.Label(self.frame_control, text="Input Source")
        self.input_desctext.grid(row=1, column=0, padx=5, pady=5)

        # radio button
        self.input_src = tk.IntVar(value=CAMERA)
        self.radio_camera = ttk.Radiobutton(self.frame_control, value=CAMERA, variable=self.input_src, text='Camera')
        self.radio_camera.grid(row=1, column=1, padx=5, pady=5)
        self.radio_movfile = ttk.Radiobutton(self.frame_control, value=MOV_FILE, variable=self.input_src, text='Movie File')
        self.radio_movfile.grid(row=1, column=2, padx=5, pady=5)
        self.video_file_path.set('参照')
        self.button_movref = ttk.Button(self.frame_control, textvariable=self.video_file_path, command=self.select_movsource)
        self.button_movref.grid(row=1, column=3, padx=5, pady=5)

        # Control Buttons
        self.frame_btn = ttk.Frame(self.frame_control)
        self.frame_btn.grid(row=2, column=0, columnspan=4)

        # exec btn
        self.button_exec = ttk.Button(self.frame_btn, text='実行', command=self.exec)
        self.button_exec.pack(side=tk.LEFT, padx=5, pady=5)
        # stop btn
        self.button_stop = ttk.Button(self.frame_btn, text='中断', command=self.stop)
        self.button_stop.pack(side=tk.LEFT, padx=5, pady=5)

        # raw image view
        self.frame_rawimage = ttk.LabelFrame(self.master, text='Raw Image')
        self.frame_rawimage.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH)
        self.canvas_rawimage = tk.Canvas(self.frame_rawimage)
        self.canvas_rawimage.grid(row=0, column=0, sticky=tk.NSEW)

        self.crop_posy = tk.IntVar()
        self.bar_crop_posy = ttk.Scale(
            self.frame_rawimage,
            variable=self.crop_posy,
            orient=tk.VERTICAL,
            from_=0,
            to=360,
            takefocus=True,
        )
        self.bar_crop_posy.grid(row=0, column=1, sticky=tk.N+tk.S)

        self.crop_posx = tk.IntVar()
        self.bar_crop_posx = ttk.Scale(
            self.frame_rawimage,
            variable=self.crop_posx,
            orient=tk.HORIZONTAL,
            from_=0,
            to=200,
            takefocus=True,
        )
        self.bar_crop_posx.grid(row=1, column=0, sticky=tk.E+tk.W)

        self.label_sizex = tk.Label(self.frame_rawimage, text='Box Size X')
        self.label_sizex.grid(row=2, column=1, sticky=tk.S)
        self.crop_sizex = tk.IntVar()
        self.bar_crop_sizex = ttk.Scale(
            self.frame_rawimage,
            variable=self.crop_sizex,
            orient=tk.HORIZONTAL,
            from_=0,
            to=200,
            takefocus=True,
        )
        self.bar_crop_sizex.grid(row=2, column=0, sticky=tk.E+tk.W)

        self.label_sizey = tk.Label(self.frame_rawimage, text='Box Size Y')
        self.label_sizey.grid(row=3, column=1, sticky=tk.S)
        self.crop_sizey = tk.IntVar()
        self.bar_crop_sizey = ttk.Scale(
            self.frame_rawimage,
            variable=self.crop_sizey,
            orient=tk.HORIZONTAL,
            from_=0,
            to=200,
            takefocus=True,
        )
        self.bar_crop_sizey.grid(row=3, column=0, sticky=tk.E+tk.W)

        # cropped image view
        self.frame_croppedimage = ttk.LabelFrame(self.master, text='Cropped Image')
        self.frame_croppedimage.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH)
        self.canvas_croppedimage = tk.Canvas(self.frame_croppedimage)
        self.canvas_croppedimage.pack()

        # differences and binarized image view
        self.frame_binarizedimage = ttk.LabelFrame(self.master, text='Binarized Image')
        self.frame_binarizedimage.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH)
        self.canvas_binarizedimage = tk.Canvas(self.frame_binarizedimage)
        self.canvas_binarizedimage.pack()

        self.threshold = tk.IntVar()
        self.bar_threshold = tk.Scale(
            self.frame_binarizedimage,
            variable=self.threshold,
            orient=tk.HORIZONTAL,
            width=20,
            sliderlength=20,
            from_=0,
            to=255,
            resolution=1,
            takefocus=True,
        )
        self.bar_threshold.pack(fill=tk.X)

    def change_pwm_slider(self, e):
        self.duty_box.delete(0, tk.END)
        self.duty_box.insert(tk.END, str(self.duty_ratio.get()))
        pass

    def press_enter_dutybox(self, e):
        self.duty_ratio.set(int(self.duty_box.get()))

    def validation(self, now_str, insert_str, in_type):
        # 入力文字が整数か
        if not insert_str.isdecimal():
            return False

        # 100を超えないようにする
        if in_type != 0 and int(now_str or '0') > 100:
            return False

        return True

    def select_movsource(self):
        init_dir_path = os.path.abspath((os.path.dirname(__file__)))
        dir_path = filedialog.askopenfile(initialdir=init_dir_path)
        if dir_path:
            self.video_file_path.set(dir_path.name)

    def play(self):
        while True:
            self.sem.acquire()
            if not self.is_running:
                self.sem.release()
                return

            ret, frame = self.cap.read()
            if not ret:
                messagebox.showinfo('情報', '再生が終了しました．')
                self.is_running = False
                self.sem.release()
                return

            
            

                
            self.sem.release()

    def exec(self):
        if self.is_running:
            self.stop()

        if self.input_src.get() == CAMERA:
            # Camera
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror('エラー', 'カメラデバイスを開くことができませんでした．')
                return
            vr = self.cap.isOpened()

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 90)
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 50)
        else:
            # Movie File
            self.cap = cv2.VideoCapture(self.video_file_path.get())
            if not self.cap.isOpened():
                messagebox.showerror('エラー', '動画ファイルが存在しなかったか，読み取れませんでした．')
                return

        self.thread_vidplay = th.Thread(target=self.play)
        self.thread_vidplay.setDaemon(True)
        self.thread_vidplay.start()

    def stop(self):
        self.sem.acquire()
        self.is_running = False
        self.thread_vidplay = None
        self.sem.release()


if __name__ == "__main__":
    root = tk.Tk()
    root.tk.call('source', 'azure.tcl')
    root.tk.call('set_theme', 'light')
    app = Application(master=root)
    root.resizable(width=False, height=False)
    root.geometry(f'+{int((root.winfo_screenwidth()*0.2)/2)}+{int((root.winfo_screenheight()*0.2)/2)}')
    app.mainloop()
