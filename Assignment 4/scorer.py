# CMSC 416 Spring 2022 
# Professor: Dr. McInnes
# Assignment 4: Word Sense Disambiguation
# Student: Christopher Flippen
# Due Date: April 5, 2022

import pprint as pp
import sys
import re
from collections import defaultdict

# Program concept and usage:
# ##########################
# The 'scorer.py' part of this program takes a file of text which has been tagged by wsd.py 
# as well as a "key" file containing the correct tags for the file in order to determine the accuracy of wsd.py.
# The output of the program is the accuracy of the model along with a confusion matrix.

# The confusion matrix is in the form {predicted: {actual tags}}
# For example:
#   {'phone': {'phone': 61, 'product': 14},
#    'product': {'phone': 11, 'product': 40}})
# Means that:
# 'phone' was correctly guessed 61 times, 
# 'phone' was incorrectly guessed 14 times when it should have been product,
# 'product' was correctly guessed 40 times, 
# and 'product' was incorrectly guessed 11 times when it should have been 'product

# The accuracy of the model is printed below the confusion matrix and states the fraction of instances correct and the percentage correct.
# For the files given with the assignment, the accuracy printed is:
# The accuracy of this model is 101/126 or 80.15873015873017%
# The "most frequent sense" baseline simply chooses whichever sense was used more frequently in the training data.
# In this case, "product" was the most frequent sense in the training data
# This gave an accuracy statement of:
# The accuracy of this model is 54/126 or 42.857142857142854%

# By default, the output is printed, but may be directed to a file.
# For example: if my-line-answers.txt is the output from wsd.py and pos-test-key.txt is the "key" file,
# the program may be run with the following command

# py scorer.py my-line-answers.txt line-key.txt 

# Program implementation:
#########################
# The program begins by calling scoreFile(sys.argv[1], sys.argv[2])
# sys.argv[1] is the file output by wsd.py and sys.argv[2] is the 'key' file
# scoreFile begins by opening both files and getting the instanceID and sense from each line using a regex
# For each instance, the guessed sense and the key sense are examined and saved to
# confusionMatrix[predictedTag][keyTag]
# If the guess and key sense are the same, the 'correct' variable in incremented
# confusionMatrix[predictedTag] stores each of the tags which were guessed to be sense predictedSense 
# confusionMatrix[predictedTag][keyTag] stores how many times the instance guessed to be sense predictedSense when the correct sense was keyTag

# After the function finishes looping through the pairs of tags, the confusion matrix and accuracy of the model are printed
# Accuracy of the model is determined by (number of tags correct)/(total tags)

# scoreFile takes the output from wsd.py (answers) and the key file (key) and prints the accuracy of answers and a confusion matrix
def scoreFile(answers, key):
    answerData = []
    keyData = []
    confusionMatrix = defaultdict(dict)
    # lineInfo gets the instanceID and senseID from the two files
    lineInfo = r'<answer instance=\"(.*)\" senseid=\"([a-zA-Z]+)\"\/>'
    # answerData stores the [id, guessedSense] pairs from the answers file
    with open(answers, 'r') as answerFile:
        for line in answerFile:
            if re.match(lineInfo, line.strip()):
                data = re.search(lineInfo, line).groups()
                answerData.append((data[0], data[1]))
    # keyData stores the [id, correctSense] pairs from the key file
    with open(key, 'r') as keyFile:
        for line in keyFile:
            if re.match(lineInfo, line.strip()):
                data = re.search(lineInfo, line).groups()
                keyData.append((data[0], data[1]))
    # iterate through the two lists
    correct = 0
    for i in range(len(answerData)):
        # if the guessed sense and key sense are the same, increment correct
        predictedTag = answerData[i][1]
        keyTag = keyData[i][1]
        if predictedTag == keyTag:
            correct += 1
        # update the confusion matrix with the [guessedSense][keySense] pair
        try:
            confusionMatrix[predictedTag][keyTag] +=1
        except:
            confusionMatrix[predictedTag][keyTag] = 1
    # print the results
    print(f'Confusion matrix:')
    pp.pprint(confusionMatrix)
    print(f'The accuracy of this model is {correct}/{len(answerData)} or {correct/len(answerData)*100}%')

if __name__ == "__main__":
    scoreFile(sys.argv[1], sys.argv[2])