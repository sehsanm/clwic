import json



def calculate_entry_result(entry):
    total = 0
    correct = 0
    for i in range(len(entry['answers'])):
        total += 1
        #print(int(entry['answers'][i]) + 1 , ' vs ' , entry['questions'][i]['original_question']['correct_option']['$numberInt'])
        if int(entry['answers'][i]) + 1  == int(entry['questions'][i]['original_question']['correct_option']['$numberInt']):
            correct += 1

    return correct/total


def print_category_confusion(entry):
    total = 0
    correct = 0
    for i in range(len(entry['answers'])):
        total += 1
        #print(int(entry['answers'][i]) + 1 , ' vs ' , entry['questions'][i]['original_question']['correct_option']['$numberInt'])
        if int(entry['answers'][i]) + 1  != int(entry['questions'][i]['original_question']['correct_option']['$numberInt']) and int(entry['answers'][i]) <= 4:
            print(entry['questions'][i]['original_question']['question']['cat_name'], ',' , entry['questions'][i]['original_question']['options'][ int(entry['answers'][i]) ]['cat_name'])


if __name__ == "__main__":
        
    with open('../../data/human_voting.json', "r" ,  encoding="utf8") as json_file:
        data = json.load(json_file)
        for entry in data:
            # print(entry)
            #print(calculate_entry_result(entry))
            print_category_confusion(entry)