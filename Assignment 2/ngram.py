# CMSC 416 Spring 2022 
# Professor: Dr. McInnes
# Assignment 2: N-gram Modeling
# Student: Christopher Flippen
# Due Date: February 22, 2022

# Program concept:
# ###########################
# This program creates a set of sentences using an n-gram language model from a set of input text files
# An n-gram language model uses probability to generate sentences based on word history
# For example, in the 3-gram case, we generate the next word of a sentence by looking at the previous 2 words
# In general, for n-grams, we look at the previous (n-1) words, meaning in the n=1 case, words are generated without using a history
# The program is run through terminal using: 
# py ngram.py n m inputFile(s)
# n is the type of n-gram model (1, 2, 3, ...), m is the number of sentences to generate, and inputFile(s) is a set of one of more .txt files
# Sentences from the text files are only used if they are >= n words long, and a large amount of sentences is needed in order for the program to
# generate interesting new sentences. The program was tested with sets of files from Project Gutenberg
# As n gets large, the sentences will make more sense but they also have a higher probabilitiy of being very close to sentences from the source texts:
# For n=1, the sentences are almost all original but mostly illogical. 
# For n=10, the sentences are almost all logical but most are sentences present in the source texts.
# Since unigrams don't use word histories, it is possible for sentences generated by the unigram model to just be a period. This happens when
# the first chosen word is the end of sentence symbol. (Dr. McInnes confirmed that these empty sentences are valid output for the unigram model)

# In the 3-gram case, if our sentence so far is: 'The quick', then we look at how often each word appears after 'The quick'
# We might have the phrase 'The quick brown' 5 times, the phrase 'The quick fox' 6 times, and the phrase 'The quick dog' 4 times
# In this case, 'fox' has the highest chance of being chosen since it was the most common word given the history 'The quick'
# Choosing a word is based on the formula: P(word | history) = freq(word, history) / freq(history), so in this case we have probabilities:
# P(fox | The quick) = 6/15 = 2/5, P(brown | The quick) = 5/15 = 1/3, P(dog | The quick) = 4/15

# Program usage examples:
# ###########################
# The .txt files used in these examples are files obtained from Project Gutenberg, they are not part of this source code.

# If we wanted to generate 5 sentences using the trigram (n=3) model based on the Great Gatsby, we can run:
# py ngram.py 3 5 gatsby.txt
# One possible set of output sentences is:
# Gatsby identified him adding that he was about eighteen.
# She goes around looking at Daisy and Gatsby in West Egg village every surmise about him.
# The only crazy I was bringing you that it was just eighteen two years I remember.
# I am but I pretended to be brought to him that the kitchen which could extract the juice of two hundred oranges in half an hour old and I understood that he was aware of the scene his 
# wife after attempting to laugh sometimes but there was a minute and far away.
# I saw that this was obviously untrue for someone had begun his career when he had committed himself to get her away.

# If we wanted to generate 10 sentences using a 6-gram model based on Alice in Wonderland and War and Peace, we can run:
# py ngram.py 6 10 alice.txt warAndPeace.txt
# One possible set of output sentences is:
# He took some gold pieces from his trouser pocket and put them on the dish for her.
# Weyrother complied and Dohktúrov noted them down.
# The young Cossack made his mighty interlocutor smile says Thiers.
# Involuntarily she thought their thoughts and felt their feelings.
# He patted her on the shoulder and himself closed the door after her.
# Pierre sat down by the fire and began eating the mash as they called the food in the cauldron and he thought it more delicious than any food he had ever tasted.
#He spoke so rapidly that he did not finish half his words but his son was accustomed to understand him.
# Her eyes always sad now looked with particular hopelessness at her reflection in the glass.
# I dont mind what they think of me.
# Natásha glanced with frightened eyes at the face of the wounded officer and at once went to meet the major.

# Program implementation:
# ###########################
# The program begins by calling checkParameters() to make sure the user's command line arguments are valid
# If checkParameters() returns True, then runNgram(n, m, files) is called
# runNgram first prints a message stating what the program is and what its current parameters are
# Next, it creates two dictionaries: a 2D dictionary 'nGrams' which stores the (word, history) pairs
# and a 1D dictionary 'history' which counts the frequency of each (n-1)-gram (each word history)
# If n=1, then nGrams is unused and history stores the frequency of each word
# Each file is opened, has its contents stored as a string, the contents are procesed using processText, and history and nGrams are updated
# After all files have been read, history and nGrams are used to generate sentences with generateSentences (or generateUniSentences for n=1)
# The resulting sentences are then printed

# The processText function first removes/replaces certain characters in the string such as puncuation and quotes
# Periods, question marks, and exclamation points are replaced with start and end tags 
# These tags are used to denote where sentences start and end
# Sentences start with (n-1) start tags to properly split the sentence into nGrams
# When we generate sentences later, we start with (n-1) start tags since that is how all sentences in the processed text start
# After formatting the text, processText calls getNgrams (for n>1) or getUnigrams (for n=1)

# getNgrams takes the formatted text string, splits it into a list of words, and goes through the list of words to get the
# frequencies of word histories and of word|history pairs. These frequencies are stored in history and nGrams
# If a sentence has fewer than n words, it is not used

# getUnigrams takes the formatted text string, splits it into a list of words, and stores the frequency of each word in history

# generateSentences first updates nGrams to store the probability of each word|history pair (P(word|history)) using computeNProbs
# Next, it starts each sentence with a set of (n-1) start tags and chooses the next word using chooseNextWord.
# When chooseNextWord returns an end tag, the sentence is formatted using formatSentence and saved in the list of output sentences

# generateUnigramSentences first updates history to store the probability of each word (P(word)) using computeUniProbs
# Next, it builds a sentence using chooseNextUnigram. Unigram sentences don't use word history, so chooseNextUnigram just chooses a word according to probability
# When chooseNextUnigram returns an end tag, the sentence is formatted using formatSentence and saved in the list of output sentences

# computeNProbs and computeUniProbs are implementations of the formulas:
# P(word|history) = freq(history, word)/freq(history) and
# P(word) = freq(word)/totalWords
# respectively

# chooseNextWord and chooseNextUnigram look at the list of possible next words and choose one using the probabilities of the available next words
# The list of possible next words is either the words in nGrams[history] for chooseNextWord or just any word for chooseNextUnigram

import sys
import os
import re
from collections import Counter, defaultdict
from random import random

# startTag and endTag are stored as global variables since several functions use them
startTag = '<s> '
endTag = ' <e> '

# This is the main function for processing the text files and generating the sentences
# n, m, and files were already checked with checkParameters(), so they must be of the correct types
# n is the type of n-gram
# m is the number of sentences
# files is the list of input txt files
# Two lines are printed stating what the program is and what the current parameters are 
# The remaining printed output is list of generated sentences
def runNgram(n, m, files):
    print('This program generates random sentences based on an Ngram model and was written by Christopher Flippen')
    print(f'Current settings are: n={n} and m={m}, so we will generate {m} sentences with a {n}-gram model')
    # command line arguments are string, so we convert to int
    n = int(n)
    m = int(m)
    # history stores the frequency of each (n-1)-gram (each 'word history')
    # if n==1, then history is the frequency of each word
    history = Counter()
    # nGrams stores the frequency of a word given its history
    # nGrams[history][word]
    nGrams = defaultdict(dict)
    # open each file, read its contents, and update history and nGrams accordingly
    for f in files:
        with open(f, 'r', encoding='utf-8') as currentFile:
           fileText = currentFile.read()
        # if n>1, both history and nGrams are updated
        if n > 1:
           history, nGrams =  processText(fileText, n, m, history, nGrams)
        # if n=1, we only need to use history
        else:
            history = processText(fileText, n, m , history, nGrams)
    # if n>1, sentences are generated using both history and nGrams
    if n > 1:
        sentences = generateSentences(n, m, history, nGrams)
    # if n=1, sentences are generated using only history
    else:
        sentences = generateUnigramSentences(m, history)
    print('Sentences:')
    for s in sentences:
        print(s)

# checkParameters checks that the values in sys.argv are appropriate
# returns False and prints a message if not
# the input format should be: ngram.py n m inputFile(s)
def checkParameters():
    # if too few arguments
    if len(sys.argv) < 3:
        printUsage()
        return False
    fileList = sys.argv[3:]
    # check that n and m are numbers
    try:
        int(sys.argv[1])
        int(sys.argv[2])
    except:
        printUsage()
        return False
    # check that each input file name is a valid file
    for fileStr in fileList:
        if not os.path.isfile(fileStr):
            printUsage()
            print(f'The string "{fileStr}" is not a valid file')
            return False
    return True

# function used by checkParameters to print the error message
def printUsage():
    print('Command line usage is: ngram.py n m inputFile(s)')

# fileText is the current text file as a string
# this function replaces end of sentence marks with periods
# later we replace all periods with end and start tags
def replacePeriods(fileText):
    return re.sub('[!?]',' . ', fileText)

# fileText is the current text file as a string
# this function removes all types of quotes
def removeQuotes(fileText):
    # triple quotes around a string allow for all quote types to be used in it
    return re.sub(r"""[“"”‘’`']""", '', fileText)

# fileText is the current text file as a string
# this function removes , ; : and a bunch of other symbols
def removePunctuation(fileText):
    # em dashes connect phrases together and so removing them or leaving them unchanged would 
    # cause some words to be connected that shouldn't have been. 
    # Hyphens are not removed because they are used in cases where two words should be connected 
    fileText = re.sub(r'[\—]',' ', fileText)
    # this is run before adding tags so removing < and > is okay
    return re.sub(r'[:;,<>\/\+\\\%\_\(\)\*\[\]]','', fileText)

# fileText is the current text file as a string
# this function removes newLine characters
def removeNewLines(fileText):
    return re.sub(r'[\t\n\v\f\r]',' ',fileText)

# fileText is the current text file as a string
# n is the type of n-gram being created
# every sentence begins with n-1 start tags and ends with an end tag
# this function is used after replacePeriods, so all sentences should end with periods
def addTags(fileText, n):
    # python allows for string multiplication: https://stackoverflow.com/a/1424016
    # startTags is n-1 copies of the start tag
    startTags = (n-1)*startTag
    # start the file with start tags
    fileText = startTags + fileText
    # replace periods with <s> <e>, we already replaced ! and ? with . in replacePeriods
    fileText = re.sub(r'\.', f'{endTag} {startTags}', fileText)
    # add an endtag to the end of the file since the file might end without a period
    fileText = fileText + endTag
    return fileText

# fileText is the current text file as a string
# n is the type of n-gram being created
# history stores the frequency of each (n-1)-gram (each word history)
# nGrams stores the frequency of a word given its history
# this function gets nGrams (for n>1) and updates history and nGrams with the results
def getNGrams(fileText, n, history, nGrams):
    # turn the file text into a list of words - split automatically deals with whitespace
    wordList = fileText.split()
    i = 0
    # for each i, we take i and the next n-1 words, so i only goes up to len(wordList) - (n-1)
    while i < len(wordList) - (n-1):
        # if on a start tag, make sure it is the start tag for a sentence of sufficient length
        if wordList[i] == startTag.strip():
            # if the length of the sentence is too short, set i to the index of the next sentence start
            if not checkSentenceLength(i, wordList, n):
                i = findNextSentenceStart(i, wordList)
            # if checkSentenceLength is true, then we can scan the current sentence with no issue
            else:
                currentNGram = wordList[i:i+n]
                # pair = (word, history)
                pair = (currentNGram[-1], ' '.join(currentNGram[:-1]))
                # if an endTag is in the history, then we don't have a valid ngram, so we skip it
                if not endTag in pair[1]:
                    # update the count of the current ngram
                    history[pair[1]] += 1
                    # update the count of the current word, history pair
                    try:
                        nGrams[pair[1]][pair[0]] +=1
                    except:
                        nGrams[pair[1]][pair[0]] = 1
                i+=1
        # if we don't have a start tag at i, then we must be in the middle of a valid sentence
        else:
            currentNGram = wordList[i:i+n]
            pair = (currentNGram[-1], ' '.join(currentNGram[:-1]))
            if not endTag in pair[1]:
                history[pair[1]] += 1
                try:
                    nGrams[pair[1]][pair[0]] +=1
                except:
                    nGrams[pair[1]][pair[0]] = 1
            i+=1
    return history, nGrams

# fileText is the current file as a string
# history is a counter we update with the frequency of each unigram
# this function updates the list of unigrams in history
def getUnigrams(fileText, history):
    wordList = fileText.split()
    for w in wordList:
        history[w] += 1
    return history

# this function starts at index i and tries to find the next start of a sentence in wordList
def findNextSentenceStart(i, wordList):
    # files have end tags appended to the end, so an end tag will always exist after a start tag
    while wordList[i] != endTag.strip():
        i+=1
    # if i is an end tag, then i+1 is either a start tag or an index larger than the length of wordList
    # if i+1 is a valid start tag, then getNGrams will process it, else it will stop its processing since the file is over
    return i+1

# this function determines if the sentence starting at index i is of a valid length
# the n parameter is needed since sentences start with (n-1) start tags
# if the current sentence is of valid length or if i is not the start of a sentence, return True
# else return False
def checkSentenceLength(i, wordList, n):
    # if a sentence has (n-1) start tags and >= n words, then the next end tag must be
    # at least 2n-2 words away from the start of the sentence
    # if i == 0, then we are on the first sentence
    if i == 0:
        if len(wordList) > (2*n-1):
            if endTag.strip() in wordList[0:2*n]:
                return False
            else:
                return True
        else:
            return False
    # check if a sentence after the first sentence is the right length
    elif wordList[i] == startTag.strip() and wordList[i-1] == endTag.strip():
        if len(wordList) > i+(2*n-1):
            if endTag.strip() in wordList[i:i+(2*n)]:
                return False
            else:
                return True
        else:
            return False
    # if we reach here, then index i wasn't the start tag at the beginning of a sentence
    else:
        return True

# for n > 1, this function generates a list of m sentences using history and nGrams
# the sentences are returned as a list of strings
def generateSentences(n, m, history, nGrams):
    sentences = []
    # update nGrams to store P(word|history) instead of frequencies
    nGrams = computeNProbs(nGrams, history)
    for _ in range(m):
        # sentences start with (n-1) start tags
        sentence = (n-1)*[startTag.strip()]
        nextWord = ''
        # choose the next word and add it to the sentence
        while not nextWord == endTag.strip():
            nextWord = chooseNextWord(n, nGrams, sentence)
            sentence.append(nextWord)
        # convert the sentence from a list to a string and remove the tags
        # then store the sentence in the list
        formattedSentence = formatSentence(sentence)
        sentences.append(formattedSentence.strip()+'.')
    return sentences

# for n = 1, this function generates a list of m sentences using history
# nGrams isn't needed because unigrams don't look at P(word|history), just P(word)
# it is possible for sentences generated by this function to be just a period if the first word of the sentence is an end tag
# Dr. McInnes confirmed that empty sentences are valid output for the unigram model
def generateUnigramSentences(m, history):
    sentences = []
    # update history to store P(word) instead of frequencies
    history = computeUniProbs(history)
    for _ in range(m):
        nextWord = ''
        sentence = []
        # choose the next word and add it to the sentence
        while not nextWord == endTag.strip():
            nextWord = chooseNextUnigram(history)
            sentence.append(nextWord)
        # convert the sentence from a list to a string and remove the tags
        # then store the sentence in the list
        formattedSentence = formatSentence(sentence)
        sentences.append(formattedSentence.strip()+'.')
    return sentences

# this function take a sentence stored as a list, 
# converts it to a string separated by spaces, removes start and end tags
# and returns the result
def formatSentence(sentenceList):
    formattedSentence = ' '.join(sentenceList)
    formattedSentence = re.sub(r'<s>','',formattedSentence)
    formattedSentence = re.sub(r'<e>','',formattedSentence)
    return formattedSentence

# this function selects the next word for the unigram sentence using the frequency table 'history'
def chooseNextUnigram(history):
    # cumulativeVals store cumulative probability of a unigram being chosen
    keys = list(history.keys())
    cumulativeVals = []
    for k in keys:
        cumulativeVals.append(history[k])
    # if there is only one type, its probability to be chosen is 1
    if len(cumulativeVals) == 1:
        cumulativeVals[0] = 1
    # if there are multiple types, P(i) += P(i-1)
    else:
        for i in range(1, len(cumulativeVals)):
            cumulativeVals[i] += cumulativeVals[i-1]
        # due to rounding errors, cumulativeVals[-1] sometimes has value 0.99999999 instead of 1
        # which could cause a very rare failure in the code, so we just set it to 1
        cumulativeVals[-1] = 1
    # generate a random number and find the choice corresponding with it
    randChoice = random()
    for i in range(len(keys)):
        if randChoice < cumulativeVals[i]:
            return keys[i]

# this function selects the next word for the sentence using the P(word|history) table 'nGrams'
def chooseNextWord(n, nGrams, sentence):
    # the most recent n words in the sentence are our word history
    history = ' '.join(sentence[-(n-1):])
    options = nGrams[history]
    keys = list(options.keys())
    cumulativeVals = []
    for k in keys:
        cumulativeVals.append(options[k])
    if len(cumulativeVals) == 1:
        cumulativeVals[0] = 1
    else:
        for i in range(1, len(cumulativeVals)):
            cumulativeVals[i] += cumulativeVals[i-1]
        # due to rounding errors, cumulativeVals[-1] sometimes has value 0.99999999 instead of 1
        # which could cause a very rare failure in the code, so we just set it to 1
        cumulativeVals[-1] = 1
    # generate a random number and find the choice corresponding with it
    randChoice = random()
    for i in range(len(keys)):
        if randChoice < cumulativeVals[i]:
            return keys[i]

# this function updates the unigram frequency table 'history' to store the 
# probabilities rather than frequencies of each type 
def computeUniProbs(history):
    historyKeys = history.keys()
    totalVals = 0
    for k in historyKeys:
        totalVals += history[k]
    for k in historyKeys:
        # P(word) = freq(word)/totalWords
        freq = history[k]
        history[k] = freq/totalVals
    return history

# this function updates the table of word-history pairs 'nGrams' to store the
# probabilities rather than frequencies
# history stores the frequency of each (n-1)-gram (each word history)
def computeNProbs(nGrams, history):
    nGramKeys = nGrams.keys()
    for currentGram in nGramKeys:
        freq = history[currentGram]
        currentGramKeys = nGrams[currentGram].keys()
        for key in currentGramKeys:
            # P(word|history) = freq(history, word)/freq(history)
            # freqWithHistory = freq(history, word)
            # freq = freq(history)
            freqWithHistory = nGrams[currentGram][key]
            nGrams[currentGram][key] = freqWithHistory/freq
    return nGrams

# fileText is the current text file stored as a string
# this function removes quotes, periods, puncuation, and newlines from the string 
# then adds start and end tags and calls getNGrams or getUnigrams
def processText(fileText, n, m, history, nGrams):
    fileText = removeNewLines(removePunctuation(replacePeriods(removeQuotes(fileText))))
    fileText = addTags(fileText, n)
    if n > 1:
        return getNGrams(fileText, n, history, nGrams)
    else:
        return getUnigrams(fileText, history)

# if checkParameters confirms that the values in sys.argv are valid, then call runNgram
if __name__ == "__main__":
    if checkParameters():
        runNgram(sys.argv[1], sys.argv[2], sys.argv[3:])