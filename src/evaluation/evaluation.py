import scipy
import numpy as np
from numpy import random

from scipy.spatial.distance import cosine

class Question:
    def __init__(self, category, question, options, answer):
        self.category = category
        self.question = question
        self.options = options
        self.answer = answer

    def __str__(self):
        ret = self.category + '\n'
        ret += str(self.question) + '\n'
        for o in self.options:
            ret += str(o) + '\n'
        ret += str(self.answer)
        return ret


class Result:
    def __init__(self):
        self.total = 0
        self.correct = 0

    def add(self, correct):
        self.total += 1
        if correct:
            self.correct += 1

    def get_accuracy(self):
        return self.correct / self.total

def load_analogy(file_name):
    """Loads the analogy dataset as a CSV file
    and returns a list of 5 element tuples (cat, word_1, word_2 , word_3, word_4)"""
    dataset = []
    with open(file_name, "r", encoding='UTF-8') as input_file:
        line = input_file.readline()
        while line:
            line = line.strip('\r\t\n ')
            parts = line.split(',')
            if len(parts) == 5:
                dataset.append((parts[0], parts[1], parts[2], parts[3], parts[4]))
            line = input_file.readline()
    print(len(dataset) , ' Analogy entries loaded from ' , file_name)
    return dataset


def sort_similarity(model, word_1, word_2, word_3):
    """Check the analogy """
    knn = find_knn(model.get_word_vector(word_3) + model.get_word_vector(word_2) - model.get_word_vector(word_1)
                   , model.get_vectors(), 'c')
    return knn


def run_analogy(model, analogy_dataset, tol=10):
    print('Running Analogy Test for :' , len(analogy_dataset))
    total_result  = Result()
    category_result = {}
    rand_ind = list(range(len(analogy_dataset)))
    random.shuffle(rand_ind)
    cnt = 0
    for r_ind in rand_ind:
        cnt = cnt + 1
        if cnt > 5000:
            break
        item = analogy_dataset[r_ind]

        if item[0] not in category_result:
            category_result[item[0]] = Result()

        try:

            knn = sort_similarity(model, item[1], item[2], item[3])
            loc = np.where(knn == model.get_word_index(item[4]))[0][0]

            if loc < tol:
                #print('Perfect ' + item[1] + ' to ' + item[2] + ' is like ' + item[3] + ' to ' + item[4])
                total_result.add(True)
                category_result[item[0]].add(True)
            else:
                #print('Failed for: ' + item[1] + ' to ' + item[2] + ' is like ' + item[3] + ' to ' + item[4],
                #      ', AnswerIndex:', loc, ' Top ', [model.get_word_in_index(index) for index in knn[0:tol]])
                total_result.add(False)
                category_result[item[0]].add(False)

        except:
            total_result.add(False)
            category_result[item[0]].add(False)
        if  cnt % 50 == 0:
            print('Accuracy so far(',cnt , '):', total_result.get_accuracy())
    return total_result, category_result


def cosine_dist(word_vec, embed_vec):
    return cosine(word_vec, embed_vec)


def euclid_dist(word_vec, embed_vec):
    return np.linalg.norm(word_vec - embed_vec)


def find_knn(word_vec, embedding_matrix, distance_method='c'):
    """Each row of the embedding matrix is the vector representation of words"""

    dists = []

    if distance_method == 'c':
        dists = 1 - np.dot(embedding_matrix, word_vec) / (
                    np.linalg.norm(embedding_matrix, axis=1) * np.linalg.norm(word_vec))

    return np.argsort(dists)


if __name__ == "__main__":
    pass


def find_pair_distances(model, question, options, distance_method='c'):
    q_vec = get_vector(model, question[0]) - \
            get_vector(model, question[1])

    option_distances = []

    for o in options:
        o_vec = get_vector(model, o[0]) - \
                get_vector(model,  o[1])
        if distance_method == 'c':
            option_distances.append(cosine_dist(q_vec, o_vec))
    return option_distances


def get_vector(model, word):
    if not model.word_exist(word):
        raise Exception('Cannot find vector for:' + word)
    return model.get_word_vector(word)


def print_closest(vec, embedding_matrix, rev_index, top_n):
    knn = find_knn(vec, embedding_matrix, 'e')
    for x in range(top_n):
        print('\t' + rev_index[knn[x]], '\t', cosine_dist(vec, embedding_matrix[knn[x]][:]))


def evaluate_sat(model, questions):
    print('Loading model')

    category_result = {}
    total_result = Result()
    for q in questions:
        #print(q)
        if q.category not in category_result:
            category_result[q.category] = Result()

        try:
            distances = find_pair_distances(model, q.question, q.options)
            #print(distances)
            guess = np.argmin(distances) + 1
            #print('My guess answer:', guess)
            category_result[q.category].add(guess == q.answer)
            total_result.add(guess == q.answer)
        except Exception as e:
            #print('Skipped:', e)
            category_result[q.category].add(False)
            total_result.add(False)
    print('SAT Accuracy:', total_result.get_accuracy())
    return total_result, category_result


def load_sat_questions(file_name, option_count=5):
    ret = []
    with open(file_name, 'r', encoding='utf8') as f:
        cat = next_line(f)
        while cat:
            question = next_line(f).split(',')
            options = []
            for i in range(option_count):
                options.append(next_line(f).split(','))
            answer = int(next_line(f))
            ret.append(Question(cat, question, options, answer))
            next_line(f)
            cat = next_line(f)
    print(len(ret), ' Questions Loaded')
    return ret


def next_line(f):
    ret = f.readline()
    if ret:
        ret = ret.strip()
    return ret


