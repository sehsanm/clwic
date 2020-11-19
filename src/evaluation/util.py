import os
import fasttext



def head(file_name, n = 500):
    with open(file_name, 'r', encoding='utf8')as f:
        for i in range(n):
            print(f.readline())

def normalize_wiki(line):
    pass


def buid_model(method, dim, w,  corpus_file):

    output_file = '{}_{}_{}_{}.out'.format(os.path.basename(corpus_file).split('.')[0], method, dim , w)
    if os.path.exists(output_file):
        print('Skipping file ' , output_file)
        return

    print('Ready to build ' , output_file)

    model = fasttext.train_unsupervised(model=method, dim=dim, ws=w , input=corpus_file )
    model.save_model(output_file)


def build_combinations(methods, dimensions, window_sizes, corpus_files):
    for m in methods:
        for d in dimensions:
            for w in window_sizes:
                for c in corpus_files:
                    buid_model(m, d ,w, c)

if __name__ == "__main__":
    build_combinations(['cbow' , 'skipgram' ], [ 100, 300, 400] , [3, 5, 10] , ['./data/wiki.txt'] )