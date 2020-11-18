from muse.utils import load_embeddings 
from  collections import namedtuple

from  transformers  import XLMRobertaModel, AutoTokenizer
import torch

import argparse

def extract_dictionary(dictionary , output_file):
    with open(output_file, 'w' , encoding='utf8') as f: 
        for i in range(len(dictionary)): 
            f.write(dictionary[i] + '\r\n')
    

def load_simple_embedding(file_name, lang, emb_dim):
    Params = namedtuple('Params' , 'src_emb src_lang emb_dim max_vocab cuda')
    params_dc = Params(file_name, lang, emb_dim , 3000000 , False)

    return load_embeddings(params_dc , True)

def  step_1(): 
    """
        This method builds  token dictionaries  for multiple languages. 
    """

    dico, embedding = load_simple_embedding('data/models/blogs_skipgram_300_3.bin' , 'fa' , 300)
    extract_dictionary(dico , 'data/common/fa.txt')
    dico, embedding = load_simple_embedding('data/models/crawl-300d-2M.vec' , 'en' , 300)
    extract_dictionary(dico , 'data/common/en.txt')


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

    build_embedding(model, tokenizer , 768 , 'data/common/en.txt' , 'data/common/en-678-xlmroberta.vec')
    build_embedding(model, tokenizer , 768 , 'data/common/fa.txt' , 'data/common/fa-678-xlmroberta.vec')

def build_embedding(model, tokenizer , model_dim , dictionary_file , output_file): 
    print('Processing file ' , dictionary_file)
    dictionary = [] 
    with open(dictionary_file , 'r' , encoding='utf8') as f: 
        token = f.readline() 
        while token:
            dictionary.append(token) 
            token = f.readline().strip()  
    print(len(dictionary) , ' Tokens detected')
    with open(output_file , 'w' , encoding='utf8') as out: 
        out.write(str(len(dictionary)) +  ' ' + str(model_dim) + '\r\n') 
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
            out.write('\r\n') 

            


if __name__ == '__main__' : 
    parser = argparse.ArgumentParser(description='Preprocessing Data')
    parser.add_argument("--step", type=int, default=2 , help="Processing Step to be applied")


    # parse parameters
    params = parser.parse_args()

    if params.step == 1:
        step_1() 
    elif params.step == 2:
        step_2() 

