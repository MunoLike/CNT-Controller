import cv2
import tkinter as tk


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        #variable declartion
        self.registered = False
        self.present_sum = 0
        self.white_sum = 0
        self.in_progress = False
        self.counter = 0
        self.wait_cnt = 0
        self.auto_reset = False
        self.target_flowrate = 0

        #set title
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
        self.scale_var = tk.IntVar()
        self.scaleH = tk.Scale(
            self.master,
            variable=self.scale_var,
            command=self.pwm_slider,
            orient=tk.HORIZONTAL,
            length=500,
            width=20,
            sliderlength=20,
            from_=0,
            to=100,
            resolution=1,
            tickinterval=5,
            takefocus=True,
        )

        self.scaleH.grid(row=1, column=1, sticky=tk.E + tk.W)

        # duty input box
        self.duty_box = tk.Entry(width=10, font=("", 20))
        self.duty_box.insert(tk.END, "0")
        self.duty_box.bind("<KeyPress>", self.enter_dutybox)
        vcmd = (self.duty_box.register(self.validation), "%P", "%S", "%d") #validator
        self.duty_box.configure(validate="key", vcmd=vcmd)
        self.duty_box.grid(row=1, column=2, sticky=tk.E)

        # raw image view

        # cripped image view

        # differences and binarized image view

        # select movie or real cam
        self.movie_radio = tk.Radiobutton

        # adjust to window size
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=1)

        master.grid_columnconfigure(0, weight=0)
        master.grid_columnconfigure(1, weight=1)
        master.grid_columnconfigure(2, weight=0)

    def pwm_slider(self, e):
        #print(str(self.scale_var.get()))
        pass

    def enter_dutybox(self, e):
        pass

    def validation(self, now_str, insert_str, in_type):
        print('input',now_str, insert_str)
        
        #入力文字が整数か
        if not insert_str.isdecimal():
            return False

        #100を超えないようにする
        if in_type != 0 and int(now_str or '0') > 100:
            return False

        return True

    def cv_init():
        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
