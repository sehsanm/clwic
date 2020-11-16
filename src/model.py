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
