
import re 

def build_most_freq_tokens(corpus_file ,  token_count): 
    dico = {}
    with open(corpus_file, 'r' , encoding='utf8') as f: 
        for i, line in enumerate(f):
            tokens = list(filter(None, re.split(';|\,|\s|\.|\?|\!|\؟' , line.strip())))
            for token in tokens: 
                if token in dico:
                    dico[token] += 1 
                else: 
                    dico[token] = 1 
    srt = sorted(dico.items() , key= lambda i: i[1] , reverse=True) 
    ret = []
    for i in range(token_count): 
        ret.append(srt[i][0])
    return ret 


def extract_dictionary(lst , output_file):
    with open(output_file, 'w' , encoding='utf8') as f: 
        for i in range(len(lst)): 
            f.write(lst[i] + '\n')

