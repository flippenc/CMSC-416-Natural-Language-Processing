# CMSC 416 Spring 2022 
# Professor: Dr. McInnes
# Assignment 3: POS Tagging
# Student: Christopher Flippen
# Due Date: March 15, 2022

# Program concept and usage:
# ##########################
# The 'scorer.py' part of this program takes a file of text which has been tagged by tagger.py 
# as well as a "key" file containing the correct tags for the file in order to determine the accuracy of tagger.py.
# The output of the program is the accuracy of the model along with a confusion matrix.

# The confusion matrix is in the form {predicted: {actual tags}}
# For example:
# 'CC': {'CC' : 1364, 'NN' : 2, 'NNP' : 1, 'RB' : 6}
# Means that when the 'CC' tag was used, it correctly marked 'CC' 1364 times, it was confused with 'NN' 2 times, confused with 'NNP' 1 times, and confused with 'RB' 6 times

# The accuracy of the model is printed below the confusion matrix and states the fraction of tokens correct and the percentage correct.
# For the files given with the assignment with all rules enabled, the accuracy printed is:
# The accuracy of this model is 50552/56824 or 88.96241024919048%

# By default, the output is printed, but may be directed to a file.
# For example: if pos-test-wth-tags.txt is the output from tagger.py and pos-test-key.txt is the "key" file,
# the program may be run with the following command which will output the result to a new file called pos-tagging-report.txt

# py scorer.py pos-test-with-tags.txt pos-test-key.txt > pos-tagging-report.txt

# Program implementation:
#########################
# The program begins by calling scoreFile(sys.argv[1], sys.argv[2])
# sys.argv[1] is the file created by tagger.py and sys.argv[2] is the 'key' file
# scoreFile begins by calling getTokens on both files in order to get lists of all of their tokens
# It then calls getTags on the lists in order to convert the list of tokens into a list of tags

# The function then enters a loop where each pair of tags, tagged[i], key[i] is compared
# If the tags are the same, a counter increments the number of correct tags
# The pairs of tags are also stored in the confusion matrix (stored as a 2D dictionary)
# The confusion matrix dictionary uses similar logic to the tagger dictionary
# confusionMatrix[predictedTag] stores each of the tags which were marked using predictedTag 
# confusionMatrix[predictedTag][keyTag] stores how many times the text was marked using predictedTag when the correct tag was keyTag

# After the function finishes looping through the pairs of tags, the confusion matrix and accuracy of the model are printed
# Accuracy of the model is determined by (number of tags correct)/(total tags)

import pprint as pp
import sys
import re
from collections import defaultdict

# scoreFile opens the tagged file and the key file, gets lists of their tags,
# compares the lists to get the accuracy and the confusion matrix, and prints the results
def scoreFile(tagged, key):
    confusionMatrix = defaultdict(dict)
    # getTokens get a list of the tokens in the file
    taggedTokenList = getTokens(tagged)
    keyTokenList = getTokens(key)
    # tokens in both lists are of the form word/tag
    # getTags turns the word/tag tokens into just tokens
    taggedTokenTags = getTags(taggedTokenList)
    keyTokenTags = getTags(keyTokenList)
    # correct keeps track of how many correct tags are present
    correct = 0
    for i in range(len(taggedTokenTags)):
        predictedTag = taggedTokenTags[i]
        keyTag = keyTokenTags[i]
        if predictedTag == keyTag:
            correct += 1
        try:
            confusionMatrix[predictedTag][keyTag] +=1
        except:
            confusionMatrix[predictedTag][keyTag] = 1
    # print the results
    print(f'Confusion matrix:')
    pp.pprint(confusionMatrix)
    print(f'The accuracy of this model is {correct}/{len(taggedTokenTags)} or {correct/len(taggedTokenTags)*100}%')

# getTokens returns a list of all of the tokens in the file 'tokens'
def getTokens(tokens):
    tokenList = []
    with open(tokens, 'r') as tokenFile:
        for line in tokenFile:
            tokenList.extend(line.split())
    return tokenList

# getTags takes a list of tokens and returns the tags from them
# if a token has a piped list of tags, the first tag is chosen
# if a token has a fraction \/, a regex is used to properly get the tag
def getTags(tokenList):
    tagList = []
    splitRegex = r"[^\\]\/"
    for pair in tokenList:
        # when computing accuracy, we don't want the '[' and ']' characters
        if pair not in ['[',']']:
            # if there is a fraction, use the regex to deal with it
            if '\/' in pair:
                _, tag = re.split(splitRegex, pair)
            # if there isn't a fraction, split normally
            else:
                _, tag = pair.split('/')
            # if the tag has a piped list of tags, take the first tag
            if '|' in tag:
                tag = tag.split('|')[0]
            tagList.append(tag)
    return tagList

if __name__ == "__main__":
    scoreFile(sys.argv[1], sys.argv[2])