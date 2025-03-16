# -*- coding: utf-8 -*-
# @Time    : 2024/10/13 16:32
# @Author  : zwj, lyf, lhl
# @File    : zhipu.py

import os
from langchain.llms import OpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import re

from cykj import prompts as pt

# llm = OpenAI(
#         model_name="gpt-4o",
#         openai_api_base="https://aihubmix.com/v1",
#         openai_api_key="sk-Eh4q6vDDkRNnEGeuDe9225Bb5220447e9e7043E43f8863D9"
# )
# prompt = ChatPromptTemplate(
#     input_variables=["chat_history", "question"],
#     messages=[
#         SystemMessagePromptTemplate.from_template(
#             '''回答问题'''
#         ),
#         MessagesPlaceholder(variable_name="chat_history"),
#         HumanMessagePromptTemplate.from_template("{question}")
#     ]
# )
# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
# conversation = LLMChain(
#     llm=llm,
#     prompt=prompt,
#     verbose=True,
#     memory=memory
# )

# llm = ChatOpenAI(
#         model="gpt-4o",
#         openai_api_base="https://aihubmix.com/v1",
#         openai_api_key="sk-Eh4q6vDDkRNnEGeuDe9225Bb5220447e9e7043E43f8863D9",
#         max_tokens=1024
#     )
class CYKJ():
    def __init__(self):
        self.llm = ChatOpenAI(
                model="gpt-4o",
                openai_api_base="https://aihubmix.com/v1",
                openai_api_key="sk-Eh4q6vDDkRNnEGeuDe9225Bb5220447e9e7043E43f8863D9"
        )
        self.srt_txt_test_file = "#"

# llm = ChatOpenAI(
#         model="glm-4",
#         openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
#         openai_api_key="add792c6af94b256e79e9b84b8b49b48.aODKdhFFJkeRwouT",
#     )





    def zhipu_main(self, srt_file, summary_file, srt_txt_test_file, min_num = 15,max_num = 20):

        new_prompt = pt.summary_segment_promt.replace("{min_num}", str(min_num))
        new_prompt = new_prompt.replace("{max_num}", str(max_num))

        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    new_prompt
                ),
                HumanMessagePromptTemplate.from_template("{question}")
            ]
        )
        conversation = LLMChain(
                llm=self.llm,
                prompt=prompt,
                verbose=True,
            )

        print("开始提取解说")
    #    conversation.prompt.messages[0] = SystemMessagePromptTemplate.from_template(new_prompt)


        def read_srt(srt_file, text_file):
            srt_content = ""
            with open(srt_file, "r", encoding="utf-8") as file:
                srt_content = file.read()  # Read the entire file content as a string

            # print(srt_content)
            # Extract text lines from SRT content
            text_lines = re.findall(r"\d+\n[\d:,]+ --> [\d:,]+\n(.*?)\n", srt_content, re.DOTALL)
            filtered_lines = [line for line in text_lines if "< No Speech >" not in line]


            text_content = "\n".join(filtered_lines)

            # Save to a txt file
            with open(text_file, "w", encoding="utf-8") as file:
                file.write(text_content)

        self.srt_txt_test_file = srt_txt_test_file
        text_file = srt_txt_test_file
        read_srt(srt_file, text_file)


        with open(text_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        question_list = []
        question=''
        cnt = 1
        for line in lines:
            #question = question + line.strip() + ','
            question = question + '\n'+ line
        # print(line)
            if(len(question) > 5000):
                question_list.append(question)
                question = ''
                cnt = cnt + 1
            #print(line.strip())
        question_list.append(question)    
            

        with open(summary_file, "w") as file:
            for i in range(cnt):
                response = conversation.invoke({"question": question_list[i]})
                print("Response:", response['text'])
                file.write(response['text'] + "\n")

        

    def zhipu_keywords_main(self,srt_file, srt_txt_test_file, min_num = 1, max_num = 3):

        print("开始提取keyword")
        self.srt_txt_test_file = srt_txt_test_file


        new_prompt = pt.summary_key_promt.replace("{min_num}", str(min_num))
        new_prompt = new_prompt.replace("{max_num}", str(max_num))


        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    new_prompt
                ),
                HumanMessagePromptTemplate.from_template("{question}")
            ]
        )
        conversation = LLMChain(
                llm=self.llm,
                prompt=prompt,
                verbose=True,
            )


        def read_srt(srt_file, text_file):
            srt_content = ""
            with open(srt_file, "r", encoding="utf-8") as file:
                srt_content = file.read()  # Read the entire file content as a string

            print(srt_content)
            # Extract text lines from SRT content
            text_lines = re.findall(r"\d+\n[\d:,]+ --> [\d:,]+\n(.*?)\n", srt_content, re.DOTALL)
            filtered_lines = [line for line in text_lines if "< No Speech >" not in line]


            text_content = "\n".join(filtered_lines)

            # Save to a txt file
            with open(text_file, "w", encoding="utf-8") as file:
                file.write(text_content)

        text_file = srt_txt_test_file
        read_srt(srt_file, text_file)


        with open(text_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        question_list = []
        question=''
        cnt = 1
        
        for line in lines:
            #question = question + line.strip() + ','
            question = question + '\n'+ line
        # print(line)
            if(len(question) > 5000):
                question_list.append(question)
                question = ''
                cnt = cnt + 1
            #print(line.strip())
        question_list.append(question)


        def keywords_to_set(keywords):
            keywords_list = keywords.split()
            return keywords_list

        print("正在根据字幕提取关键词")
        #keywords = []
        keywords_list = []
        for i in range(len(question_list)):
            response = conversation.invoke({"question": question_list[i]})
            print("Response:", response['text'])
            keywords_list = keywords_to_set(response['text'])
            #keywords.append( response['text'])
        print('keywords list:',keywords_list)
        return keywords_list


    def zhipu_userkeywords_main(self, text,min_num= 1 , max_num = 5):
        new_prompt = pt.userkey_promt.replace("{min_num}", str(min_num))
        new_prompt = new_prompt.replace("{max_num}", str(max_num))
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    new_prompt
                ),
                HumanMessagePromptTemplate.from_template("{question}")
            ]
        )
        conversation = LLMChain(
                llm=self.llm,
                prompt=prompt,
                verbose=True,
        )


        
        print("正在根据用户输入内容提取关键词")
        response = conversation.invoke({"question": text})
        keywords_list = response['text'].split()
        print('keywords list:',keywords_list)
        return keywords_list



    def video_memory(self, conversation, fpath):
        a = str(fpath)
        b = a.split('/')
        L = len(b)
        c = b[L - 1].split('.')
        d = a.split('.')[0]
        srt_txt_test_file = '/'.join(b[:-2]) + '/video/' + c[0] + "_srt_txt.txt"
        text_file = srt_txt_test_file
        if self.srt_txt_test_file != "#":
            text_file = self.srt_txt_test_file
    
        conversation.prompt.messages[0] = SystemMessagePromptTemplate.from_template(pt.llm_memory)


        with open(text_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        question_list = []
        question=''
        cnt = 1
        for line in lines:
            #question = question + line.strip() + ','
            question = question + '\n'+ line
        # print(line)
            if(len(question) > 5000):
                question_list.append(question)
                question = ''
                cnt = cnt + 1
            #print(line.strip())
        question_list.append(question)    
            

        for i in range(cnt):
            response = conversation.invoke({"question": question_list[i]})
            print("Response:", response['text'])

    def simpleQA_init(self, fpath):
        prompt = ChatPromptTemplate(
                    input_variables=["chat_history", "question"],
                    messages=[
                        SystemMessagePromptTemplate.from_template(
                            '''回答问题'''
                        ),
                        MessagesPlaceholder(variable_name="chat_history"),
                        HumanMessagePromptTemplate.from_template("{question}")
                    ]
                )
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        conversation = LLMChain(
                    llm=self.llm,
                    prompt=prompt,
                    verbose=True,
                    memory=memory
                )
        
        self.video_memory(conversation, fpath)

        return conversation


    def simpleQA(self, question, conversation):
            
        conversation.llm = self.llm


        conversation.prompt.messages[0] = SystemMessagePromptTemplate.from_template(pt.user_qa_promt)



        response = conversation.invoke({"question": question})
        return response['text']


    def finalSummary(self, summary_file):
        new_prompt = SystemMessagePromptTemplate.from_template(
            pt.summary_final_promt
        )
        prompt = ChatPromptTemplate(
            messages=[
                new_prompt,
                HumanMessagePromptTemplate.from_template("{question}")
            ]
        )
        conversation = LLMChain(
                llm=self.llm,
                prompt=prompt,
                verbose=True,
            )


        with open(summary_file, 'r', encoding='utf-8') as file:
            text = file.read()
        response = conversation.invoke({"question": text})
        with open(summary_file, 'w', encoding='utf-8') as file:
            file.write(response['text'])


    def changeModel(self, model):
        if model == 1:
            print('切换claude')
            new_llm = ChatOpenAI(
                model="claude-3-5-sonnet@20240620",
                openai_api_base="https://aihubmix.com/v1",
                openai_api_key="sk-Eh4q6vDDkRNnEGeuDe9225Bb5220447e9e7043E43f8863D9"
            )        
        elif model == 2:
            print('切换gpt')
            new_llm = ChatOpenAI(
                model="gpt-4o",
                openai_api_base="https://aihubmix.com/v1",
                openai_api_key="sk-Eh4q6vDDkRNnEGeuDe9225Bb5220447e9e7043E43f8863D9"
        )
        self.llm = new_llm


