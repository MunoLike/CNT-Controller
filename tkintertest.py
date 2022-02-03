import cv2
import tkinter as tk


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        # variable declartion
        self.registered = False
        self.present_sum = 0
        self.white_sum = 0
        self.in_progress = False
        self.counter = 0
        self.wait_cnt = 0
        self.auto_reset = False
        self.target_flowrate = 0
        self.is_simulation = False
        self.video_file_path = 'satellite.mp4'
        self.cap = None

        # set title
        self.master.title("CNT Film Maker")

        # app name
        self.app_title = tk.Label(
            self.master, text="CNT Film Maker", font=("", 15, "bold")
        )
        self.app_title.grid(row=0, column=0, columnspan=3, sticky=tk.N)

        # ratio control describe text
        self.duty_desctext = tk.Label(
            self.master, text="Operation Ratio(PWM Duty Ratio)", font=("", 13)
        )
        self.duty_desctext.grid(row=1, column=0, sticky=tk.W)

        # Peristaltic Pump PWM ON Ratio
        self.duty_ratio = tk.IntVar()
        self.bar_duty_ratio = tk.Scale(
            self.master,
            variable=self.duty_ratio,
            command=self.change_pwm_slider,
            orient=tk.HORIZONTAL,
            length=500,
            width=20,
            sliderlength=20,
            from_=0,
            to=100,
            resolution=1,
            takefocus=True,
        )

        self.bar_duty_ratio.grid(row=1, column=1, sticky=tk.E + tk.W)

        # duty input box
        self.duty_box = tk.Entry(self.master, width=10, font=("", 20))
        self.duty_box.insert(tk.END, "0")
        self.duty_box.bind("<KeyPress-Return>", self.press_enter_dutybox)
        vcmd = (self.duty_box.register(self.validation), "%P", "%S", "%d")  # validator
        self.duty_box.configure(validate="key", vcmd=vcmd)
        self.duty_box.grid(row=1, column=2, sticky=tk.E)

        # raw image view
        self.frame_rawimage = tk.LabelFrame(self.master, text='Raw Image')
        self.frame_rawimage.grid(row=2, column=0)
        self.canvas_rawimage = tk.Canvas(self.frame_rawimage)
        self.canvas_rawimage.grid(row=0, column=1)

        self.crop_posx = tk.IntVar()
        self.bar_crop_posx = tk.Scale(
            self.frame_rawimage,
            variable=self.crop_posx,
            orient=tk.HORIZONTAL,
            length=200,
            width=20,
            sliderlength=20,
            from_=0,
            to=360,
            resolution=1,
            takefocus=True,
        )
        self.bar_crop_posx.grid(row=1, column=0)

        
        self.crop_posy = tk.IntVar()
        self.bar_crop_posy = tk.Scale(
            self.frame_rawimage,
            variable=self.crop_posy,
            orient=tk.VERTICAL,
            length=200,
            width=20,
            sliderlength=20,
            from_=0,
            to=360,
            resolution=1,
            takefocus=True,
        )
        self.bar_crop_posy.grid(row=0, column=1)



        # cropped image view
        self.frame_croppedimage = tk.LabelFrame(self.master, text='Cropped Image')
        self.frame_croppedimage.grid(row=2, column=1)
        self.canvas_croppedimage = tk.Canvas(self.frame_croppedimage)
        self.canvas_croppedimage.pack()

        # differences and binarized image view
        self.frame_binarizedimage = tk.LabelFrame(self.master, text='Binarized Image')
        self.frame_binarizedimage.grid(row=2, column=2)
        self.canvas_binarizedimage = tk.Canvas(self.frame_binarizedimage)
        self.canvas_binarizedimage.grid(row=0,column=0)

        self.threshold = tk.IntVar()
        self.bar_threshold = tk.Scale(
            self.frame_binarizedimage,
            variable=self.threshold,
            orient=tk.HORIZONTAL,
            length=200,
            width=20,
            sliderlength=20,
            from_=0,
            to=255,
            resolution=1,
            takefocus=True,
        )
        self.bar_threshold.grid(row=1, column=0)

        # select movie or real cam
        self.movie_radio = tk.Radiobutton()

        # adjust to window size
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=1)

        master.grid_columnconfigure(0, weight=0)
        master.grid_columnconfigure(1, weight=1)
        master.grid_columnconfigure(2, weight=0)

    def change_pwm_slider(self, e):
        self.duty_box.delete(0, tk.END)
        self.duty_box.insert(tk.END, str(self.duty_ratio.get()))
        pass

    def press_enter_dutybox(self, e):
        self.duty_ratio.set(int(self.duty_box.get()))

    def validation(self, now_str, insert_str, in_type):
        print('input', now_str, insert_str)

        # 入力文字が整数か
        if not insert_str.isdecimal():
            return False

        # 100を超えないようにする
        if in_type != 0 and int(now_str or '0') > 100:
            return False

        return True

    def openfile(self):
        pass

    def cv_init(self):
        self.cap = None
        if self.is_simulation:
            self.cap = cv2.VideoCapture(self.video_file_path)
        else:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 120)
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 50)


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
