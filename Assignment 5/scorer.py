# CMSC 416 Spring 2022 
# Professor: Dr. McInnes
# Assignment 5: Twitter Sentiment Analysis
# Student: Christopher Flippen
# Due Date: April 21, 2022

import pprint as pp
import sys
import re
from collections import defaultdict

# Program concept and usage:
# ##########################
# The 'scorer.py' part of this program takes a file of text which has been tagged by sentiment.py 
# as well as a "key" file containing the correct tags for the file in order to determine the accuracy of sentiment.py.
# The output of the program is the accuracy of the model along with a confusion matrix.

# The confusion matrix is in the form {predicted: {actual tags}}
# For example:
#   {'negative': {'negative': 13, 'positive': 11},
#    'positive': {'negative': 59, 'positive': 149}})
# Means that:
# 'negative' was correctly guessed 13 times, 
# 'negative' was incorrectly guessed 11 times when it should have been positive,
# 'positive' was correctly guessed 149 times, 
# and 'positive' was incorrectly guessed 59 times when it should have been 'negative'

# The accuracy of the model is printed below the confusion matrix and states the fraction of instances correct and the percentage correct.
# For the files given with the assignment, the accuracy printed is:
# The accuracy of this model is 162/232 or 69.82758620689656%
# The "most frequent sentiment" baseline simply chooses whichever sentiment was used more frequently in the training data.
# In this case, "positive" was the most frequent sentiment in the training data
# This gave an accuracy statement of:
# The accuracy of this model is 160/232 or 68.96551724137932%

# By default, the output is printed, but may be directed to a file.
# For example: if my-sentiment-answers.txt is the output from sentiment.py and sentiment-test-key.txt is the "key" file,
# the program may be run with the following command:

# py scorer.py my-sentiment-answers.txt sentiment-test-key.txt 

# Program implementation:
#########################
# The program begins by calling scoreFile(sys.argv[1], sys.argv[2])
# sys.argv[1] is the file output by sentiment.py and sys.argv[2] is the 'key' file
# scoreFile begins by opening both files and getting the instanceID and sentiment from each line using a regex
# For each instance, the guessed sentiment and the key sentiment are examined and saved to
# confusionMatrix[predictedTag][keyTag]
# If the guess and key sentiment are the same, the 'correct' variable in incremented
# confusionMatrix[predictedTag] stores each of the tags which were guessed to be sentiment predictedSentiment
# confusionMatrix[predictedTag][keyTag] stores how many times the instance guessed to be sentiment predictedTag when the correct tag was keyTag

# After the function finishes looping through the pairs of tags, the confusion matrix and accuracy of the model are printed
# Accuracy of the model is determined by (number of tags correct)/(total tags)

# The scorer program should be run as follows:
# py scorer.py my-sentiment-answers.txt sentiment-test-key.txt

# scoreFile takes the output from wsd.py (answers) and the key file (key) and prints the accuracy of answers and a confusion matrix
def scoreFile(answers, key):
    answerData = []
    keyData = []
    confusionMatrix = defaultdict(dict)
    # lineInfo gets the instanceID and sentiment from the two files
    # <answer instance="621351052047028224" sentiment="negative"/>
    lineInfo = r'<answer instance=\"(.*)\" sentiment=\"([a-zA-Z]+)\"\/>'
    # answerData stores the [id, guessedSentiment] pairs from the answers file
    with open(answers, 'r') as answerFile:
        for line in answerFile:
            if re.match(lineInfo, line.strip()):
                data = re.search(lineInfo, line).groups()
                answerData.append((data[0], data[1]))
    # keyData stores the [id, correctSentiment] pairs from the key file
    with open(key, 'r') as keyFile:
        for line in keyFile:
            if re.match(lineInfo, line.strip()):
                data = re.search(lineInfo, line).groups()
                keyData.append((data[0], data[1]))
    # iterate through the two lists
    correct = 0
    for i in range(len(answerData)):
        # if the guessed sentiment and key sentiment are the same, increment correct
        predictedTag = answerData[i][1]
        keyTag = keyData[i][1]
        if predictedTag == keyTag:
            correct += 1
        # update the confusion matrix with the [guessedSentiment][keySentiment] pair
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