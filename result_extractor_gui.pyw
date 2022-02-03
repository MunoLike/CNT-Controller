#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import glob
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk



def dirdiag_clicked():
    init_dir_path=os.path.abspath((os.path.dirname(__file__)))
    dir_path=filedialog.askdirectory(initialdir=init_dir_path)
    dir_path_var.set(dir_path)
    if dir_path:
        exec_button.focus_set()
    
    
def execute():

    if not dir_path_var.get():
        messagebox.showerror('エラー', '処理したいフォルダを選択してください．')
        return
    if not messagebox.askyesno('確認', '実行すると元ファイルに変更を加えます．\n初回実行時はバックアップを取ることをおすすめします．\n実行しますか？'):
        return

    csv_list = glob.glob(dir_path_var.get() + r"/*.csv")
    print(csv_list)

    for file_path in csv_list:
        text = ""
        with open(file_path, "r") as file:
            body = file.readlines()

            delimiter = body[2][-3]

            if delimiter == ",":
                continue

            body = body[15 + 20 :]
            newbody = [''] * len(body)

            for i in range(len(body)):
                newbody[i] = body[i].split(delimiter)[-1]

            text = "".join(newbody) + "\n"

        with open(file_path, "w") as file:
            file.write(text)

root = tk.Tk()
root.title("Result Extractor")

frame1=tk.Frame(root, padx=5, pady=5)
frame1.grid(row=0, column=0, sticky=tk.EW)
# ラベル
dir_label = ttk.Label(frame1, text="フォルダ参照")
dir_label.pack(side=tk.LEFT)
# フォルダパスインプットボックス
dir_path_var = tk.StringVar()
dir_entry = ttk.Entry(frame1, textvariable=dir_path_var, width=30)
dir_entry.pack(side=tk.LEFT, expand=True)
# 参照ボタン
dir_button = ttk.Button(frame1, text="参照", command=dirdiag_clicked, padding=[7,14,7,14])
dir_button.pack(side=tk.LEFT)

frame2 = tk.Frame(root, padx=5, pady=5) 
frame2.grid(row=1, column=0, sticky=tk.EW)
#実行ボタン
exec_button=ttk.Button(frame2, text='卍処理卍', command=execute, padding=[20])
exec_button.pack(anchor=tk.CENTER,fill=tk.BOTH)


# サイズ変更禁止
root.resizable(width=False, height=False)
root.mainloop()
