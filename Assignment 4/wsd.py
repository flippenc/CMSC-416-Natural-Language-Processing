# CMSC 416 Spring 2022 
# Professor: Dr. McInnes
# Assignment 4: Word Sense Disambiguation
# Student: Christopher Flippen
# Due Date: April 5, 2022

# Program concept and usage:
# ###########################
# The 'wsd.py' part of this program implements a Decision List classifier using the bag of words feature representation to perform word sense disambiguation
# The goal of word sense disambiguation is to determine which definition of a word is being used in a given sentence.
# For training this program, data about different senses of the word "line" was used.

# The bag of words feature representation views training instances as "bags of words".
# That is, the words that appear in training instances, except for the headword and tags, are treated as features and the order of words is ignored
# Different bag of words representations use different "windows" around the headword
# In this implementation, all words in an instance are used as features except for the headword and tags (the window is the whole instance)
# Punctuation that appears in features is left in, so the feature "product;" would keep its semicolon
# Capitalization of features is also left in
# Capitalization and punctuation are left unchanged since the accuracy of the test model was slightly higher when they were unchanged

# The "log-likelihood" is calculated to determine how useful each feature is at identifying a word sense
# For example, if the word "exchange-rate" only appears when the word "line" is being used in the "phone" sense, then "exchange-rate" will have a high log-likelihood
# More general words such as "is" appear with multiple senses of the word "line", so "is" has a low log-likelihood
# When determining the sense of a word in an instance, a "feature vector" is created to represent which words appear in the instance
# To determine which sense the headword is, the program "tests" each word in the feature vector to see if it is a word in the model 
# and how high the log-likelihood of the word in the model is.
# The sense associated with the word of highest log-likelihood is the chosen sense
# This process of "testing" each word in the feature vector is called a Decision List

# If multiple words in the feature vector have the same log-likelihood, we choose the sense of whichever word appears more often in the testing instance.
# For example, if "business" and "exchange" both have log-likelihood 3 but "business" appears 3 times in the testing instance while "exchange" only appears 1 time,
# then the program will choose the sense associated with "business" in the model

# The model created by the program is output to a file and the list of senses along with their instance IDs is printed (this can be redirected to a file)
# To run this part of the program with:
#  training data 'line-train.txt', testing data 'line-test.txt', model output file 'my-model.txt', and instance sense, ID pair output file 'my-line-answers.txt',
# the program can be run with the following command:

# py wsd.py line-train.txt line-test.txt my-model.txt > my-line-answers.txt

# When testing this program, the decision tree process described above was compared to the "most frequent sense" baseline.
# The "most frequent sense" baseline simply chooses whichever sense was used more frequently in the training data.
# In this case, "product" was the most frequent sense in the training data, so the resulting confusion matrix is:
# 		    phone:	product:
# phone:	0	    0
# product:	72	    54
# and an accuracy of 54/126 (42.8571%).

# When using the bag of words representation and the decision tree, we get the following confusion matrix:
# 		    phone:	product:
# phone:	61	    14
# product:	11	    40
# and an accuracy of 101/126 (80.1587%).

# These confusion matrices and accuracies are determined by the 'scorer.py' part of this program.

# Program implementation:
#########################
# The program begins by calling tagFile(sys.argv[1], sys.argv[2], sys.argv[3])
# sys.argv[1] is the training data file
# sys.argv[2] is the testing data file
# sys.argv[3] is the file to print the model to

# tagFile takes the three filenames as input and first calls trainModel(training) to create the model
# the "most frequent sense" is then determined using findDefaultGuess(model)
# the default guess is used if none of the words in the testing data are present in the model
# the default guess was also used to obtain the "most frequent sense" baseline
# tagFile next calls generateTests to obtain a dictionary 'tests' of the form tests[feature] = [feature, logLikelihood, predictedSense]
# Finally, tagFile calls tagTesting to tag the testing file using 'tests' and the default guess

# The trainModel function takes the training text file and outputs a 2D dictionary of the form:
# model[s][f] = count(feature f with sense s) in the training data 
# The function opens the text file, iterates through the lines of the file and treats each line according to a set of regex
# For each instance, we obtain the sense of the instance, the ID of the instance (which isn't used), and the context of the instance
# When an </instance> tag is found, we are at the end of an instance, so the current sense of the instance and its context are saved to the dictionary
# The context of the current instance is obtained using the getFreqVector function which takes the current line of text and creates a Counter object of
# how often each word besides the headword was used.

# The findDefaultGuess function counts the frequency of each sense in the model created by trainModel
# Whichever sense has the highest frequency is returned as the defaultGuess

# The generateTests function starts by using the model to obtain a list of all of the features from the training data
# For each feature, the frequency of that feature with sense1 and sense2 is obtained
# Using these frequencies, the logLikelihood of the feature f_i is obtained using:

#|log(P(sense1 | fi) / P(sense2 | fi))|
# where:
# P(sense1 | fi) = freq[sense1][fi] / freq[fi]
# P(sense2 | fi) = freq[sense2][fi] / freq[fi]
# so P(sense1 | fi) / P(sense1 | fi) = ( freq[sense1][fi] / freq[fi] ) / ( freq[sense2][fi] / freq[fi] ) = freq[sense1][fi] / freq[sense2][fi]
# Therefore:
# |log(P(sense1 | fi) / P(sense2 | fi))| = |log( freq[sense1][fi] / freq[sense2][fi] )|

# If a feature is only used in one sense, we take logLikelihood = |log(1/number of features)|
# We want a large value of logLikelihood in this case since if a word only appears in one sense, it is very good at determining which sense an instance is
# After the loglikelihood is computed, the output dictionary is updated with:
# tests[f_i] = [f_i, logLikelihood, predictedSense]
# where predictedSense is whichever is larger: freq(sense1) or freq(sense2)
# After all features have been processed in this way, the resulting dictionary is returned and each value in tests in printed to the given file

# The tagTesting function takes the testing text file and prints pairs of the form:
# (f'<answer instance="{currentID}" senseid="{senseGuess}"/>') to STDOUT
# Processing of the testing text file is very similar to how trainModel processed it
# The file is opened and its lines are iterated through to obtain the ID and frequency vector of each instance
# The frequency vector is then iterated through and the following processing occurs to determine senseGuess:
#   For each feature in the frequency vector, 
#       the 'tests' dictionary is checked for the feature
#       if the feature is present in the dictionary and the feature has a higher logLikelihood than senseGuess, update senseGuess
#       if the logLikelihood of the feature is the same as senseGuess and a higher frequency in the frequency vector, then we also update senseGuess
#   If none of the features were present in the 'tests' dictionary, then use defaultGuess as the senseGuess
# After this processing, the current instance and its guessed sense is printed to STDOUT

import sys
import re
import math
from collections import defaultdict, Counter

# these regex are used to determine what the current line of the training or testing file is
startLines = [r'<corpus lang=\"[a-zA-Z]+\">', r'<lexelt item=\"[a-zA-z\-]+\">']
endLines = [r'</lexelt>', r'</corpus>']
getID = r'<instance id=\"(.*)\">'
getSense = r'<answer instance=\".*\" senseid=\"([a-zA-Z]+)\"\/>'
startContext = r'<context>'
endInstance = r'<\/instance>'

# tagFile is the main function of the program
# it takes the training, testing, and model output file names
# it outputs the model to modelFile and prints the guessed senses for the instances in 'testing' to STDOUT
def tagFile(training, testing, modelFile):
    model = trainModel(training)
    defaultGuess = findDefaultGuess(model)
    tests = generateTests(model, modelFile)
    tagTesting(testing, tests, defaultGuess)

# trainModel takes a file of training data and outputs a 2D dictionary which serves as the bag of words model
def trainModel(training):
    model = defaultdict(dict)
    lines = []
    # open the training file and get all of the lines in a list
    with open(training, 'r') as trainingFile:
        for line in trainingFile:
            lines.append(line.strip())
    # remove extra tags not needed for this assignment
    lines = removeExtraTags(lines)
    i = 0
    # iterate through the list of lines and process accordingly
    while i < len(lines):
        currentLine = lines[i]
        # the lines at the beginning of the document are ignored
        for r in startLines:
            if re.match(r, currentLine):
                i+=1
                continue
        # the lines at the end of the document are also ignored
        for r in endLines:
            if re.match(r, currentLine):
                i+=1
        # if the current line contains the ID of the instance, save the ID
        # we don't actually use the ID for training the model, so this is unused
        if re.match(getID, currentLine):
            currentID = re.search(getID, currentLine).groups()[0]
            i+=1
            continue
        # if the current line gives the sense of the current instance, save the instance to currentSense
        if re.match(getSense, currentLine):
            currentSense = re.search(getSense, currentLine).groups()[0]
            i+=1
            continue
        # if the current line is <context>, then the next line is the sentence of context for this instance
        # get the frequency vector for the sentence
        if re.match(startContext, currentLine):
            # the current index is <context>, we have:
            # <context>
            # sentence
            # </context>
            # ...
            # lines[i+1] is the sentence
            # lines[i+3] is the tag after </context>
            freqVector = getFreqVector(lines[i+1])
            i += 3
            continue
        # if the current line is </instance>, then we have obtained the sense, ID, and frequency vector for this instance
        # save the results for the current instance into the model with the form:
        # model[currentSense][feature] = count(uses of feature f with sense currentSense in this instance)
        if re.match(endInstance, currentLine):
            for f in freqVector.keys():
                try:
                    model[currentSense][f] +=freqVector[f]
                except:
                    model[currentSense][f] = freqVector[f]
            i+=1
    # once the file has been looped through, return the model
    return model

# findDefaultGuess determines which sense is used most frequently in the model generated by trainModel 
# and outputs it as a string
def findDefaultGuess(model):
    senses = list(model.keys())
    # featureSum is the number of times the most common sense appears
    featureSum = 0
    defaultGuess = ''
    for sense in senses:
        # sum is how many times the current sense appears
        sum = 0
        keys = model[sense].keys()
        for k in keys:
            sum += model[sense][k]
        # if the sum is higher than that of other senses, update featureSum and choose the current sense as defaultGuess
        if sum > featureSum:
            featureSum = sum
            defaultGuess = sense
    return defaultGuess

# tagTesting takes the list of tests, the defaultGuess, and the testing data file
# the instance, tag pairs are printed to STDOUT
def tagTesting(testing, tests, defaultGuess):
    lines = []
    # store the lines of the testing file in a list
    with open(testing, 'r') as testingFile:
        for l in testingFile:
            lines.append(l.strip())
    i = 0
    # iterate through the list of lines and process accordingly 
    while i < len(lines):
        currentLine = lines[i]
        # the lines at the beginning and end of the document are ignored
        for r in startLines + endLines:
            if re.match(r, currentLine):
                i+=1
                continue
        # if the current line contains the ID of the instance, save the ID
        if re.match(getID, currentLine):
            currentID = re.search(getID, currentLine).groups()[0]
            i += 1
            continue
        # if the current line is <context>, then the next line is the sentence of context for this instance
        # get the frequency vector for the sentence
        if re.match(startContext, currentLine):
            freqVector = getFreqVector(lines[i+1])
            i += 3
            continue
        # if the current line is </instance>, then we have obtained the ID and frequency vector for this instance
        # use the frequency vector to determine the sense and print the result along with the ID
        if re.match(endInstance, currentLine):
            senseGuess = ''
            foundGuess = False
            senseLogLikelihood = -1
            senseFreq = -1
            # we want the sense with the highest log likelihood
            # if there are multiple features in the vector which give the same log likelihood, choose the one with the highest frequency
            for f in freqVector:
                if f in tests:
                    # test is [feature, log, predicted]
                    # if (logLikelihood of f is higher) or (logLikelihood of f is the same AND f has higher frequency)
                    if (tests[f][1] > senseLogLikelihood) or (tests[f][1] == senseLogLikelihood and freqVector[f] > senseFreq):
                        senseLogLikelihood = tests[f][1]
                        senseGuess = tests[f][2]
                        senseFreq = freqVector[f]
                        foundGuess = True
            if not foundGuess:
                senseGuess = defaultGuess
            # print the result to STDOUT
            print(f'<answer instance="{currentID}" senseid="{senseGuess}"/>')
            i+=1

# generateTests takes the model and a file to write the model to
# the function outputs a dictionary 'tests' of the feature tests
# the model is written in the form:
# Feature {feature}:
#   Log-likelihood: {logLikelihood}
#   Predicted Sense: {predictedSense}
def generateTests(model, modelFile):
    tests = defaultdict(list)
    # features stores all of the features
    # we use a set to prevent repeats
    features = set()
    senses = list(model.keys())
    for sense in senses:
        keys = model[sense].keys()
        features = features.union(set(keys))
    # for each feature, determine the logLikelihood
    for f in features:
        # if the feature isn't in the dictionary, it has frequency 0
        try:
            freq1 = model[senses[0]][f]
        except:
            freq1 = 0
        try:
            freq2 = model[senses[1]][f]
        except:
            freq2 = 0
        # predict whichever sense appears more often
        if freq1 >= freq2:
            predicted = senses[0]
        elif freq1 < freq2:
            predicted = senses[1]
        # if both frequencies are non-zero, then compute the logLikelihood like normal
        if freq1 != 0 and freq2 != 0:
            logLikelihood = abs( math.log2(freq1 / freq2))
        # if one of the frequencies is zero, then we make the logLikelihood a large number
        # otherwise, we would have a log of 0 or log of something divided by zero which throws an error
        # log(1/len(features)) will give a logLikelihood larger than any feature which appears in both senses
        else:
            logLikelihood = abs( math.log2( 1 / len(features)))
        # store the feature, its likelihood, and the predicted sense in the tests dictionary
        tests[f] = [f, logLikelihood, predicted]
    # print the results and return the list of tests
    with open(modelFile, 'w') as f:
        #tests is tests[feature] = [feature, log, predicted]
        for t in tests.keys():
            f.write(f'Feature {tests[t][0]}:\n\tLog-likelihood: {tests[t][1]}\n\tPredicted sense: {tests[t][2]}\n\n')
    return tests

# getFreqVector takes the current sentence as a string and outputs a frequency vector for it
def getFreqVector(sentence):
    # symbols are ignored since they aren't meaningful features
    symbols = [',','.',';',':',')','(']
    # we don't include the headword in the frequencyVector
    headRegex = r'<head>([a-zA-z]+)<\/head>'
    sentenceList = sentence.split()
    freqVector = Counter()
    for currentWord in sentenceList:
        # I decided to not parse out punctuation from in features since removing the punctuation lowered the accuracy
        # For example, the feature " product; " is left without removing the semicolon
        if not re.match(headRegex, currentWord) and currentWord not in symbols:
            #freqVector[currentWord.strip(''.join(symbols))] += 1
            freqVector[currentWord] += 1
    return freqVector

# removeExtraTags takes the list of lines from the training data and removes the unnecessary tags from it
# the list of lines without these tags is returned
def removeExtraTags(lines):
    newLines = []
    # remove <p> </p> <s> </s> <@>
    badTags = ['<p>', '</p>', '<s>', '</s>', '<@>']
    for l in lines:
        for tag in badTags:
            l = l.replace(tag, '')
        newLines.append(l)
    return newLines

if __name__ == "__main__":
    tagFile(sys.argv[1], sys.argv[2], sys.argv[3])