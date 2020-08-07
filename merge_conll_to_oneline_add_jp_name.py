#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
from __future__ import print_function
from __future__ import division
import argparse
import random

parser = argparse.ArgumentParser(description='merge_conll_to_oneline.py')

##
## **Preprocess Options**
##
parser.add_argument('-input_file', required=True,
                    help="Path to the training data")
parser.add_argument('-output_file', required=True,
                    help="Path to the output")
parser.add_argument('-augment_jp_name', action='store_true',  default=False, 
                    help="Augment Japanese person names")
# parser.add_argument('-want_type', default='per',
#                     help="What kind of label to show")
opt = parser.parse_args()

def makeData(filename):
    src, tgt = [], []
    pos_instances = dict()
    outputs = []
    sent_count = 0
    line_num = 0
    print('Processing file %s...' % (filename))
    with open(filename) as inputFile:
        for oneline in inputFile.readlines():
            line_num += 1
            oneline = oneline.rstrip()
            if len(oneline) < 1:
                if len(src) > 0:
                    outputs.append((src, tgt))
                    sent_count += 1
                    if sent_count % 10000 == 0:
                        print('... %d sentences read' % sent_count)
                    src = []
                    tgt = []
                    continue
            oneline = oneline.split('\t')
            if len(oneline) != 2:
                print("Error on line %d, length not 2." % (line_num))
                continue
            srcWords = oneline[0]
            tgtWords = oneline[1]
            src.append(srcWords)
            tgt.append(tgtWords)
            pos_instance = pos_instances.get(tgtWords, [])
            pos_instance.append(srcWords)
            pos_instances[tgtWords] = pos_instance
    return outputs, pos_instances

def join_words_pos(words, poss):
    joined_words = "".join(words)
    joined_pos = ""
    for w_id, word in enumerate(words):
        pos_tag = poss[w_id]
        if pos_tag.lower() not in ["per", "loc", "org"]:
            pos_tag = "N-{}".format(pos_tag)
        if len(word) == 1:
            joined_pos += 'S-{} '.format(pos_tag)
            continue
        if len(word) == 2:
            joined_pos += 'B-{0} E-{0} '.format(pos_tag)
            continue
        joined_pos += 'B-{} '.format(pos_tag)
        for i in range(len(word)-2):
            joined_pos += 'I-{} '.format(pos_tag)
        joined_pos += 'E-{} '.format(pos_tag)
    joined_pos = joined_pos.strip()
    return joined_words, joined_pos

def replace_with_jp_name(words, poss):
    ret_words = []
    for w_id, word in enumerate(words):
        newword = word
        if poss[w_id].lower() == "per":
            newword = u"{}{}".format(random.choice(jp_last_names), random.choice(jp_first_names))
        ret_words.append(newword)
    return ret_words

def main():
    sents, pos_instances = makeData(opt.input_file)
    sent_count = 0
    with open(opt.output_file, 'w') as ofile:
        for sent in sents:
            sent_count += 1
            # if sent_count > 3: exit()
            words, poss = sent
            joined_words, joined_pos = join_words_pos(words, poss)
            ofile.write(joined_words)
            ofile.write('\t')
            ofile.write(joined_pos)
            ofile.write('\n')
            # augment JP names randomly
            if opt.augment_jp_name and \
                    any(x.lower() == "per" for x in poss):
                new_words = replace_with_jp_name(words, poss)
                joined_words, joined_pos = join_words_pos(new_words, poss)
                ofile.write(joined_words)
                ofile.write('\t')
                ofile.write(joined_pos)
                ofile.write('\n')
                sent_count += 1
            if sent_count % 10000 == 0:
                print("Output sentence {}".format(sent_count))
        print("Output sentence {}".format(sent_count))
    # want_type = opt.want_type
    # all_data = {}
    # all_data['src'], all_data['tgt'], all_data['sizes'] = makeData(opt.input_file)
    # found_words = set()
    # linenum = 0
    # for i in range(len(all_data['tgt'])):
    #     linenum += 1
    #     assert len(all_data['tgt'][i]) == len(all_data['src'][i]), "Line %s length mismatch" % linenum
    #     for c in range(len(all_data['tgt'][i])):
    #         if want_type in (all_data['tgt'][i][c]).lower():
    #             # print (linenum)
    #             found_words.add(all_data['src'][i][c])
    # for w in found_words:
    #     print(w, end=' ')

if __name__ == "__main__":
    # jp_first_names = [n.strip() for n in open('JP_first_name.txt').readlines()]
    # jp_last_names = [n.strip() for n in open('JP_last_name.txt').readlines()]
    main()
