# -*- coding: utf-8 -*-
# @Time    : 2024/10/13 16:24
# @Author  : zwj, lyf, lhl
# @File    : clip_main.py

from docarray import Document
from jina import Flow, DocumentArray
import os
import glob
from jina.types.request.data import DataRequest
import streamlit as st
from jina import Client, DocumentArray, Document
import json
import os
import time
import uuid

from cykj.videoLoader.video_loader import *
from cykj.customClipImage.clip_image import *
from cykj.customClipText.clip_text import *
from cykj.customIndexer.executor import *

def config():
    os.environ['JINA_PORT'] = '45679'  # the port for accessing the RESTful service, i.e. http://localhost:45678/docs
    os.environ['JINA_WORKSPACE'] = './workspace'  # the directory to store the indexed data
    os.environ['TOP_K'] = '20'  # the maximal number of results to return


def cutVideo(start_t: str, length: int, input: str, output: str):
    """
    start_t: 起始位置
    length: 持续时长
    input: 视频输入位置
    output: 视频输出位置
    """
    os.system(f'ffmpeg -ss {start_t} -i {input} -t {length} -c:v copy -c:a copy -y {output}')


def getTime(t: int):
    m,s = divmod(t, 60)
    h, m = divmod(m, 60)
    t_str = "%02d:%02d:%02d" % (h, m, s)
    #print (t_str)
    return t_str

def search_clip(uid, video_file_path, text_prompt, topn_value, video_name, video_loader, image_encoder, text_encoder, indexer):
    
    print(f"\n\n\n search clip {text_prompt}\n\n\n")
    video = DocumentArray([Document(uri=video_file_path, id=str(uid) + video_name)])
    video_loader.extract(video, {})
    image_encoder.encode(video, {})
    indexer.index(video)    

    text = DocumentArray([Document(text=text_prompt)])
    # 传入 parameters 参数，即使为空
    text_encoder.encode(text, parameters={"uid": str(uid), "maxCount": int(topn_value), 
                                 "traversal_paths": "@r", "batch_size": 32})
    search_result = indexer.search(text, parameters={"uid": str(uid), "maxCount": int(topn_value), 
                                 "traversal_paths": "@r", "batch_size": 32})

    data = []
    for doc in search_result:
        doc_data = {}
        # 检查并添加必要字段
        print('*')
        if hasattr(doc, 'text'):
            doc_data['text'] = doc.text
        else:
            doc_data['text'] = None  # 或者你可以选择抛出错误

        if hasattr(doc, 'matches'):
            doc_data['matches'] = doc.matches.to_dict() if doc.matches else None
        else:
            doc_data['matches'] = None  # 或者你可以选择抛出错误

        data.append(doc_data)
    return json.dumps(data)



def check_device():
    device = "cpu"
    if (
        # os.environ.get("DEVICE") == "cuda" and
        torch.cuda.is_available()
    ):
        device = "cuda"
    print(f"The CLIP model is loaded on device: {device}")
    return device   


def clip_main(video_file_path, video_path, text_prompt, topn_value):
    config()
    uid = uuid.uuid1()
    device = check_device()

    # 初始化功能模块
    video_loader = VideoLoader(config='videoLoader/config.yml')
    image_encoder = CLIPImageEncoder(config='customClipImage/config.yml', device=device)
    text_encoder = CLIPTextEncoder(config='customClipText/config.yml', device=device)
    indexer = SimpleIndexer(config='customIndexer/config.yml', workspace=os.environ['JINA_WORKSPACE'])

    video_name = os.path.basename(video_file_path)
    result = search_clip(uid, video_file_path, text_prompt, topn_value, video_name, video_loader, image_encoder, text_encoder, indexer)
    result = json.loads(result)  # 解析得到的结果

    start_time_list = []
    len_list = []

    for i in range(len(result)):
        matchLen = len(result[i]['matches'])
        for j in range(matchLen):
            left = result[i]['matches'][j]['tags']['leftIndex']
            right = result[i]['matches'][j]['tags']['rightIndex']
            start_t = getTime(left)
            output = f"{video_path}/clip{text_prompt}{j}.mp4"
            start_time_list.append(start_t)
            video_len = int(right - left)
            len_list.append(video_len)
            # cutVideo(start_t, right - left, video_file_path, output)

    return start_time_list, len_list

if __name__ == '__main__':
    video_file= "/home/errico/桌面/autocut/media/interview.mp4"
    clip_save_folder= "./clip_tmp"
    srt_file="media/interview.srt"
    llm_answer_file="./zhipu_response.txt"
    cut_srt_file = './test_cut.srt'
    summary_file= './summary.txt'
    topn_value = 2
    keyword = '人物'
    start_time_list, len_list = clip_main(video_file, clip_save_folder, keyword, topn_value)
    print(start_time_list)