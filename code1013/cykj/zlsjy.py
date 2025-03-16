# -*- coding: utf-8 -*-
# @Time    : 2024/10/13 16:32
# @Author  : zwj, lyf, lhl
# @File    : zlsjy.py

import math

from cykj.zhipu import *
from cykj.summary2srt import *
from cykj.clip_main import clip_main
# from cykj.top_sentences import *
import sys
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from cykj.zhipu import *


# from zhipu import *
# from summary2srt import *
# from clip_main import clip_main
# import sys

class Worker(QThread):
    naviBarValue = pyqtSignal(int)
    index = 0
    i = 0
    
    def __init__(self):
        super(Worker,self).__init__()

    def setIndex(self, index):
        self.index = index
    
    def run(self):
        if self.i != self.index:
            self.i = self.index
            self.naviBarValue.emit(self.i)

def video_process(cykj, video_file, clip_save_folder, Funclisten):

    a = str(video_file)
    b = a.split('/')
    L = len(b)
    c = b[L-1].split('.')
    d = a.split('.')[0]
    print(c[0])
    print(d)
    os.system('mkdir ' + '/'.join(b[:-2]) + '/video')
    os.system("exit")
    srt_file = d + ".srt"
    llm_answer_file = '/'.join(b[:-2]) + '/video/' + c[0] + ".txt"
    cut_srt_file = '/'.join(b[:-2]) + '/video/' + c[0] + "_cut.srt"
    summary_file = '/'.join(b[:-2]) + '/video/' + c[0] + "_summary.txt"
    srt_txt_test_file = '/'.join(b[:-2]) + '/video/' + c[0] + "_srt_txt.txt"


    #LLM总结
    print("开始运行zhipu_main")
    cykj.zhipu_main(srt_file, llm_answer_file, srt_txt_test_file)


    now_index = 0
    keywords_list = cykj.zhipu_keywords_main(srt_file, srt_txt_test_file)
    now_index += 10
    Funclisten.setIndex(now_index)
    Funclisten.start()

    #keywords_list = keywords_list[0:3]


    # clip
    start_time_list = []
    len_list = []
    topn_value = 1

    kwlen = math.floor(80/len(keywords_list))

    
    for keyword in keywords_list:
        now_index += kwlen
        Funclisten.setIndex(now_index)
        Funclisten.start()
        start_time_list_temp, len_list_temp = clip_main(video_file, clip_save_folder, keyword, topn_value)
        start_time_list = start_time_list + start_time_list_temp
        len_list = len_list + len_list_temp



    # combine clip and autocut video
    summary2srt_main(srt_file=srt_file, llm_answer_file=llm_answer_file, cut_srt_file=cut_srt_file,
                     summary_file=summary_file, start_time_list=start_time_list, len_list=len_list)

    cykj.finalSummary(summary_file)
    
    now_index = 99
    Funclisten.setIndex(now_index)
    Funclisten.start()
                     


    
    

def video_process_usercut(cykj, video_file, clip_save_folder, text, Funclisten):

    a = str(video_file)
    b = a.split('/')
    L = len(b)
    c = b[L-1].split('.')
    d = a.split('.')[0]
    print(c[0])
    print(d)
    os.system('mkdir ' + '/'.join(b[:-2]) + '/video')
    os.system("exit")
    srt_file = d + ".srt"
    llm_answer_file = '/'.join(b[:-2]) + '/video/' + c[0] + ".txt"
    cut_srt_file = '/'.join(b[:-2]) + '/video/' + c[0] + "_cut.srt"
    summary_file = '/'.join(b[:-2]) + '/video/' + c[0] + "_summary.txt"
    # top_sentences_file = '/'.join(b[:-2]) + '/video/' + c[0] + "_top.txt"
    srt_txt_test_file = '/'.join(b[:-2]) + '/video/' + c[0] + "_srt_txt.txt"

    keywords_list = cykj.zhipu_userkeywords_main(text)

    # top_sentences('./srt_test.txt', keywords_list, top_sentences_file)

    kwlen = math.floor(80/len(keywords_list))
    now_index = 0

    # clip
    start_time_list = []
    len_list = []
    topn_value = 3
    for keyword in keywords_list:
        now_index += kwlen
        Funclisten.setIndex(now_index)
        Funclisten.start()
        start_time_list_temp, len_list_temp = clip_main(video_file, clip_save_folder, keyword, topn_value)
        start_time_list =  start_time_list + start_time_list_temp
        len_list = len_list + len_list_temp

    # combine clip and autocut video
    summary2srt_usercut_main(srt_file=srt_file, llm_answer_file=llm_answer_file, cut_srt_file=cut_srt_file,
                     summary_file=summary_file, start_time_list=start_time_list, len_list=len_list)

    now_index = 100
    Funclisten.setIndex(now_index)
    Funclisten.start()
                     
if __name__=="__main__":
    video_file= "./media/interview.mp4"
    clip_save_folder= "./clip_tmp"
    srt_file="media/interview.srt"
    llm_answer_file="./zhipu_response.txt"
    cut_srt_file = './test_cut.srt'
    summary_file= './summary.txt'
    # video_process_test(video_file, clip_save_folder)
    #video_process_usercut(video_file, clip_save_folder, "一个男人在说话，脸上有笑容")



    #combine_srt_and_clip(start_time_list, len_list)

