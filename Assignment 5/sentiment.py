# CMSC 416 Spring 2022 
# Professor: Dr. McInnes
# Assignment 5: Twitter Sentiment Analysis
# Student: Christopher Flippen
# Due Date: April 21, 2022

# Program concept and usage:
# ###########################
# The 'sentiment.py' part of this program implements a Decision List classifier using the bag of words feature representation 
# to perform positive/negative sentiment analysis over tweets from twitter
# The goal of sentiment analysis is to determine if a piece of text has a positive or negative sentiment.

# The bag of words feature representation views training instances as "bags of words".
# All of the words that appear in training instance  are treated as features and the order of words is ignored
# In addition to this base set of features for the bag of words, three additional types of features are added
# 1.The "(EMOTICON)" feature counts how many emoticons (such as ':)', ':(', etc.) appear in a tweet
# 2.The "(LINK)", "(AT_MENTION)", and "(HASH)" features count how many links, at mentions (@), and hashtags (#) appear in a tweet
#   These three features are referred to as the "twitter features"
# 3.The "(LOWER)", "(ALLCAPS)", and "(CAPITALIZED)" features count how many lowercase, all-caps, and regular capitalized words appear in a tweet
#   These three features are referred to as the "capitalization features"

# The "log-likelihood" is calculated to determine how useful each feature is at identifying a sentiment
# For example, if the word "happy" only appears in positive sentiment and appears several times, then "happy" will have a high log-likelihood
# More general words such as "is" appear with both positive and negative sentiments, so "is" has a low log-likelihood
# When determining the sentiment of a word in an instance, a "feature vector" is created to represent which words appear in the instance
# The sentiment associated with the word of highest log-likelihood is the chosen sentiment
# This process of "testing" each word in the feature vector is called a Decision List

# If multiple words in the feature vector have the same log-likelihood, we choose the sentiment of whichever word appears more often in the testing instance.
# For example, if "Amazon" and "Google" both have log-likelihood 3 but "Amazon" appears 3 times in the testing instance while "Google" only appears 1 time,
# then the program will choose the sentiment associated with "Amazon" in the model

# If a word appears only 1 time in the training data, it is given a log-likelihood of 0, meaning it will be very unlikely to be used
# If none of the words in the testing instance appear in the training data, the "most frequent sentiment" baseline is used.
# This means if the training data had more positive sentences than negative ones, then the default guess is positive

# The model created by the program is output to a file and the list of sentiments along with their instance IDs is printed (this can be redirected to a file)
# To run this part of the program with:
#  training data 'sentiment-train.txt', testing data 'sentiment-test.txt', model output file 'my-model.txt', and instance sentiment, ID pair output file 'my-sentiment-answers.txt',
# the program can be run with the following command:

# py sentiment.py sentiment-train.txt sentiment-test.txt my-model.txt > my-sentiment-answers.txt

# When testing this program, the decision tree process described above was compared to the "most frequent sentiment" baseline.
# The "most frequent sentiment" baseline simply chooses whichever sentiment was used more frequently in the training data.
# In this case, a positive sentiment was the most frequent in the training data, so the resulting confusion matrix is:
#           negative:   positive:
# negative: 0           0
# positive: 72          160
# and an accuracy of 160/232 (68.9655%)

# When using the bag of words with none of the extra features, the resulting confusion matrix is:
#           negative:   positive:
# negative: 16          17
# positive: 56          143
# and an accuracy of 159/232 (68.5345%)

# When using the bag of words with the Twitter features, the resulting confusion matrix is:
#           negative:   positive:
# negative: 13          11
# positive: 59          149
# and an accuracy of 162/232 (69.8276%)

# When using the bag of words with the emoticon features, the resulting confusion matrix is:
#           negative:   positive:
# negative: 13          11
# positive: 59          149
# and an accuracy of 162/232 (69.8276%) (the same as when just using the Twitter features)

# When using the bag of words with the capitalization features, the resulting confusion matrix is:
#           negative:   positive:
# negative: 16          17
# positive: 56          143
# and an accuracy of 160/232 (68.9655%) (the same as the baseline case but with a different matrix)

# When using the bag of words with the emoticon and Twitter features, the resulting confusion matrix is:
#           negative:   positive:
# negative: 13          11
# positive: 59          149
# and an accuracy of 162/232 (69.8276%) (the same as when just using the Twitter features or just the emoticon features)

# When using the bag of words with all extra features, the resulting confusion matrix is:
#           negative:   positive:
# negative: 13          11
# positive: 59          149
# and an accuracy of 162/232 (69.8276%) (the same as when using Twitter, Emoticon, or Twitter+Emoticon)

# Surprisingly, the bag of words without any additional features was less accurate than the baseline case
# We can also see that the capitalization features added as many inaccurate guesses as it added accurate ones
# Another result is that the Twitter and Emoticon features added the same amount of accuracy 
# and that combining them didn't improve the accuracy any further
# Finally, we can see that adding the capitalization features to the Twitter and Emoticon features 
# did not change the accuracy

# These confusion matrices and accuracies are determined by the 'scorer.py' part of this program.

# Program implementation:
#########################
# The program begins by calling tagFile(sys.argv[1], sys.argv[2], sys.argv[3])
# sys.argv[1] is the training data file
# sys.argv[2] is the testing data file
# sys.argv[3] is the file to print the model to

# tagFile takes the three filenames as input and first calls trainModel(training) to create the model
# the "most frequent sentiment" is then determined using findDefaultGuess(model)
# the default guess is used if none of the words in the testing data are present in the model
# the default guess was also used to obtain the "most frequent sentiment" baseline
# tagFile next calls generateTests to obtain a dictionary 'tests' of the form tests[feature] = [feature, logLikelihood, predictedSentiment]
# Finally, tagFile calls tagTesting to tag the testing file using 'tests' and the default guess

# The trainModel function takes the training text file and outputs a 2D dictionary of the form:
# model[s][f] = count(feature f with sentiment s) in the training data 
# The function opens the text file, iterates through the lines of the file and treats each line according to a set of regex
# For each instance, we obtain the sentiment of the instance, the ID of the instance (which isn't used), and the context of the instance
# When an </instance> tag is found, we are at the end of an instance, so the current sentiment of the instance and its context are saved to the dictionary
# The context of the current instance is obtained using the getFreqVector function.

# The getFreqVector takes the current sentence and returns a Counter object of the frequency of each word in the sentence
# In addition to the words in the sentence, the getFreqVector gets the results from getExtraFeatures 
# which counts the frequency of capitalization, emoticons, and twitter features and saves them as 
# the "(EMOTICON)", "(LINK)", "(AT_MENTION)", "(HASH)", "(LOWER)", "(ALLCAPS)", and "(CAPITALIZED)" 
# features as described in the program concept section

# The findDefaultGuess function counts the frequency of each sentiment in the model created by trainModel
# Whichever sentiment has the highest frequency is returned as the defaultGuess

# The generateTests function starts by using the model to obtain a list of all of the features from the training data
# For each feature, the frequency of that feature with sentiment1 and sentiment2 is obtained
# Using these frequencies, the logLikelihood of the feature f_i is obtained using:

#|log(P(sentiment1 | fi) / P(sentiment2 | fi))|
# where:
# P(sentiment1 | fi) = freq[sentiment1][fi] / freq[fi]
# P(sentiment2 | fi) = freq[sentiment2][fi] / freq[fi]
# so P(sentiment1 | fi) / P(sentiment1 | fi) = ( freq[sentiment1][fi] / freq[fi] ) / ( freq[sentiment2][fi] / freq[fi] ) 
#                                            = freq[sentiment1][fi] / freq[sentiment2][fi]
# Therefore:
# |log(P(sentiment1 | fi) / P(sentiment2 | fi))| = |log( freq[sentiment1][fi] / freq[sentiment2][fi] )|

# If a feature is only used in one sentiment, but is used multuple times in the sentiment,
# we take logLikelihood = |log(1/number of features)|
# We want a large value of logLikelihood in this case since if a word appears frequently and in only one sentiment, 
# it is very good at determining which sentiment an instance is

# If a feature is only used once in the training data, it is not very good at determining sentiment,
# so it is given a log-likelihood of 0

# After the loglikelihood is computed, the output dictionary is updated with:
# tests[f_i] = [f_i, logLikelihood, predictedSentiment]
# where predictedSentiment is whichever is larger: freq(sentiment1) or freq(sentiment2)
# After all features have been processed in this way, the resulting dictionary is returned and each value in tests in printed to the given file

# The tagTesting function takes the testing text file and prints pairs of the form:
# (f'<answer instance="{currentID}" sentiment="{sentimentGuess}"/>') to STDOUT
# Processing of the testing text file is very similar to how trainModel processed it
# The file is opened and its lines are iterated through to obtain the ID and frequency vector of each instance
# The frequency vector is then iterated through and the following processing occurs to determine sentimentGuess:
#   For each feature in the frequency vector, 
#       the 'tests' dictionary is checked for the feature
#       if the feature is present in the dictionary and the feature has a higher logLikelihood than sentimentGuess, update sentimentGuess
#       if the logLikelihood of the feature is the same as sentimentGuess and a higher frequency in the frequency vector, then we also update sentimentGuess
#   If none of the features were present in the 'tests' dictionary, then use defaultGuess as the sentimentGuess
# After this processing, the current instance and its guessed sentiment is printed to STDOUT

import sys
import re
import math
from collections import defaultdict, Counter

# these regex are used to determine what the current line of the training or testing file is
startLines = [r'<corpus lang=\"[a-zA-Z]+\">', r'<lexelt item=\"[a-zA-z\-]+\">']
endLines = [r'</lexelt>', r'</corpus>']
getID = [r'<instance id=\"(.*)\">', r'<answer instance=\"(.*)\">']
getSentiment = r'<answer instance=\".*\" sentiment=\"([a-zA-Z]+)\"\/>'
startContext = r'<context>'
endInstance = r'<\/instance>'

# tagFile is the main function of the program
# it takes the training, testing, and model output file names
# it outputs the model to modelFile and prints the guessed sentiments for the instances in 'testing' to STDOUT
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
        for r in getID:
            if re.match(r, currentLine):
                currentID = re.search(r, currentLine).groups()[0]
                i+=1
                continue
        # if the current line gives the sentiment of the current instance, save the instance to currentSentiment
        if re.match(getSentiment, currentLine):
            currentSentiment = re.search(getSentiment, currentLine).groups()[0]
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
        # if the current line is </instance>, then we have obtained the sentiment, ID, and frequency vector for this instance
        # save the results for the current instance into the model with the form:
        # model[currentSentiment][feature] = count(uses of feature f with sentiment currentSentiment in this instance)
        if re.match(endInstance, currentLine):
            for f in freqVector.keys():
                try:
                    model[currentSentiment][f] +=freqVector[f]
                except:
                    model[currentSentiment][f] = freqVector[f]
            i+=1
    # once the file has been looped through, return the model
    return model

# generateTests takes the model and a file to write the model to
# the function outputs a dictionary 'tests' of the feature tests
# the model is written in the form:
# Feature {feature}:
#   Log-likelihood: {logLikelihood}
#   Predicted sentiment: {predictedSentiment}
def generateTests(model, modelFile):
    tests = defaultdict(list)
    # features stores all of the features
    # we use a set to prevent repeats
    features = set()
    sentiments = list(model.keys())
    for sentiment in sentiments:
        keys = model[sentiment].keys()
        features = features.union(set(keys))
    # for each feature, determine the logLikelihood
    for f in features:
        # if the feature isn't in the dictionary, it has frequency 0
        try:
            freq1 = model[sentiments[0]][f]
        except:
            freq1 = 0
        try:
            freq2 = model[sentiments[1]][f]
        except:
            freq2 = 0
        # predict whichever sentiment appears more often
        if freq1 >= freq2:
            predicted = sentiments[0]
        elif freq1 < freq2:
            predicted = sentiments[1]
        # if both frequencies are sufficiently high, compute log-likelihood like normal
        if freq1 > 1 and freq2 > 1:
            logLikelihood = abs( math.log2(freq1 / freq2))
        # if the feature appeared in only one sentiment but it appeared more than once, it is given a high log-likelihood
        elif (freq1 == 0 or freq2 == 0) and (freq1 + freq2) > 1:
            logLikelihood = abs( math.log2( 1 / len(features)))
        # if the feature appeared in only one sentiment and only one time, then it is given a low log-likelihood
        else:
            logLikelihood = 0
        # store the feature, its likelihood, and the predicted sentiment in the tests dictionary
        tests[f] = [f, logLikelihood, predicted]
    # print the results and return the list of tests
    with open(modelFile, 'w') as f:
        #tests is tests[feature] = [feature, log, predicted]
        for t in tests.keys():
            f.write(f'Feature {tests[t][0]}:\n\tLog-likelihood: {tests[t][1]}\n\tPredicted sentiment: {tests[t][2]}\n\n')
    return tests

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
        for r in getID:
            if re.match(r, currentLine):
                currentID = re.search(r, currentLine).groups()[0]
                i+=1
                continue
        # if the current line is <context>, then the next line is the sentence of context for this instance
        # get the frequency vector for the sentence
        if re.match(startContext, currentLine):
            freqVector = getFreqVector(lines[i+1])
            i += 3
            continue
        # if the current line is </instance>, then we have obtained the ID and frequency vector for this instance
        # use the frequency vector to determine the sentiment and print the result along with the ID
        if re.match(endInstance, currentLine):
            sentGuess = ''
            foundGuess = False
            sentLogLikelihood = -1
            sentFreq = -1
            # we want the sentiment with the highest log likelihood
            # if there are multiple features in the vector which give the same log likelihood, choose the one with the highest frequency
            for f in freqVector:
                if f in tests:
                    # test is [feature, log, predicted]
                    # if (logLikelihood of f is higher) or (logLikelihood of f is the same AND f has higher frequency)
                    if (tests[f][1] > sentLogLikelihood) or (tests[f][1] == sentLogLikelihood and freqVector[f] > sentFreq):
                        sentLogLikelihood = tests[f][1]
                        sentGuess = tests[f][2]
                        sentFreq = freqVector[f]
                        foundGuess = True
            if not foundGuess:
                sentGuess = defaultGuess
            # print the result to STDOUT
            print(f'<answer instance="{currentID}" sentiment="{sentGuess}"/>')
            i+=1

# getExtraFeatures takes the current sentence as a list of words 
# and updates the frequency vector with the features from addEmoticons, addTwitterFeatures, and addCapitalization
def getExtraFeatures(sentenceList, freqVector):
    return addEmoticons(sentenceList, addTwitterFeatures(sentenceList, addCapitalization(sentenceList, freqVector)))

# addTwitterFeatures takes the current sentence as a list of words 
# and updates the frequency vector with the features from addLinks, addAts, and addHash
def addTwitterFeatures(sentenceList, freqVector):
    return addLinks(sentenceList, addAts(sentenceList, addHash(sentenceList, freqVector)))

# addLinks takes the current sentence as a list of words 
# and updates the frequency vector with the number of links
def addLinks(sentenceList, freqVector):
    getLink = r'https:\/\/.+\Z'
    numLinks = 0
    for word in sentenceList:
        if re.match(getLink, word):
            numLinks += 1
    freqVector['(LINK)'] += numLinks
    return freqVector

# addAts takes the current sentence as a list of words 
# and updates the frequency vector with the number of at mentions
def addAts(sentenceList, freqVector):
    getAt = r'@.+\Z'
    numAts = 0
    for word in sentenceList:
        if re.match(getAt, word):
            numAts += 1
    freqVector['(AT_MENTION)'] += numAts
    return freqVector

# addHash takes the current sentence as a list of words 
# and updates the frequency vector with the number of hashtags
def addHash(sentenceList, freqVector):
    getHash = r'#.+\Z'
    numHash = 0
    for word in sentenceList:
        if re.match(getHash, word):
            numHash += 1
    freqVector['(HASH)'] += numHash
    return freqVector

# addEmoticons takes the current sentence as a list of words 
# and updates the frequency vector with the number of emoticons
def addEmoticons(sentenceList, freqVector):
    # these lists of emoticons came from https://en.wikipedia.org/wiki/List_of_emoticons
    posEmoticons = [':-)', ':)', ':-]', ':]', ':->', ':>', ':-}', ':}', ':^)', '=]', '=)', ':-D', ':D', '=D', '=3', ':3', ';3', 
                    ';)', 'x3', ':-3', '>:3', ';-)', ':"D', ';D', ':-))', 'c:', 'C:', 'uwu', 'owo', ':P', ':-P', '=p', 'XP', 'X-P']
    negEmoticons = [':-(', ':(', ':-c', ':((', ':c', ':[', ':-[', ';(', ';-(', ';c', 'D:', 'D:<', 'D;', ':/', ':\\', ':-\\', ':-/', ':|', '://', 'D=']
    numEmote = 0
    for word in sentenceList:
        if word in posEmoticons+negEmoticons:
            numEmote += 1
    freqVector['(EMOTICON)'] += numEmote
    return freqVector

# addCapitalization takes the current sentence as a list of words 
# and updates the frequency vector with the number of all lowercase, all caps, and regular capitalized words
def addCapitalization(sentenceList, freqVector):
    numLower = 0
    numAllCaps = 0
    numCap = 0
    for word in sentenceList:
        if word.isalpha():
            if word.islower():
                numLower += 1
            elif word.isupper():
                numAllCaps += 1
            elif word == word.capitalize():
                numCap += 1
    freqVector['(LOWER)'] += numLower
    freqVector['(ALLCAPS)'] += numAllCaps
    freqVector['(CAPITALIZED)'] += numCap
    return freqVector

# getFreqVector takes the current sentence as a string and outputs a frequency vector for it
def getFreqVector(sentence):
    # individual symbols are ignored since they aren't meaningful features
    symbols = [',','.',';',':',')','(']
    sentenceList = sentence.split()
    freqVector = Counter()
    for currentWord in sentenceList:
        # punctuation is not parsed out from the features
        if currentWord not in symbols and not currentWord.isspace():
            #freqVector[currentWord.strip(''.join(symbols))] += 1
            freqVector[currentWord] += 1
    return getExtraFeatures(sentenceList, freqVector)

# findDefaultGuess determines which sentiment is used most frequently in the model generated by trainModel 
# and outputs it as a string
def findDefaultGuess(model):
    sentiments = list(model.keys())
    # featureSum is the number of times the most common sentiment appears
    featureSum = 0
    defaultGuess = ''
    for sentiment in sentiments:
        # sum is how many times the current sentiment appears
        sum = 0
        keys = model[sentiment].keys()
        for k in keys:
            sum += model[sentiment][k]
        # if the sum is higher than that of other sentiments, update featureSum and choose the current sentiment as defaultGuess
        if sum > featureSum:
            featureSum = sum
            defaultGuess = sentiment
    return defaultGuess

# sys.argv[1] = sentiment-train.txt
# sys.argv[2] = sentiment-test.txt
# sys.argv[3] = my-model.txt

if __name__ == "__main__":
    tagFile(sys.argv[1], sys.argv[2], sys.argv[3])