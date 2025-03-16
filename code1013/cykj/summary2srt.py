# -*- coding: utf-8 -*-
# @Time    : 2024/10/13 16:29
# @Author  : zwj, lyf, lhl
# @File    : summary2srt.py
import string
import re


import re

def extract_timespan(timestamp):
    # 正则表达式匹配时间戳
    match = re.match(r"(\d{2}:\d{2}:\d{2}),\d{3} --> (\d{2}:\d{2}:\d{2}),\d{3}", timestamp)
    if match:
        start_time = match.group(1)
        end_time = match.group(2)
        return start_time, end_time
    else:
        return None


def replace_punctuation_with_space(text):
    # 创建一个映射表，将所有标点符号映射为空格
    all_punctuations = string.punctuation + '。，、？！：；“”’‘'
    replace_dict = {ord(char): ' ' for char in all_punctuations}
    
    # 使用 translate 方法替换标点符号为空格
    return text.translate(replace_dict)

def extract_references(file_path, srt_map, valid_index_list):
    # 读取txt文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    # 定位“参考”部分的开始
    references = []
    parts = text.split('总结：')
    print('参考 sentence: ')
    for part in parts:
        if '参考：' in part:
            reference_text = part.split('参考：')[1].split('总结：')[0].strip()
            # 替换标点符号为空格
            cleaned_content = replace_punctuation_with_space(reference_text)
            #print(cleaned_content)
            cleaned_content_list = cleaned_content.split()
            for content in cleaned_content_list:
                if content in srt_map:
                    valid_index_list[srt_map[content]] = True
                    print(content)


def write_summary(llm_answer_file, summary_file):
    # 读取txt文件内容
    with open(llm_answer_file, 'r', encoding='utf-8') as file:
        text = file.read()


    combined_summary = ''
    flag = False
    parts = text.split('\n')
    tmp = ''
    for part in parts:
        print('part: ',part)
         
        if '参考：' in part:
            flag = False
            combined_summary =  combined_summary + tmp
        elif '总结：'in part:
            flag = True
            tmp = ''

        if flag:
            tmp = tmp + part


    with open(summary_file, 'w', encoding='utf-8') as file:
        file.write(combined_summary)
    print('combined_summary: ', combined_summary)
    return combined_summary


def init(srt_file):
    srt_map = {}
    with open(srt_file, 'r', encoding='utf-8') as file:
        text = file.read()
    lines = text.split('\n')
    flag = 0
    last = -1
    for line in lines:
        if(line.isdigit()):
            last = int(line)
        else:
            line_list = replace_punctuation_with_space(line).split()
            for mini_line in line_list:
                srt_map[mini_line] = last


    cnt = 0
    start_time_list = []
    end_time_list = []
    for line in lines:
        ## 数字行
        #print(line)
        if cnt == 0:
            if(line.isdigit()):
                last = int(line)
                cnt = cnt + 1
        ## 时间戳
        elif cnt == 1:
            # 提取时间戳
            start_time, end_time = extract_timespan(line)
            start_time_list.append(start_time)
            end_time_list.append(end_time)
            cnt = cnt + 1
        ## 字幕
        elif cnt == 2:
            cnt = cnt + 1
        ## 换行
        else:
            cnt = 0
    return last, srt_map, start_time_list, end_time_list

def srt_match(srt_file, valid_index_list):
    with open(srt_file, 'r', encoding='utf-8') as file:
        text = file.read()
    lines = text.split('\n')
    flag = True
    cnt = 0
    cut_lines = []
    for line in lines:
        ## 数字行
        #print(line)
        if cnt == 0:
            if(line.isdigit()):
                index = int(line)
                if(valid_index_list[index] == True):
                    flag = True
                    cut_lines.append(line)
                else:
                    flag = False
                cnt = cnt + 1
            else:
                flag = False
        ## 时间戳
        elif cnt == 1:
            if(flag == True):
                cut_lines.append(line)
            cnt = cnt + 1
        ## 字幕
        elif cnt == 2:
            if(flag == True):
                cut_lines.append(line)
            cnt = cnt + 1
        ## 换行
        else:
            if(flag == True):
                cut_lines.append(line)
            cnt = 0



    # for line in lines:
    #     if(line.isdigit()):
    #         index = int(line)
    #         #print(index)
    #         if(valid_index_list[index] == True):
    #             flag = True
    #             cut_lines.append(line)
    #         else:
    #             flag = False
    #     else:
    #         if(flag == True):
    #             cut_lines.append(line)
    return cut_lines

def write_srt(file_path, cut_lines):
    with open(file_path, 'w', encoding='utf-8') as file:
        for line in cut_lines:
            if(line.isdigit() == True):
                file.write('\n')
            file.write(line)
            file.write('\n')


def time_to_seconds(time_str):
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s


def is_range_in_timespan(clip_start_time_seconds, srt_start_time, srt_end_time):
    srt_start_time_seconds = time_to_seconds(srt_start_time)
    srt_end_time_seconds = time_to_seconds(srt_end_time)
    return srt_start_time_seconds <= clip_start_time_seconds <= srt_end_time_seconds

def combine_srt_and_clip(clip_start_time_list, clip_video_len_list, valid_index_list, srt_start_time_list, srt_end_time_list):
    clip_all_len = len(clip_start_time_list)
    print('clip_all_len: ', clip_all_len)
    print('clip_start_time_list:', clip_start_time_list)
    for i in range(clip_all_len):
        for clip_video_len in clip_video_len_list:
            for j in range(clip_video_len):
                clip_start_time = time_to_seconds(clip_start_time_list[i]) + j
                for k in range(len(srt_start_time_list)):
                    srt_start_time = srt_start_time_list[k]
                    srt_end_time = srt_end_time_list[k]
                    if is_range_in_timespan(clip_start_time, srt_start_time, srt_end_time):
                        valid_index_list[k] = True


def summary2srt_main_0(srt_file, llm_answer_file, summary_file, cut_srt_file):
    srt_map = {}
    len, srt_map, srt_start_time_list, srt_end_time_list = init(srt_file)
    len = len + 2
    valid_index_list  = [False] * len
    print('len: ',len)
    # 提取参考部分的文字并存储在列表中
    extract_references(llm_answer_file, srt_map, valid_index_list)


    cut_lines = srt_match(srt_file, valid_index_list)
    print('cut_lines: ',cut_lines)
    write_srt(cut_srt_file, cut_lines)

def center_expand(valid_index_list, len, k):
    back_list = []
    for i in range(len):
        if valid_index_list[i]:
            for j in range(k):
                if i - (j+1):
                    valid_index_list[i] = True
                if i + (j+1)<len:
                    back_list.append(i + (j+1))
    for index in back_list:
        valid_index_list[index]=True

def summary2srt_main(srt_file, llm_answer_file, summary_file, cut_srt_file, start_time_list, len_list, k=3):
    srt_map = {}
    len, srt_map, srt_start_time_list, srt_end_time_list = init(srt_file)
    len = len + 2
    valid_index_list  = [False] * len
    print('len: ',len)
    # 提取参考部分的文字并存储在列表中
    extract_references(llm_answer_file, srt_map, valid_index_list)

    center_expand(valid_index_list, len, k)

    write_summary(llm_answer_file, summary_file)

    combine_srt_and_clip(start_time_list, len_list, valid_index_list, srt_start_time_list, srt_end_time_list)

    cut_lines = srt_match(srt_file, valid_index_list)
    print('cut_lines: ',cut_lines)
    write_srt(cut_srt_file, cut_lines)


def summary2srt_usercut_main(srt_file, llm_answer_file, summary_file, cut_srt_file, start_time_list, len_list):
    srt_map = {}
    len, srt_map, srt_start_time_list, srt_end_time_list = init(srt_file)
    len = len + 2
    valid_index_list  = [False] * len
    print('len: ',len)
    # 提取参考部分的文字并存储在列表中
    # extract_references(llm_answer_file, srt_map, valid_index_list)

    # write_summary(llm_answer_file, summary_file)

    combine_srt_and_clip(start_time_list, len_list, valid_index_list, srt_start_time_list, srt_end_time_list)

    cut_lines = srt_match(srt_file, valid_index_list)
    print('cut_lines: ',cut_lines)
    write_srt(cut_srt_file, cut_lines)



# if __name__=="__main__":
#     srt_map = {}
#     len = init() + 2
#     valid_index_list  = [False] * len
#     print('len: ',len)
#     # 提取参考部分的文字并存储在列表中
#     extract_references('zhipu_response.txt')
#     cut_lines = srt_match()
#     print('cut_lines: ',cut_lines)
#     write_srt('./test_cut.srt', cut_lines)



