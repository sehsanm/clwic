import gensim
import fasttext
import numpy as np


class Model:

    def get_word_vector(self, word):
        raise Exception('Cannot load word', word)

    def word_exist(self, word):
        return None

    def get_vectors(self):
        return None

    def get_word_in_index(self, index):
        return None

    def get_word_index(self, word):
        return None

class TextModel(Model):

    def __init__(self, file_name):
        self.word2id = {}
        self.id2word = [] 
        with open(file_name, 'r', encoding='utf-8', newline='\n', errors='ignore') as f:
            for i, line in enumerate(f):
                if i == 0:
                    split = line.split()
                    print(split)
                    self._emb_dim_file = int(split[1])
                    self.vectors = np.ndarray( (int(split[0]), self._emb_dim_file) )
                    
                else:
                    word, vect = line.rstrip().split(' ', 1)
                    word = word.lower()
                    vect = np.fromstring(vect, sep=' ')
                    if np.linalg.norm(vect) == 0:  # avoid to have null embeddings
                        vect[0] = 0.01
                    self.word2id[word] = i - 1 
                    self.id2word.append(word)
                    self.vectors[i - 1] [:] = vect 


    def get_word_vector(self, word):
        return self.vectors[self.word2id[word]]

    def word_exist(self, word):
        return word in self.word2id

    def get_vectors(self):
        return self.vectors

    def get_word_in_index(self, index):
        return self.id2word[index]

    def get_word_index(self, word):
        return self.word2id[word] 


            


class Word2VecModel(Model):

    def __init__(self, file_name, binary=True):
        if binary:
            self.model = gensim.models.KeyedVectors.load_word2vec_format(file_name, binary=True)
        else:
            self.model = gensim.models.Word2Vec.load(file_name).wv

    def get_word_vector(self, word):
        return self.model.get_vector(word)

    def word_exist(self, word):
        return word in self.model.vocab

    def get_vectors(self):
        return self.model.vectors

    def get_word_in_index(self, index):
        return self.model.index2word[index]

    def get_word_index(self, word):
        return self.model.vocab[word].index


class FastTextModel(Model):

    def __init__(self, file_name):
        self.model = fasttext.load_model(file_name)
        self.w2ind = {}

        self.vectors = np.ndarray((len(self.model.get_words(False , 'surrogateescape')), len(self.model[self.model.get_words(False, 'surrogateescape')[0]])))
        ind = 0
        for w in self.model.get_words(False , 'surrogateescape'):
            try:
                self.vectors[ind][:] = self.model[w]
                self.w2ind[w] = ind
                ind += 1
            except Exception:
                print('ignoring!')


    def get_word_vector(self, word):
        return self.model[word]

    def word_exist(self, word):
        return True

    def get_vectors(self):
        return self.vectors

    def get_word_in_index(self, index):
        return self.model.words[index]

    def get_word_index(self, word):
        return  self.w2ind[word]


def load_model(file_name, binary):
    if binary:
        model = gensim.models.KeyedVectors.load_word2vec_format(file_name, binary=True)
    else:
        model = gensim.models.Word2Vec.load(file_name).wv

    return model
