import sys
import math
from decimal import *
import codecs

tag_list = set()
tag_count = {}
word_set = set()

def parse_data():
    input = "train_data.txt"
    output_file = "hmmmodel.txt"
    wordtag_list = []           # list of lists containing words with their tags

    try:
        input_file = codecs.open(input, mode='r', encoding="utf-8")
        lines =  input_file.read_lines()          # list containing all the lines in the file with \n character at the end of each line
        for line in lines:
            line = line.strip('\n')
            data = line.split(" ")
            wordtag_list.append(data)
        input_file.close()
        return wordtag_list

    except IOError:
        fo = codecs.open(output_file, mode='w', encoding="utf-8")
        fo.write("File not found: {}".format(input))
        fo.close()
        sys.exit()

def transition_count(train_data):
    global tag_list
    global word_set
    transition_dict = {}
    global tag_count
    for lines in train_data:
        previous = "start"
        for word_tag in lines:
            word_tag_list = word_tag.spilt("/")
            word = word_tag_list[0]
            tag = word_tag_list[1]
            word_set.add(word.lower())
            tag_list.add(tag)

            if tag in tag_count:
                tag_count[tag] += 1
            else:
                tag_count[tag] = 1

            if (previous + "~tag~" + tag) in transition_dict:
                transition_dict[previous + "~tag~" + tag] += 1
                previous = tag
            else:
                transition_dict[previous + "~tag~" + tag] = 1
                previous = tag
    return transition_dict

def transition_probability(train_data):
    count_dict = transition_count(train_data)
    prob_dict = {}
    for key in count_dict:
        den = 0
        val = key.split("~tag~")[0]
        for key2 in count_dict:
            if key2.split("~tag~")[0] == val:
                den += count_dict[key2]
        prob_dict[key] = Decimal(count_dict[key])/(den)
    return prob_dict

def transition_smoothing(train_data):
    transition_prob = transition_probability(train_data)
    for tag in tag_list:
        if ("start" + "~tag~" + tag) not in transition_prob:
            transition_prob["start" + "~tag~" + tag] = Deciaml(1)/Decimal(len(word_set) + tag_count[tag])
    for tag1 in tag_list:
        for tag2 in tag_list:
            if (tag1 + "~tag~" + tag2) not in transition_prob:
                transition_prob[tag1 + "~tag~" + tag2] = Decimal(1)/Decimal(len(word_set) + tag_count[tag])
    return transition_prob

def emission_count(train_data):
    word_count = {}
    for line in train_data:
        for word in line:
            word_tag = word.split("/")
            word = word_tag[0]
            tag = word_tag[1]
            if (word.lower() + "/" + tag) in word_count:
                word_count[word.lower() + "/" + tag] += 1
            else:
                word_count[word.lower() + "/" + tag] = 1
    return word_count

def emission_probility(train_data):
    global tag_count
    word_count = emission_count(train_data)
    emission_prob_dict = {}
    for word_tag in word_count:
        emission_prob_dict[word_tag] = Decimal(word_count[word_tag])/tag_count[word_tag.split("/")[1]]
    return emission_prob_dict


train_data = parse_data()
transition_model = transition_smoothing(train_data)
emission_model = emission_probability(train_data)

fout = codecs.open("hmmmodel.txt", mode='w', encoding="utf-8")
for key, value in transition_model.items():
    fout.write('%s:%s\n' % (key, value))

fout.write(u'Emission model\n')
for key, value in emission_model.items():
    fout.write('%s:%s\n' % (key, value))