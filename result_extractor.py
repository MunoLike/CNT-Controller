#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
import sys
import glob


if len(sys.argv) != 2 :
    print('invalid arguments') 
    sys.exit(-1)

target_dir=os.path.abspath(sys.argv[1])
#target_dir = os.path.abspath('0131')

print('Be about to search:',target_dir)
print('実行すると元ファイルに破壊的変更を加えます．初回実行時はバックアップを取ることをおすすめします．')
input('Enterキーを押下してください．')
csv_list = glob.glob(target_dir+r'\*.csv')
print(csv_list)

for file_path in csv_list:
    text=''
    with open(file_path, 'r') as file:
        body=file.readlines()
        
        delimiter=body[2][-3]
        
        if delimiter==',':
            continue

        body = body[15+20:]
        newbody=['']*len(body)

        for i in range(len(body)):
            newbody[i] = body[i].split(delimiter)[-1]
            
        text = ''.join(newbody)+'\n'


    with open(file_path, 'w') as file:
        file.write(text)