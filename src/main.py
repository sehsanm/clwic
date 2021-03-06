from muse.utils import load_embeddings 
from  collections import namedtuple
import  preprocess as prep
from  transformers  import XLMRobertaModel, AutoTokenizer
import torch
import numpy as np 
import argparse

import re 

def build_most_freq_tokens(corpus_file ,  token_count): 
    dico = {}
    total_tokens = 0 
    with open(corpus_file, 'r' , encoding='utf8') as f: 
        for i, line in enumerate(f):
            tokens = list(filter(None, re.split(';|\,|\s|\.|\?|\!|\؟' , line.strip())))
            for token in tokens: 
                if token in dico:
                    dico[token] += 1 
                else: 
                    dico[token] = 1 
                total_tokens += 1 
    srt = sorted(dico.items() , key= lambda i: i[1] , reverse=True) 
    ret = []
    selected_tokens = 0 
    for i in range(token_count):
        selected_tokens += srt[i][1] 
        ret.append(srt[i][0])
    print ('Total token {}  we selected {}  which is {} percent'.format(total_tokens, selected_tokens,  selected_tokens / total_tokens * 100))
    return ret 

def extract_dictionary(lst , output_file):
    with open(output_file, 'w' , encoding='utf8') as f: 
        for i in range(len(lst)): 
            f.write(lst[i] + '\n')


def create_mean_vectors(top_word_file , corpus_file , output_file , model , tokenizer , line_count = 10000 ):
    dico = {}
    dico_count = {} 
    with open(top_word_file, 'r' , encoding='utf8') as f: 
        for i, line in enumerate(f):
            dico_count[line.strip()] =  0
            dico[line.strip()] = np.zeros([768])


    with open(corpus_file, 'r' , encoding='utf8') as f: 
        found = 0 
        not_found = 0 
        for i, line in enumerate(f):
            if i > line_count:
                break

            tokens = tokenizer(line)
            lst = tokenizer.convert_ids_to_tokens(tokens['input_ids']) 
            
            input_ids = torch.tensor(tokens['input_ids']).unsqueeze(0)  
            outputs = model(input_ids)

            #print ('Line:',  line )
            #print('Tokens:' , lst)

            for ind , item in enumerate(lst): 
                if item == '<s>' or item == '</s>':
                    continue 
                else: 
                    item = item.replace('▁' , '') 
                    #print(item)

                    if item in dico_count: 
                        found += 1 
                        dico_count[item] += 1 
                        dico[item] += outputs[0][0, ind , : ].detach().numpy() 
                    else:
                        not_found += 1 
            if i % 100 == 1:
                print('Found {} not found {}  Success Rate: {}'.format(found, not_found ,  found / (found + not_found)))

    non_zero = 0 
    for t, c in dico_count.items():
        if c > 0: 
            non_zero += 1 
    with open(output_file , 'w' , encoding='utf8') as out: 
        out.write(str(non_zero) +  ' ' + str(768) + '\n') 
        for token in dico: 
            if dico_count[token] > 0:
                out.write(token + ' ')
                for x in (dico[token] / dico_count[token]).tolist(): 
                    out.write('{:.4f} '.format(x)) 
                out.write('\n') 
    


    



    


def load_simple_embedding(file_name, lang, emb_dim):
    Params = namedtuple('Params' , 'src_emb src_lang emb_dim max_vocab cuda')
    params_dc = Params(file_name, lang, emb_dim , 3000000 , False)

    return load_embeddings(params_dc , True)

def  step_1(): 
    """
        This method builds  token dictionaries  for multiple languages. 
    """

    dico, embedding = load_simple_embedding('data/models/blogs_skipgram_300_3.bin' , 'fa' , 300)
    prep.extract_dictionary(dico , 'data/common/fa.txt')
    dico, embedding = load_simple_embedding('data/models/crawl-300d-2M.vec' , 'en' , 300)
    prep.extract_dictionary(dico , 'data/common/en.txt')


def  step_2():
    """
    This step we load a  model and unify  embeddings - In this case we want to load XLMR as base 
    """
    #print(pipeline('sentiment-analysis')('I was expected to be amazed but no'))
    tokenizer = AutoTokenizer.from_pretrained('xlm-roberta-base')
    model = XLMRobertaModel.from_pretrained('xlm-roberta-base')

    # tokens = tokenizer.encode("Hello") 
    # print (tokenizer.decode(tokens))
    # input_ids = torch.tensor(tokens).unsqueeze(0)  # Batch size 1
    # print(input_ids.shape)
    # outputs = model(input_ids)
    # last_hidden_states = outputs[0]  # The last hidden-state is the first element of the output tuple    
    # print(last_hidden_states.shape)

    #build_embedding(model, tokenizer , 768 , 'data/common/fa.txt' , 'data/common/fa-768-xlmroberta.vec')
    #build_embedding(model, tokenizer , 768 , 'data/common/en.txt' , 'data/common/en-768Schuster2019cross-xlmroberta.vec')

    create_mean_vectors('../data/common/fa-top.txt' , '../data/common/blogs-100K.txt', '../data/commom/fa-mean.vec' , model , tokenizer)

def build_embedding(model, tokenizer , model_dim , dictionary_file , output_file): 
    print('Processing file ' , dictionary_file)
    dictionary = [] 
    with open(dictionary_file , 'r' , encoding='utf8') as f: 
        token = f.readline().strip()  
        while token:
            dictionary.append(token) 
            token = f.readline().strip()  
    print(len(dictionary) , ' Tokens detected')
    with open(output_file , 'w' , encoding='utf8') as out: 
        out.write(str(len(dictionary)) +  ' ' + str(model_dim) + '\n') 
        cnt = 0 
        for token in dictionary: 
            cnt += 1 
            if cnt % 1000 == 0 :
                print (cnt , ' Tokens Processed')
            out.write(token + ' ' ) 
            tokens = tokenizer.encode(token) 
            
            input_ids = torch.tensor(tokens).unsqueeze(0)  # Batch size 1
            outputs = model(input_ids)
            last_hidden_states = outputs[0]  # The last hidden-state is the first element of the output tuple    
            for x in torch.flatten(last_hidden_states[0 , 1 , :]).tolist(): 
                out.write('{:.4f} '.format(x)) 
            out.write('\n') 

            




if __name__ == '__main__' : 
    parser = argparse.ArgumentParser(description='Preprocessing Data')
    parser.add_argument("--step", type=int, default=2 , help="Processing Step to be applied")


    # parse parameters
    params = parser.parse_args()

    if params.step == 1:
        step_1() 
    elif params.step == 2:
        step_2() 

