# -*- coding: utf-8 -*-
# @Time    : 2024/10/13 16:30
# @Author  : zwj, lyf, lhl
# @File    : top_sentences.py

# import os
# os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from sentence_transformers import SentenceTransformer


def top_sentences(text_file, sentences1, processed_file):
    # model = SentenceTransformer("./all-MiniLM-L6-v2")
    model = SentenceTransformer("./cykj/mode/distiluse-base-multilingual-cased-v1")


    with open(text_file, 'r', encoding='utf-8') as file:
        sentences2 = file.readlines()


    # Compute embeddings for both lists
    embeddings1 = model.encode(sentences1)
    embeddings2 = model.encode(sentences2)

    # Compute cosine similarities
    similarities = model.similarity(embeddings1, embeddings2)


    with open(processed_file, "w", encoding="utf-8") as file:
        file.write("以下是相关度较高的字幕：\n")

    with open(processed_file, "a", encoding="utf-8") as file:
        for idx_j, sentence2 in enumerate(sentences2):
            for idx_i, sentence1 in enumerate(sentences1):
                if similarities[idx_i][idx_j] > 0.5:
                    file.write(f"-{sentence2.strip()}: {similarities[idx_i][idx_j]:.4f}\n")
                    print(f"-{sentence2.strip()}: {similarities[idx_i][idx_j]:.4f}")
                    break  # Found a match, move to the next sentence2


    # top_n = 3

    # # 对于 sentences1 中的每一个句子，找出与 sentences2 中最相似的 top_n 个句子
    # for idx_i, sentence1 in enumerate(sentences1):
    #     # 获取第 idx_i 个句子的所有相似度值
    #     sim_scores = list(enumerate(similarities[idx_i]))
        
    #     # 根据相似度降序排序
    #     sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
    #     # 获取 top_n 个相似度最高的句子
    #     top_scores = sim_scores[:top_n]
        
    #     # 输出这些句子及其相似度
    #     print(f"Top {top_n} most similar sentences to '{sentence1}':")
    #     for idx_j, score in top_scores:
    #         print(f" - {sentences2[idx_j].strip():<30}: {score:.4f}")
    #     print()  # 输出空行以区分不同的句子对

    #     # with open(processed_file, "w", encoding="utf-8") as file:
    #     #     file.write("以下是相关台词：\n")
    #     # Save to a txt file
    #     with open(processed_file, "a", encoding="utf-8") as file:
    #         for idx_j, score in top_scores:
    #             file.write(f" - {sentences2[idx_j].strip():<30}: {score:.4f}\n")




if __name__=="__main__":
    text_file = '/home/errico/桌面/code903/srt_test.txt'
    sentences1 = [
        "头发",
        "电影"
    ]

    processed_file = './top_sentences.txt'
    top_sentences(text_file, sentences1, processed_file)
