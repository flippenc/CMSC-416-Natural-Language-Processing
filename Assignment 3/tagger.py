# CMSC 416 Spring 2022 
# Professor: Dr. McInnes
# Assignment 3: POS Tagging
# Student: Christopher Flippen
# Due Date: March 15, 2022

import sys
import re
from collections import defaultdict 

# Program concept and usage:
# ##########################
# The 'tagger.py' part of this program takes a file of part of speech tagged text in order to train a POS-tagger 
# and a file of text to POS tag using the trained model.
# The output of the program is by default printed, but may be directed to a file.
# For example: if pos-train.txt is training data and post-test.txt is text to be tagged,
# the program may be run with the following command which will output the result to a new file called pos-test-with-tags.txt

# py tagger.py pos-train.txt pos-test.txt > pos-test-with-tags.txt

# The POS tagger uses the "most likely tag" baseline. 
# This means, when choosing the tag for a word, it chooses the tag which maximizes P(tag|word). 
# This is equivalent to choosing the tag that most frequently appeared with that word in the training data

# In order to check the accuracy of the tagger, this program has a second part: 'scorer.py'.
# A description of this part is on the scorer.py file.

# Program implementation and rules:
###################################
# The main functionality of the program comes from using a 2D dictionary. 
# This dictionary stores word, tag pairs and tagDict[word][tag] gives the frequency of the tag with the word
# Since this tagger uses the most likely tag baseline, selecting the tag for a given word is done by looking at the tags in the tagDict[word] list and
# choosing the one with the highest frequency

# The program begins by calling tagFile(sys.argv[1], sys.argv[2])
# sys.argv[1] is the training file and sys.argv[2] is the file to tag
# tagFile begins by calling createTagDict() to create the tag dictionary
# createTagDict starts by opening each line of the training file
# It then uses a regex to get all tokens on the line that contain '/'
# This regex prevents '[' and ']' characters from being treated as tokens
# The list of tokens containing '/' is then split into its word, tag components
# If the token contains '\/', a regex is used to make sure the token is split properly
# If the token contains '|', the first tag in the piped list is taken as the chosen tag
# With this list of word, tag pairs, the dictionary is then filled and returned

# Once tagFile has the dictionary created, it opens the file of text to tag, and tags it line by line using replaceLine
# The tagged lines are stored in a list and the list is printed
# replaceLine starts by taking the current line of the file to be tagged
# It splits the line into a list of words, and if the words are not '[' or ']', it checks if they are present in the dictionary.
# If the word is present in the dictionary, the most likely tag is chosen and the word is added to a list with its new token
# By default, if the current word does not appear in the dictionary, it is assumed to be 'NN' (a singular noun)
# If the 'rules' variable is set to True, 5 additional rules will be used when determining a tag for words
# The rules try to reduce how often this guess occurs and the final rule changes how this guess works.

# The first two rules are checked by running a regex on the encountered tokens. 
# These two rules are the 'number rule' and the 'money rule' which are implemented in the 'checkNumber' and 'checkMoney' functions respectively. 
# These two functions are called by the 'checkRegexRules' function.

# The number rule: in the Penn Treebank POS tagset, numbers always have the tag of 'CD' (cardinal-number). 
# Since the training data likely doesn't have all numbers in it, this function uses regular expressions to identify numbers. 
# The number forms it recognizes are: 
# fractions: 322\/653, decimals: 21.654, integers: 213, and numbers with commas (and maybe decimals) 123,456,789.91011. 
# This rule isn't perfect because it doesn't cover fractions that are written as words, 
# such as 'three-fifths', however, fractions like this are not always 'CD' in the Penn Treebank tagset.

# The money rule: in the Penn Treebank POS tagset, the '$' tag includes the $ sign by itself
# as well as other currencies which use the $ sign such as C$, HK$, and US$. 
# The testing training data we were given for the assignment did not include HK$ or US$, so this rule covers those cases. 
# This rule uses a regex to check if a token is of the form {letters}$ and if it is, it is assigned the tag of '$'. 
# This rule is relatively specific, but it should ensure that the '$' is close to perfect.

# The next two rules are the 'cases rule' and the 'plural rule' which are implemented by the 'checkCase' and 'checkPlural' functions respectively. 
# These two functions are called by the 'checkDict' function. 
# Both of these rules rely on the following idea: 
# the current word is not in the dictionary, if we modify the word slightly, does the modified version appear in the dictionary?

# The cases rule: sometimes a word is present in the training data, but only with different capitalization. 
# If a word is not in the trained dictionary, this rule checks if the unknown word in all caps, in all lowercase, or with a capitalized first letter is present in the dictionary. 
# This rule is used instead of making the dictionary ignore case because there are cases in which the capitalized or lowercase versions of a word might have distinct meanings 
# such as 'apple' as in the fruit versus 'Apple' as in the company.

# The plural rule: sometimes a word is present in the training data, but only in the singular or only in the plural form. 
# If a word is not trained dictionary or found by the cases rule, this rule checks if adding or removing an 's' from its end results in a word in the dictionary. 
# Since we are changing between singular and plural, if the modified word has a plural noun tag in the dictionary, the function returns the singular tag and vice versa. 
# This function only works with nouns since other parts of speech which end in 's' behave in more complicated ways.

# The final rule is the 'guess' rule which is used if the current word was not found by the regex rules and if it and its modified forms were not in the dictionary. 
# This rule is implemented by the 'guessTag' function and is run after the 'checkRegexRules' and 'checkDict' functions.

# The guess rule: if a word starts in a capital letter, rather than guessing that is a regular noun, guess that it is a proper noun. 
# In addition, if the unknown word ends in an 's', then it might be plural, so guess that it is a plural noun or proper noun. 
# Even though this rule is relatively simple and is similar to the cases and plural rules, it had the largest impact on tagger accuracy out of the rules.

# Rule 1: numbers
# Rule 2: money
# Rule 3: cases
# Rule 4: plural
# Rule 5: guess

# The accuracies for the different rules were as follows:
# Accuracy with no rules: 	47912/56824 (84.316%)   (baseline)
# Accuracy with rule  1: 	48357/56824 (85.099%)   (+0.783%)
# Accuracy with rules 1-2:	48361/56824 (85.1066%)  (+0.0076%)
# Accuracy with rules 1-3:	48509/56824 (85.367%)   (+0.2604%)
# Accuracy with rules 1-4:	48743/56824 (85.779%)   (+0.412%)
# Accuracy with rules 1-5:	50552/56824 (88.962%)   (+3.183%)

# Each rule addition increased the accuracy of the tagger
# The largest increase came from the guess rule with an improvement of 3.183% over the run with just rules 1 through 4

rules = True

# tagFile is the main function for the tagger
# training is the name of the file to train from and testing is the file to add tags to
def tagFile(training, testing):
    # tagDict is a 2D dictionary that stores the (word, tag) pairs
    # when tagging data, the most common tag in tagDict[word][tag] is chosen
    tagDict = createTagDict(training)
    # results is a list of modified lines from the file
    results = []
    # open the file, read each line, and add the tags to it
    with open(testing, 'r') as testingFile:
        for line in testingFile:
            line = replaceLine(line, tagDict)
            results.append(line)
    # each line of the file is printed to the console which is redirected to a file
    for line in results:
        print(line)

# checkNumber is the rule that checks if a given token is a number
# if the token is a number the tuple (True, 'CD') is returned, else (False, '') is returned
def checkNumber(token):
    # fractions D\/D, decimals D.D, and integers D, numbers with commas (and maybe decimals) D,D,D,D.D
    # the \A and \Z characters are to make sure the string doesnt have trailing non-numbers
    # since the tokens were obtained using split(), we don't have to worry about whitespace
    regList = [r"(\A\d+\\\/\d+\Z)", r"(\A\d+.\d+\Z)", r"(\A\d+\Z)", r"\A(\d+\,\d+)+\.{0,1}\d*\Z"]
    # check each type of number and return if a match is found
    for r in regList:
        if re.match(r, token):
            return True, 'CD'
    return False, ''

# checkMoney is the rule that checks if a given token is of the $ class
# types of money such as US$, HK$, C$, etc. are of the $ class
# if the token matches the regex, (True, '$') is returned, else (False, '') is returned
def checkMoney(token):
    r = r"\A[a-zA-z]+\$\Z"
    if re.match(r, token):
        return True, '$'
    return False, ''

# checkRegexRules checks if the current token satisfies one of the regex rules
# if the token matches one of the regex rules, (True, tag) is returned, else (False, '') is returned
def checkRegexRules(token):
    rule = [checkNumber, checkMoney]
    for r in rule:
        result, tag = r(token)
        if result:
            return True, tag
    return False, ''

# checkDict checks if the current token is in the tag dictionary
# if the rule variable is set to True and the current token is not in the dictionary,
# then the tag dictionary is checked using checkCase, and if that fails, checkPlural
# if a match is found, (True, tag) is returned, else (False, '') is returned
def checkDict(tagDict, token):
    result, tag = dictSearch(tagDict, token)
    if rules and not result:
        result, tag = checkCase(tagDict, token)
        if not result:
            result, tag = checkPlural(tagDict, token)
    return result, tag

# checkCase checks if changing the case of the current token results in something that is in the tag dictionary
# the token is put into all lowercase, all caps, and first letter capitalized and if a match is found,
# (True, tag) is returned, otherwise (False, '') is returned
def checkCase(tagDict, token):
    variants = [token.lower(), token.upper(), token.capitalize()]
    for v in variants:
        result, tag = dictSearch(tagDict, v)
        if result:
            return True, tag
    return False, ''

# guessTag checks if the current token is capitalized and if it ends in an 's' and returns a tag as a guess
# if the token is capitalized, it might be a proper noun
# if the token is capitalized and ends in 's', it might be proper plural
# if the token is lowercase and ends in 's', it might be plural
# otherwise, the token is guessed to be a singular regular noun
def guessTag(token):
    if token == token.capitalize():
        if token[-1] == 's':
            tag = 'NNPS'
        else:
            tag = 'NNP'
    elif token[-1] == 's':
        tag = 'NNS'
    else:
        tag = 'NN'
    return tag

# checkPlural checks if adding or removing an 's' (making the token singular -> plural or plural -> singular)
# from the end of the current string results in something that is in the tag dictionary
# if the plural is in the dictionary but not the singular, return the singular noun tag
# if the singular is in the dictionary but not the plural, return the plural noun tag
def checkPlural(tagDict, token):
    # if the word is plural, try removing the s and see if the result is a singular known word
    if token[-1] == 's' or token[-1] == 'S':
        result, tag = dictSearch(tagDict, token[:-1])
        if result and tag == 'NN':
            return True, 'NNS'
        elif result and tag == 'NNP':
            return True, 'NNPS'
    # otherwise the word could be singular, so we try to add an s
    else:
        result, tag = dictSearch(tagDict,token+'s')
        if result and tag == 'NNS':
            return True, 'NN'
        elif result and tag == 'NNPS':
            return True, 'NNP'
    return False, ''

# dictSearch searches the tag dictionary for the current token
# if the token is found, look at the list of tags associated with that token and choose the most common one
# if the token is found, return (True, tag) otherwise, return (False, '')
def dictSearch(tagDict, token):
    if token in tagDict:
        # options is the list of tags associated with the current token
        options = tagDict[token].keys()
        bestCount = -1
        # go through the list of tags and choose the best one
        for option in options:
            optionCount = tagDict[token][option]
            if optionCount > bestCount:
                bestCount = optionCount
                tag = option
        return True, tag
    return False, ''

# replaceLine takes one line of the file to be tagged and returns a copy of the line that has been tagged
def replaceLine(line, tagDict):
    # put each word on the line into a list using split
    lineTokens = line.split()
    newTokens = []
    for token in lineTokens:
        if token not in ['[', ']']:
            checkRegexResult = False
            tag = ''
            # if the rules variable is active, first check the regex rules
            # the regex rules cover tokens likely not in the dictionary, so they are run first
            if rules:
                checkRegexResult, tag = checkRegexRules(token)
            # if a result was not found in the regex rules or if the rules variable is disabled, check the dictionary
            if not checkRegexResult:
                checkDictResult, tag = checkDict(tagDict, token)
                # if checking the dictionary didn't work, either make an educated guess with guessTag or choose 'NN'
                if not checkDictResult:
                    if rules:
                        tag = guessTag(token)
                    else:
                        tag = 'NN'
            newToken = f'{token}/{tag}'
        # if the current token is '[' or ']', don't change it, but leave it in the file
        else:
            newToken = token
        newTokens.append(newToken)
    # reconstruct the line and return it
    line = ' '.join(newTokens)
    return line

# createTagDict takes the file containing the training data and creates a 2D word, tag dictionary from it
# the dictionary is in the form tagDict[word][tag] where tagDict[word][tag] tells you freq(word|tag)
def createTagDict(training):
    tagDict = defaultdict(dict)
    # words have slashes in them, so pairRegex gets all of the words
    pairRegex = r"(\S+\/\S+)"
    searchFor = re.compile(pairRegex)
    regexResults = []
    # open the file, get the words from each line, and store them in a list
    with open(training, 'r') as trainingFile:
        for line in trainingFile:
            # findall returns a list of all matches
            result = searchFor.findall(line)
            if result is not None:
                # extend adds each match from the result list to regexResults
                regexResults.extend(result)
    # fractions have an extra slash character in them, so splitRegex deals with that
    splitRegex = r"[^\\]\/"
    for pair in regexResults:
        # if the current word/tag is a fraction, use the regex to split it
        if '\/' in pair:
            word, tag = re.split(splitRegex, pair)
        # if there is only one '/', use the normal split function
        else:
            word, tag = pair.split('/')
        # if a piped list is present in the tag, then choose the first tag
        if '|' in tag:
            tag = tag.split('|')[0]
        # if the word, tag pair is in the dictionary, increment, else add it to the dictionary
        try:
            tagDict[word][tag] +=1
        except:
            tagDict[word][tag] = 1
    return tagDict

if __name__ == "__main__":
    tagFile(sys.argv[1], sys.argv[2])