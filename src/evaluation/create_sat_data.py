import random
import json

def read_file(file_name):
    ret = []
    with open(file_name, "r", encoding="utf8") as f:
        l = f.readline()
        while l:
            l = f.readline()  # ignoring first line
            ret.append(l.split(','))
    return ret


def build_category_map(rows):
    temp = {}
    for r in rows:
        if len(r) >= 4 and len(r[1]) > 0 and len(r[2]) > 0 and len(r[3]) > 0:
            if r[1] not in temp:
                temp[r[1]] = []
            temp[r[1]].append((r[2].strip(), r[3].strip()))
    ret = {}
    #remove elements that their size is less than 2
    for k in temp.keys():
        if len(temp[k]) >= 2:
            ret[k] = temp[k]

    return ret


def select_random(list , forbiddden =[]):
    assert len(list) > len(forbiddden)
    index = random.randrange(len(list))
    while index in forbiddden:
        index = random.randrange(len(list))
    return index

def get_json_obj(cat_ind , cat_name , ind , pair):
    return {'w0': pair[0],
               'w1' : pair[1],
               'ind' : ind,
               'cat_name' : cat_name}


def buid_analogy_question_set(file_name ,  cat_map, question_count, option_count=5):
    with open(file_name + '.txt', 'w' , encoding='utf8') as f:
        cat_list = list(cat_map.keys())
        j_questions = []

        for i in range(question_count):
            j_question = {}
            cat_ind = select_random(cat_list)


            f.write(cat_list[cat_ind] + '\n')
            question_ind = select_random(cat_map[cat_list[cat_ind]], [] )
            answer_ind = select_random(cat_map[cat_list[cat_ind]] , [question_ind])
            j_question['question'] = get_json_obj(cat_ind,
                                               cat_list[cat_ind],
                                               question_ind,
                                               cat_map[cat_list[cat_ind]][question_ind])

            detractors = []
            detractor_cats = [cat_ind]
            j_question['options'] = []
            for j in range(option_count-1):
                next_cat_index = select_random(cat_list, detractor_cats)
                detractor_cats.append(next_cat_index)
                pair_ind = select_random(cat_map[cat_list[next_cat_index]])
                detractors.append(cat_map[cat_list[next_cat_index]][pair_ind])
                j_question['options'].append(get_json_obj(next_cat_index,
                                                          cat_list[next_cat_index],
                                                          pair_ind,
                                                          detractors[-1]))
            answer_loc = random.randrange(option_count)
            j_question['correct_option'] = answer_loc + 1

            detractors.insert(answer_loc, cat_map[cat_list[cat_ind]][answer_ind])
            j_question['options'].insert(answer_loc , get_json_obj(
                cat_ind, cat_list[cat_ind], answer_ind , cat_map[cat_list[cat_ind]][answer_ind]
            ))

            detractors.insert(0, cat_map[cat_list[cat_ind]][question_ind])


            print(detractors)
            for d in detractors:
                f.write(d[0] + ',' + d[1] + '\n')
            f.write(str(answer_loc+1) + '\n\n')
            j_questions.append(j_question)
        json.dump(j_questions , open(file_name + '.json' , 'w', encoding='utf8'),ensure_ascii=False )


if __name__ == "__main__":
    rows = read_file('../../data/analogy/SAT_ANALOGY.csv')
    cat_map = build_category_map(rows)
    buid_analogy_question_set('../../data/analogy/sat_analogy_1' , cat_map , 1000)
    print(cat_map)
