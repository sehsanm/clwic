import evaluation

from model import Word2VecModel,FastTextModel


def test_model(model, test_file):
    data_set = evaluation.load_analogy(test_file)
    evaluation.run_analogy(model,  data_set,  5)


if __name__ == "__main__":
    #model = load_model('../data/hm-blogfa-all-vec-win5-d400-min-2000.bin', True)
    model = FastTextModel('../../data/wiki_cbow_100_5.out')
    #model = load_model('../data/w2v_farsi.model' , False)
    test_model(model, '../../data/analogy/analogy_slang.csv')
    #test_model(model, '../data/analogy_farsi.csv')
    #test_model(model, '../data/analogy_slang.csv')

    print('Model loaded!')
