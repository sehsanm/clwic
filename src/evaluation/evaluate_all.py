import os
import pickle

import evaluation
from model import FastTextModel
import xlsxwriter as xlsxwriter

from os.path import isfile, join


SLANG = 'Slang'

ANALOGY = 'Analogy'

SAT = 'SAT'


class ModelData:
    def __init__(self, file, corpus, method, dimension, window):
        self.file = file
        self.corpus = corpus
        self.method = method
        self.dimension = dimension
        self.window = window
        self.results = {}

    def add_result(self, test, result):
        self.results[test] = result


def load_all_models(path):
    ret = []
    for file in os.listdir(path):
        if isfile(join(path, file)) and file.endswith('.out'):
            splits = file.split('.')[0].split('_')
            if len(splits) == 4:
                ret.append(ModelData(join(path, file), splits[0], splits[1], splits[2], splits[3]))
            else:
                print('Skipping ', file)

    return ret


def load_model(model_data):
    print('Loading data file:', model_data.file)
    if model_data.method in ['skipgram', 'cbow']:
        return FastTextModel(model_data.file)


def export_to_excel(output_file, models):
    workbook = xlsxwriter.Workbook(output_file)
    worksheet = workbook.add_worksheet('All models')
    worksheet.write(0, 0, 'Corpus')
    worksheet.write(0, 1, 'Method')
    worksheet.write(0, 2, 'Dimension')
    worksheet.write(0, 3, 'Window')
    worksheet.write(0, 4, 'SAT')
    worksheet.write(0, 5, 'Analogy')
    worksheet.write(0, 6, 'Slang')
    for i in range(len(models)):
        worksheet.write(i + 1, 0, models[i].corpus)
        worksheet.write(i + 1, 1, models[i].method)
        worksheet.write(i + 1, 2, models[i].dimension)
        worksheet.write(i + 1, 3, models[i].window)
        if SAT in models[i].results:
            worksheet.write(i + 1, 4, models[i].results[SAT][0].get_accuracy())
        if ANALOGY in models[i].results:
            worksheet.write(i + 1, 5, models[i].results[ANALOGY][0].get_accuracy())
        if SLANG in models[i].results:
            worksheet.write(i + 1, 6, models[i].results[SLANG][0].get_accuracy())
    workbook.close()


def write_to_temp_file(processed, file_name):
    with open(file_name, 'w', encoding='utf8') as temp_file:
        for p in processed:
            temp_file.write(p + '\n')


def load_from_temp_file(file_name):
    ret = []
    with open(file_name, 'r', encoding='utf8') as temp_file:
        l = temp_file.readline()
        while l:
            if len(l.strip()) > 0:
                ret.append(l.strip())
            l = temp_file.readline()
    return ret


if __name__ == "__main__":
    data_tmp = 'dump.tmp'
    if os.path.exists(data_tmp):
        all_models = pickle.load(open(data_tmp , 'rb'))
    else:
        all_models = load_all_models('../../../')
    sat_questions = evaluation.load_sat_questions('../../data/analogy/sat_analogy.txt')
    analogy_normal = evaluation.load_analogy('../../data/analogy/analogy_farsi.csv')
    analogy_slang = evaluation.load_analogy('../../data/analogy/analogy_slang.csv')
    for model_data in all_models:
        # try:
        if SAT in model_data.results and ANALOGY in model_data.results and SLANG in model_data.results:
            print('Skipping file: ', model_data.file, ' Already Processed')
        else:
            model = load_model(model_data)
            model_data.add_result(SAT, evaluation.evaluate_sat(model, sat_questions))
            model_data.add_result(ANALOGY, evaluation.run_analogy(model, analogy_normal, 5))
            model_data.add_result(SLANG, evaluation.run_analogy(model, analogy_slang, 5))

        export_to_excel('../../output.xlsx', all_models)
        pickle.dump(all_models , open(data_tmp , 'wb'))

        # except Exception as e:
        #     print('Skipping file: ', model_data.file, ' Error:', e)
