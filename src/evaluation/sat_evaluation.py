import  model
import evaluation
import numpy as np
import xlsxwriter as xlsxwriter


def store_in_excel(result, file_name):
    workbook = xlsxwriter.Workbook(file_name)

    for k in result.keys():
        worksheet = workbook.add_worksheet(k)
        worksheet.write(0, 0, 'Category')
        worksheet.write(0, 1, 'Total')
        worksheet.write(0, 2, 'Correct')
        cats = list(result[k].keys())
        cats.sort()
        for i in range(len(cats)):
            worksheet.write(i + 1, 0, cats[i])
            worksheet.write(i + 1, 1, result[k][cats[i]].total)
            worksheet.write(i + 1, 2, result[k][cats[i]].correct)
        last = len(cats) + 1
        worksheet.write(last , 0 , 'SUM')
        worksheet.write(last , 1 , '=SUM(B2:B' + str(last) + ')')
        worksheet.write(last , 2 , '=SUM(C2:C' + str(last) + ')')
    workbook.close()


if __name__ == "__main__":

    questions = evaluation.load_sat_questions('../../data/analogy/sat_analogy.txt')
    model_wiki = model.FastTextModel('../../data/twitter_cbow_100_5.out')
    print(evaluation.evaluate_sat(model_wiki, questions)[0].get_accuracy())
