#! /usr/env/bin python
# -*-coding: utf-8 -*-

#���������ڶ�������4500���������BM25���ԣ����Ƚ����еĴ𰸺�����ȥ��stopwords��Ȼ����ڳ��ִ����ϸߵĴ������ȥ���������BM25��ֵ

#sys.agrv[1]Ϊѵ�����ݵ�·����sys.argv[2]Ϊѵ�����ݵ��ļ���,sys.argv[3]����ѵ�������е�����ĸ�����sys.argv[4]�������Ĳ���ѡȡ��ΪDCG@k��kֵ
#sys.argv[5]Ϊ�趨�ĵ��ʵ���������

import json
import sys
import numpy as np
import os
import re
import numpy as np

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import pynlpir

def get_words(sentence):
    #����Ϊһ��string�ľ��ӣ����Ϊ������ӵķֽ�ĵ���
    pynlpir.open()
    sentence_words_list = pynlpir.segment(sentence,pos_tagging=False)
    return sentence_words_list

def get_stop_words(file_path):
    file_read = open(file_path,'rb')
    stop_words_list = []
    for line in file_read.readlines():
        word = line.strip()
        stop_words_list.append(word)
    return stop_words_list

def sort_by_value(d): 
    items=d.items() 
    backitems=[[v[1],v[0]] for v in items] 
    backitems.sort(reverse = True) 
    return [ backitems[i][1] for i in range(0,len(backitems))]
    
def write_words_question(item,word_list,line_num):
    #�����������⼰�𰸵���ѡ�Ĵ������/home/dcd-qa/MLT_code/BM25/data/question_ansers_words_without_stopwords/�ļ����ж�Ӧ���ļ���
    file_write = open('/home/dcd-qa/MLT_code/BM25/data/question_ansers_words_without_stopwords/' + str(line_num-1),'ab+')
    file_write.write(item + '\t')
    for word in word_list:
        if word != ' ' and word != '' and word != ' ' and word != '��':
            file_write.write(str(word) + '\t')
    file_write.write('\n')
    file_write.close()
    
def write_words_answer(item,word_list,line_num,label):
    #�����������⼰�𰸵���ѡ�Ĵ������/home/dcd-qa/MLT_code/BM25/data/question_ansers_words_without_stopwords/�ļ����ж�Ӧ���ļ���
    file_write = open('/home/dcd-qa/MLT_code/BM25/data/question_ansers_words_without_stopwords/' + str(line_num-1),'ab+')
    file_write.write(item + '\t' + str(label) + '\t')
    for word in word_list:
        if word != ' ' and word != '' and word != ' ' and word != '��':
            file_write.write(str(word) + '\t')
    file_write.write('\n')
    file_write.close()
    
def get_word_dict(train_file,stop_words_list):
    #������������������е����⼰�𰸵ľ��ӽ��б��������ȶ������е�stopwords����ȥ����Ȼ���ҵ����дʵĳ��ִ��������ճ��ִ�����������֮�󣬶��ڳ��ִ����ر��ģ�
    #Ҳ����ȥ��
    f_read = open(train_file,'r')
    r1 = u"[\��\��\��\��\��\\\��\�A\��\��\��\��\��\��\��\��\��\��\��\��\��\��\��\��\��\!\"\#\$\%\&\'\(\)\*\+\,\-\.\/\:\;\<\=\>\?\@\��\��\?\��\��\��\��\��\��\��\��\��\��\��\��\��\[\]\^\_\`\{\|\}\~\]\+\��\��\~\+\��\��\.\��]"
    word_dict = {}
    line_num = 1
    for line in f_read.readlines():
        if line_num%1000 == 1:
            print 'Now for line_num: ' + str(line_num) + '\n'
        line_num = line_num + 1
        file_dict_temp = json.loads(line)
        query = file_dict_temp['query']
        query = re.sub(r1," " ,query)
        query_word_list = get_words(query)
        #��ȥ��stopwords�����洢�����е��ʵĳ��ִ���
        for word in query_word_list:
            if word in stop_words_list or word == 'br' or word == ' ' or word == '' or word == '��' or word == ' ' or word == u'\u3000':
                query_word_list.remove(word)
            elif word not in word_dict:
                word_dict[word] = 1
            else:
                word_dict[word] = word_dict[word] + 1

        passages_list = file_dict_temp['passages']
        for item in passages_list:
            item_passage_text_temp = item['passage_text']
            item_passage_text_temp_1 = re.sub(r1," " ,item_passage_text_temp)
            item_passage_text_temp_word_list = get_words(item_passage_text_temp_1)
            for word in item_passage_text_temp_word_list:
                if word in stop_words_list or word == 'br' or word == ' ' or word == '' or word == '��' or word == ' ' or word == u'\u3000':
                    item_passage_text_temp_word_list.remove(word)
                elif word not in word_dict:
                    word_dict[word] = 1
                else:
                    word_dict[word] = word_dict[word] + 1
    word_dict_list = sort_by_value(word_dict)
    # for word in word_dict_list:
        # print word,word_dict[word]
    #���ڳ��ִ�������1000�ε�ǰ103���ʣ�����Ӹ���question��answer��ɾȥ
    word_delete = []
    for word in word_dict_list:
        if word_dict[word] > 1000 or word_dict[word] < 2:
            word_delete.append(word)
    
    f_read.close()
    f_read = open(train_file,'r')
    line_num = 1
    question_length = [] #�洢ÿ��question�ĳ��ȣ����õ������ƽ������
    for line in f_read.readlines():
        if line_num%1000 == 1:
            print 'Now for line_num: ' + str(line_num) + '\n'
        line_num = line_num + 1
        file_dict_temp = json.loads(line)
        query = file_dict_temp['query']
        query = re.sub(r1," " ,query)
        query_word_list = get_words(query)
        #��ȥ��stopwords�����洢�����е��ʵĳ��ִ���
        for word in query_word_list:
            if word in stop_words_list or word == 'br' or word == ' ' or word == '' or word == ' ' or word == '��' or word == u'\u3000' or word in word_delete:
                query_word_list.remove(word)
            else:
                continue
        write_words_question('question',query_word_list,line_num)
        question_length.append(len(query_word_list))
        passages_list = file_dict_temp['passages']
        for item in passages_list:
            item_passage_text_temp = item['passage_text']
            item_label = item['label']
            item_passage_text_temp_1 = re.sub(r1," " ,item_passage_text_temp)
            item_passage_text_temp_word_list = get_words(item_passage_text_temp_1)
            for word in item_passage_text_temp_word_list:
                if word in stop_words_list or word == 'br' or word == ' ' or word == '' or word == ' ' or word == '��' or word == u'\u3000' or word in word_delete:
                    item_passage_text_temp_word_list.remove(word)
                else:
                    continue
            write_words_answer('answer',item_passage_text_temp_word_list,line_num,item_label)
            
    f_read.close()
    return question_length
    
def score_calu_BM25(avg_answer_length,answer_temp_length,answer_word_num_dict,question_line_list,answer_temp_word_num_dict,answer_num):
    question_word_score_list = [] #question�еĸ������ʵ�scoreֵ
    k1 = 1.5
    b = 0.75
    answer_word_score_list = []
    for word in question_line_list:
        if word == 'question':
            continue
        else:
            if word in answer_word_num_dict:
                n_qi = int(answer_word_num_dict[word])
            else:
                n_qi = 0
            IDF = np.log((int(answer_num) - n_qi + 0.5)/(n_qi + 0.5))
            if word in answer_temp_word_num_dict:
                f_qi_D = int(answer_temp_word_num_dict[word])
            else:
                f_qi_D = 0
            score_temp = (f_qi_D * (k1 + 1))/(f_qi_D + k1 *(1-b+b*(answer_temp_length/avg_answer_length)))
            score_temp = IDF * score_temp
            answer_word_score_list.append(score_temp)
    answer_score = np.sum(answer_word_score_list)
    return answer_score

def calu_avg_answer_length(answer_length):
    length_sum = 0
    for length in answer_length:
        length_sum = length_sum + length
    avg_length = length_sum/len(answer_length)
    return avg_length
    
def calu_answer_score(question_num,word_delete):
    answer_score_label_dir = '/home/dcd-qa/MLT_code/BM25/data/answer_score_label/'
    for id in range(question_num):
        file_name = '/home/dcd-qa/MLT_code/BM25/data/question_ansers_words_without_stopwords/' + str(id+1)
        file_read = open(file_name,'rb')
        question_line = file_read.readline()
        question_line_list = question_line.strip().split('\t')
        for word in question_line_list:
            if word in word_delete:
                question_line_list.remove(word)
        #������ڸ�question��Ӧ������answer���б������õ�����answer�и�����һ�����ֵĴ�����dict��Ϊ��IDF��׼��
        answer_word_num_dict = {}
        answer_length = []
        for line in file_read.readlines():
            answer_temp_line_list = line.strip().split('\t')
            answer_length_temp = len(answer_temp_line_list) - 2
            answer_length.append(answer_length_temp)
            word_has_calu = [] #������¼�Ѿ��ڸô��м������Ĵ����֤ÿ������ֻ��һ�����м���һ��
            for index in range(len(answer_temp_line_list)):
                if index < 2:
                    continue
                else:
                    word = answer_temp_line_list[index]
                    if word not in word_has_calu and word not in word_delete:
                        if word not in answer_word_num_dict:
                            answer_word_num_dict[word] = 1
                        else:
                            answer_word_num_dict[word] = answer_word_num_dict[word] + 1
                        word_has_calu.append(word)
                    else:
                        continue
        avg_answer_length = calu_avg_answer_length(answer_length)
        file_read.close()
        file_read = open(file_name,'rb')
        question_line = file_read.readline()
        answer_num = 0
        for line in file_read.readlines():
            answer_temp_line_list = line.strip().split('\t')
            answer_label = answer_temp_line_list[1]
            answer_temp_word_num_dict = {} #�洢��ǰanswer�ĸ���������ֵĴ���
            for index in range(len(answer_temp_line_list)):
                if index < 2:
                    continue
                else:
                    word = answer_temp_line_list[index]
                    if word not in answer_temp_word_num_dict and word not in word_delete:
                        answer_temp_word_num_dict[word] = 1
                    else:
                        answer_temp_word_num_dict[word] = answer_temp_word_num_dict[word] + 1
            answer_score = score_calu_BM25(avg_answer_length,answer_length[answer_num],answer_word_num_dict,question_line_list,answer_temp_word_num_dict,len(answer_length))
            answer_num = answer_num + 1
            file_write_name = answer_score_label_dir + str(id+1)
            file_write = open(file_write_name,'ab+')
            file_write.write(str(answer_label) + '\t' + str(answer_score))
            file_write.write('\n')
            file_write.close()

def calu_DCG(answer_score_file,k):
    #����ʵ��DCG�ļ��㺯��������������������
    answer_index_label_dict = {} #�洢answer_index��label�Ķ�Ӧdict
    answer_index_score_dict = {} #�洢answer_index��score�Ķ�Ӧdict
    #score_answer_index_dict = {} #�洢score��answer_index�Ķ�Ӧdict
    answer_index = 0
    for line in open(answer_score_file,'rb').readlines():
        line_list = line.strip().split('\t')
        label = int(line_list[0])
        score = float(line_list[1])
        answer_index_label_dict[answer_index] = label
        answer_index_score_dict[answer_index] = score
        #score_answer_index_dict[score] = []
        #score_answer_index_dict[score].append(answer_index) #������ֹ���ֶ��answer����ͬscoreֵ�����
        answer_index = answer_index + 1
    answer_index_list = sort_by_value(answer_index_score_dict)
    k_temp = 0
    DCG_result = 0
    for answer_index in answer_index_list:
        if k_temp < k: 
            score = answer_index_score_dict[answer_index]
            label = answer_index_label_dict[answer_index]
            log_num = np.log(k_temp+2)/np.log(2)
            DCG_result = DCG_result + (2**label - 1)/log_num
            k_temp = k_temp + 1
    return DCG_result
            
        
    
def calu_avg_DCG(question_num,k):
    DCG_list = [] #�洢ÿ��question��DCGֵ
    for id in range(question_num):
        answer_score_file = '/home/dcd-qa/MLT_code/BM25/data/answer_score_label/' + str(id+1)
        DCG_temp = calu_DCG(answer_score_file,k)
        DCG_list.append(DCG_temp)
    DCG_avg = calu_avg_answer_length(DCG_list)
    return DCG_avg
    
def get_word_num(question_num,word_num_limit):
    word_num_dict = {}
    for id in range(question_num):
        file_name = '/home/dcd-qa/MLT_code/BM25/data/question_ansers_words_without_stopwords/' + str(id+1)
        file_read = open(file_name,'rb')
        question_line = file_read.readline()
        question_line_list = question_line.strip().split('\t')
        question_line_list.remove('question')
        for word in question_line_list:
            if word not in word_num_dict:
                word_num_dict[word] = 1
            else:
                word_num_dict[word] += 1
        for line in file_read.readlines():
            answer_temp_line_list = line.strip().split('\t')
            answer_label = answer_temp_line_list[1]
            answer_temp_line_list.remove('answer')
            answer_temp_line_list.remove(answer_labe)
            for word in answer_temp_line_list:
                if word not in word_num_dict:
                    word_num_dict[word] = 1
                else:
                    word_num_dict[word] += 1
    word_delete = []
    word_dict_list = sort_by_value(word_num_dict)
    for word in word_dict_list:
        if word_dict[word] > word_num_limit or word_dict[word] < 2:
            word_delete.append(word)
    return word_delete
            
    
def words_statics(question_num,k,word_num_limit):
    #����train_file�е�ÿһ������ͳ��һ�¸���������ֵ�Ƶ�ʣ����ҽ�stop_words_list�еĲ�����ͳ��,���ڳ��ִ����ر��ģ�Ҳ����ȥ����
    #Ȼ���ٰ��մ𰸵�label�ĸߵͣ��������еĴ�ȥ�����Ա������ٽ�ʣ��Ĵʵĳ���Ƶ�ʽ��д洢���洢��һ��json�ļ��У����ļ���ÿһ��Ϊһ���������һ���𰸵Ĵ���ĸ�����
    #��������洢һ���ļ�������������������еĴ𰸵ĸ���
    #question_length = get_word_dict(train_file,stop_words_list)
    word_delete = get_word_num(question_num,word_num_limit)
    calu_answer_score(question_num,word_delete) #�ֱ�������question������answer��scoreֵ�����ҽ�ÿ��question��scoreֵ����Ӧ��labelֵ����һ���ļ���
    DCG_result = calu_avg_DCG(len(question_length),k)
    return DCG_result
    
def main():
    train_file_dir = sys.argv[1]
    train_file_name = sys.argv[2]
    question_num = int(sys.argv[3])
    k = int(sys.argv[4])
    word_num_limit = int(sys.argv[5])
    train_file = os.path.join(train_file_dir,train_file_name)
    #stop_words_list = get_stop_words('/home/dcd-qa/MLT_code/BM25/data/chinese_stopwords.txt')
    DCG_result = words_statics(question_num,k,word_num_limit)
    print 'DCG@' + str(k) + '\t' + str(DCG_result) + '\n'
    
    
if __name__ == '__main__':
    main()