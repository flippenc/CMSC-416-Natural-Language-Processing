# CMSC 416 Spring 2022 
# Professor: Dr. McInnes
# Assignment 1: ELIZA
# Student: Christopher Flippen
# Due Date: February 8, 2022

# Program concept and usage:
# #############################
# This program is based off of the famous ELIZA program.
# ELIZA is a chatbot program originally designed by Joseph Weizenbaum in 1966.
# ELIZA plays the role of a Rogerian psychotherapist that takes user input as text
# and responds to the user by transforming their input into a question.
# ELIZA is run through terminal using the command 'python eliza.py'
# For example: 
# USER:  I am feeling depressed.
# ELIZA: Why are you feeling depressed?

# ELIZA's specific response depends on certain keywords in the input text.
# The conversation begins with ELIZA asking the user's name and the conversation ends when the user types 'goodbye' or 'bye'
# In this implementation, ELIZA will recognize certain keywords related to family, work, people, or school and ask about them
# These sets of words were chosen as keywords since they are things a therapy patient might talk about
# For example:
# USER:  My classes this semester are difficult
# ELIZA: Is there anything else you want to say about school?
# Or:
# USER:  My friends aren't nice to me
# ELIZA: What else can you tell me about your friends?

# For most inputs, ELIZA has multiple responses it will choose between
# For the example about friends, ELIZA could respond as follows:
# USER:  My friends aren't nice to me
# ELIZA: Are there any other people you want to talk about?

# ELIZA is able to recognize certain verbs such as 'need', 'feel', 'am', 'want', 'love', 'hate'
# These verbs were chosen due because they are things a therapy patient might talk about
# For example:
# USER:  I hate programming
# ELIZA: Is there anything else that you hate?
# Or: 
# USER:  I want to feel happy
# ELIZA: Can you tell me more about what you want?

# If the user uses a verb ELIZA isn't familiar with, its response will be more general
# For example:
# USER:  I crave power
# ELIZA: You crave power?

# ELIZA is able to recognize phrases with subjects such as 'everybody' or 'nobody'
# For example:
# USER:  Nobody wants to be my friend
# ELIZA: Are you sure that nobody wants to be your friend?
# Or:
# USER:  Everybody is angry at me
# ELIZA: You said "everybody," can you think of someone in particular?

# ELIZA can also respond to some specific questions such as:
# USER:  Are you a program?
# ELIZA: Of course not.
# When asked general questions, it will avoid them:
# USER:  I like you
# ELIZA: Let's talk about you instead.

# ELIZA also has some basic understanding of pronouns.
# If the user inputs a phrase in the form 'my {something}', 
# and begins their next input with a pronoun, ELIZA will understand the subject
# USER:  My friend
# ELIZA: Tell me about your friend
# USER:  He isn't very nice
# ELIZA: Your friend isn't very nice?

# If the user inputs 'yes' or 'no,' or something that ELIZA doesn't understand, ELIZA will give generic responses
# For example:
# USER:  Yes
# ELIZA: Okay, what would you like to tell me next?
# Or: 
# USER:  The government is controlled by aliens
# ELIZA: Interesting.

# Program implementation:
# #######################
# The program begins by calling runEliza which greets the user and gets the user's name with getName
# Next, runEliza enters a loop where it gets the user's input, uses the checkGoodbye function to see if the user ended the conversation, 
# and if not, runs elizaRespond

# elizaRespond takes the user's input (inputStr), memory information (memory), and the user's name (name) and tries to respond accordingly
# The memory variable is usually None unless the most recent message was of the form 'My {object}'
# ELIZA's responses are in a list of tuples called elizaResponseTuples
# The first element of the tuple is a regular expression
# The second element of the tuple is how ELIZA will respond if that regex is satisfied
# The code at the end of the elizaRespond function runs through this list and if the regex of a tuple is satisfied, 
# it will use the corresponding second element to generate a response

# Once a regex in the list is satisfied, the input text will be 'transformed' using the formatInput function. formatInput goes through each capture 
# group of the regex and changes words from first person to second person and vice versa in order to transform the input statement into a question.
# For example, formatInput would change the groups of (I) and (hate you) to (You) and (hate me).

# Next, the response element is used to create the response.
# The response element is either a string which is manipulated to form a response or a function pointer which is called to give a response.
# The response strings contain text such as '(GROUP0)' or '(GROUP1)' which is replaced with the corresponding capture group of the regular expression.
# If the response element is a function pointer, then the function is called with parameters inputStr, memory, and name

# The two function pointer responses in this implementation are pronounStatement and readStatement
# pronounStatement uses the memory variable to substitute a pronoun (He, She, They, It). If the memory variable is None, it will print asking the user what
# the pronoun is referring to
# readStatement works with statements in the form 'My {object}' by responding in specific ways if {object} is something it recognizes in one of
# its lists of words
# readStatement also returns object to the main function to be used as the memory variable for the next input

# When ELIZA responds using elizaRespond or readStatement, it will randomly choose to include the user's name in the response or not
# This is done by using random.choice([selection, fixCapitalization(f'{name}, {selection}')])
# fixCapitalization takes a sentence and returns that sentence where only the first word, "I", and "I'm" are capitalized

import re
import random

# This is the main function for generating responses
# inputStr is the user's current input line of text
# memory stores an object that the user referenced on their previous input - this variable is usually None
# prints ELIZA's response to the current input
def elizaRespond(inputStr, memory, name):
    # elizaResponseTuples form the 'script' for ELIZA
    # the first element of a tuple is the regex, second element is used for the response

    # Most of ELIZA's specific responses are to "I" statements since therapy frequently involves talking about oneself 
    # and because "I" statements have easy-to-recognize formats of {subject} {verb} {object}. Sentences with other subjects
    # are more likely to have more complicated structure, so ELIZA tries to deal with sentences not of this form by finding
    # specific noun keywords or the "my {}" structure
    elizaResponseTuples = [
        # responses for if user apologizes 
        # I included this because it was in Weizenbaum's original script
        (
            r"\b(I'm sorry|I am sorry|Sorry)\b",
            ["Why do you feel sorry?",
            "You don't need to apologize.",
            "Why do you want to apologize?"]
        ),

        # If ELIZA is asked if it is a person or who it is, it will respond accordingly
        # I got the idea of these responses from Weizenbaum's original script

        # specific statements or questions directed towards ELIZA 
        (
            r"\b(What is your name|Who are you|What are you)\b",
            ["My name is Eliza.",
            "I am a psychotherapist named Eliza."]
        ),

        # more formats of questions directed at ELIZA
        (
            r"\b(Are you) (real|a person|a human|alive)\b",
            ["Why wouldn't I be (GROUP1)?",
            "Of course I am (GROUP1).",
            "Yes, I am (GROUP1)."]
        ),

        # more formats of questions direacted at ELIZA
        (
            r"\b(Are you) (not real|a machine|a computer|a program|a computer program|an AI|a robot|not human)\b",
            ["Why would you think that?",
            "Why would you think that I am (GROUP1)?",
            "Of course not."]
        ),
        
        # general statements directed at ELIZA are deflected
        (
            r"\b(you)\b",
            ["Why are you talking about me?",
            "You don't need to talk about me, let's focus on you.",
            "Let's talk about you instead."]
        ),

        # ELIZA is about the user telling ELIZA things, 
        # not about ELIZA telling the user things since it doesn't understand anything
        (
            r"\b(What|Why|Who|Where|When)\b",
            ["Why are you asking me this?",
            "Why would I know that?",
            "I don't think I can answer that."]
        ),

        # A lot of negative feelings can be caused by feeling that "everyone" or "nobody" treats you a certain way:

        # respond to statements like "everybody does {}", "everybody thinks {}", etc.
        (
            r"\b(Everybody|Everyone|Somebody) (.*)", 
            ['You said "(GROUP0)," can you think of someone in particular?', 
            'You said "(GROUP0)," can you think of someone specific that (GROUP1)?']
        ),

        # respond to statements like "nobody likes {}", "no one does {}"
        (
            r"\b(Nobody|No one|Noone) (.*)", 
            ["Are you sure that (GROUP0) (GROUP1)?", 
            "Why do you think that (GROUP0) (GROUP1)?"]
        ),
        
        # search for specific negative emotions in "I am" statements in order to respond with sympathy
        (
            r"\b(I'm|I am) (depressed|worried|stressed|sad|blue|unhappy|lonely|unhappy|unloved|afraid|nervous|angry)\b", 
            ["I'm sorry to hear that you are (GROUP1), please tell me why.", 
            "Do you think talking to me will help you not be (GROUP1)?", 
            "I'm sorry to hear that, can you tell me why?"]
        ),
    
        # search for general "I am" statements
        (
            r"\b(I'm|I am) (.*)", 
            ["Why are you (GROUP1)?", 
            "Can you tell me more about why you are (GROUP1)?", 
            "You are (GROUP1)?"]
        ),

        # search for specific negative emotions in "I feel" statements in order to respond with sympathy
        (
            r"\b(I feel) (depressed|worried|stressed|sad|blue|unhappy|lonely|unhappy|unloved|afraid|nervous|angry)\b", 
            ["I'm sorry to hear that you are feeling (GROUP1), please tell me more.", 
            "Do you think talking to me will help you not feel (GROUP1)?", 
            "I'm sorry to hear that, can you tell me more?"]
        ),

        # search for general feelings
        (
            r"\b(I feel) (.*)", 
            ["Why do you feel that way?", 
            "Why do you feel (GROUP1)?", 
            "Can you tell me why you feel (GROUP1)?", 
            "Tell me more about this feeling."]
        ),

        # generic agreement and disagreement
        (
            r"\b(I don't|I do not|I'm not|I am not|I cannot|I can't|I can not)\b",
            ["Why not?"]
        ),

        (
            r"\b(I do|I can)\b",
            ["Why?"]
        ),

        # generic responses to yes and no that should work regardless of context
        (
            r"\b(Yes|No|Yeah)\b",
            ["Okay, what would you like to tell me next?"]
        ),

        # general thoughts and feelings
        (
            r"\b(I think) (.*)",
            ["Why do you think (GROUP1)?",
            "Why do you think this?",
            "Tell me why you think (GROUP1)."]
        ),

        (
            r"\b(I hope) (.*)",
            ["Why do you hope this?",
            "Why do you hope (GROUP1)?",
            "Tell me more about what you hope for."]
        ),

        (
            r"\b(I like) (.*)",
            ["Can you tell me more about what you like?",
            "You like (GROUP1)?",
            "Why do you like (GROUP1)?"]
        ),

        (
            r"\b(I want) (.*)",
            ["Why do you want (GROUP1)?",
            "You want (GROUP1)?",
            "Can you tell me more about what you want?"]
        ),

        (
            r"\b(I need) (.*)",
            ["Why do you need (GROUP1)?",
            "You need (GROUP1)?",
            "Can you tell me more about what you want?"]
        ),

        (
            r"\b(I love) (.*)",
            ["Why do you love (GROUP1)?",
            "You love (GROUP1)?",
            "What else do you love?"]
        ),

        (
            r"\b(I hate) (.*)",
            ["Why do you hate (GROUP1)?",
            "You hate (GROUP1)?",
            "Is there anything else that you hate?"]
        ),

        # if a statement is in the form 'my {...}', send it to readStatement so more detailed processing can be done
        (
            r"\b(My) (.*)", 
            [readStatement]
        ),

        # if a statement uses a pronoun, send it to pronoun statement to check if the pronoun subject is in the 
        # memory variable and to respond accordingly
        (
            r"\b(He|She|They|It) (.*)",
            [pronounStatement]
        ),

        # statement using a keyword but sentence structure not recognized
        (
            r"\b(family|husband|wife|spouse|sister|brother|son|daughter|children|child|parent|sibling|mom|dad|mother|father)\b",
            ["What else can you tell me about your (GROUP0)?",
            "Is there anything else you want to say about your family?"]
        ),

        (
            r"\b(school|class|professor|teacher|instructor|classes|professors|teachers|instructors)\b",
            ["What else can you tell me about your (GROUP0)?",
            "Is there anything else you want to say about school?"]
        ),

        (
            r"\b(people|friend|friends|boyfriend|girlfriend|roommate|significant other)\b",
            ["What else can you tell me about your (GROUP0)?",
            "Are there any other people you want to talk about?"]
        ),

        (
            r"\b(boss|job|work|employer)\b",
            ["What else can you tell me about your (GROUP0)?",
            "Is there anything else you want to say about work?"]
        ),

        # generic I statement using verb not recognized
        (
            r"\b(I) (.*)",
            ["Why do you (GROUP1)?",
            "You (GROUP1)?"]
        ),

        # input doesn't match anything else
        (
            r"(.*)",
            ["I see.",
            "Please continue.",
            "Interesting."]
        )
    ]

    for ruleTuple in elizaResponseTuples:
        # iterate through the list of elizaResponseTuples and which regex the message fits
        pattern = ruleTuple[0]
        # re.IGNORECASE used because case doesn't matter
        searchFor = re.compile(pattern, re.IGNORECASE)
        regexResults = searchFor.search(inputStr)
        # if the current regex doesn't work, continue looping
        if regexResults is None:
            continue
        else:
            # if the current regex does work, get the corresponding response 'ruleList' and choose one
            ruleList = ruleTuple[1]
            ruleSelection = random.choice(ruleList)
            # callable checks if an object is a function pointer
            # https://docs.python.org/3/library/functions.html#callable
            # call the function pointer if it is one - the returned value is what 'memory' will become
            if callable(ruleSelection):
                return ruleSelection(inputStr, memory, name)
            # if it is not a function pointer, it is a string we have to manipulate
            else:
                # use formatInput to change subjects of phrases to direct them towards the user
                regexGroups = formatInput(regexResults.groups())
                # replace all (GROUP) tags with the appropriate capture group text
                # f-strings allow for easier formatting of Python strings than .format():
                # https://www.geeksforgeeks.org/formatted-string-literals-f-strings-python/
                for i in range(len(regexGroups)):
                    groupStr = f"(GROUP{i})"
                    ruleSelection = ruleSelection.replace(groupStr, regexGroups[i])
                # randomly decide whether or not to use the user's name and then print the response
                # fixCapitalization makes sure the sentence starts with a capitalized name followed by a sentence where only "I" or "I'm" is capitalized
                nameSelection = random.choice([ruleSelection, fixCapitalization(f'{name}, {ruleSelection}')])
                print(nameSelection)
                # return None since memory is only non-None if a function rule is used
                return None

# if the current statement uses a pronoun, respond by referencing the object the pronoun refers to
# inputStr is the current user input, memory should be the subject of the pronoun
def pronounStatement(inputStr, memory, name):
    pattern = r"(He|She|They|It) (.*)"
    searchFor = re.compile(pattern, re.IGNORECASE)
    regexGroups = searchFor.search(inputStr).groups()
    pronoun = regexGroups[0].lower()
    # if there is nothing in 'memory', ELIZA doesn't know what the pronoun refers to
    if memory is None and pronoun != "it":
        print(f'Who is "{pronoun}" referring to?')
    elif memory is None and pronoun == "it":
        print(f'What is "{pronoun}" referring to?')
    # if there is something in memory, use it in the response
    else:
        # format the regex groups and then return asking about the sentence subject
        regexGroups = formatInput(regexGroups)
        print(f"Your {memory} {regexGroups[1].lower()}?")
    # keep the current value as memory
    return memory


# function to get the user's name from the input, inputStr
# in the cases I could think of, the user's name would either be the first or last word,
# so the function splits the input into words and takes either the first or last word
# My name is ...
# ... is my name.
# I am ...
def readName(inputStr):
    wordList =  inputStr.split()
    # rstrip used to remove puncuation from the right end of strings
    # https://docs.python.org/3/library/stdtypes.html#str.rstrip
    name1 = wordList[-1].rstrip('.!?')
    name2 = wordList[0].rstrip('.!?')
    # if the last word of the input is 'NAME', the user probably put their name as the first word
    if (name1.upper() == "NAME"):
        return name2.capitalize()
    return name1.capitalize()

# go through each capture group in regexGroups and replace words using wordSwap 
# so the phrase is directed towards the user (me -> you), etc.
# end of sentence puncutation (.?!) is also removed using rstrip()
# return the 'formatted' regex groups
def formatInput(regexGroups):
    formattedGroups = []
    for i in range(len(regexGroups)):
        group = regexGroups[i]
        # lower() used since wordSwaps makes some things capitalized
        group = wordSwaps(group).lower().rstrip('.?!')
        formattedGroups.append(group)
    return formattedGroups

# take a regex group from formatInput and replace words to direct it towards the user ('me' becomes 'you', etc.)
# group is the current regex group, returns a group with the word swaps done to it
def wordSwaps(group):
    # wordSwaps stores all of the words that might need to be swapped out along with what they are swapped to
    # the swapped in values have 1s around them to denote a word has been swapped in
    # this prevents a word from being swapped in and then back out 
    # this also prevents phrases that have both 'you' and 'me' in them from behaving weirdly
    wordSwaps = [
        (r"\b(me)\b", "1YOU1"),
        (r"\b(you)\b", "1ME1"),
        (r"\b(yourself)\b", "1MYSELF1"),
        (r"\b(myself)\b", "1YOURSELF1"),
        (r"\b(my)\b", "1YOUR1"),
        (r"\b(our)\b", "1YOUR1"),
        (r"\b(your)\b", "1MY1"),
        (r"\b(mine)\b", "1YOURS1"),
        (r"\b(yours)\b", "1MINE1")
    ]
    # check if any of the words in the swap list are present in the current group and do the swap
    for swapTuple in wordSwaps:
        searchFor = re.compile(swapTuple[0], re.IGNORECASE)
        group = searchFor.sub(swapTuple[1], group)
    # remove the 1s that were left around the swapped in words
    return re.sub(r"(1)",'', group)

# check if the current input, inputStr is the user ending the conversation using 'bye' or 'goodbye'
# return True if goodbye, else False
def checkGoodbye(inputStr):
    inputStr = inputStr.upper()
    if inputStr == 'GOODBYE' or inputStr == 'BYE':
        return True
    return False

# lists of words used by readStatement
# in class, we discussed what kinds of things someone would talk about in therapy and the main ones were family (and people in general), school, and work
family = ['husband', 'wife', 'spouse', 'sister', 'brother', 'son', 'daughter', 'children', 'child', 'parent', 'sibling', 'mom', 'dad', 'mother', 'father']
school = ['class', 'professor', 'teacher', 'instructor', 'classes', 'professors', 'teachers', 'instructors']
people = ['friend', 'boyfriend', 'girlfriend', 'roommate', 'friends']
work = ['boss', 'job', 'work']

# readStatement deals with phrases of the form 'My {object}' and provides special responses if it recognizes the subject
# returns the {object} value so it can be used as the value for the memory variable for the next input
def readStatement(inputStr, memory, name):
    pattern = r"\b(My) (.*)"
    searchFor = re.compile(pattern, re.IGNORECASE)
    regexGroups = searchFor.search(inputStr).groups()
    object = regexGroups[1].lower()
    # if a word in the family list is used, respond accordingly (the word 'family' is not in the list)
    if object in family:
        selection = random.choice(['Do you want to say something about anyone else in your family?', f'Tell me about your {object}.'])
    # if the word family is used, ask for clarification for who in the family
    elif object == 'family':
        selection = random.choice(['Is there a specific family member you want to talk about?', 'Tell me about your family.'])
    elif object in people:
        selection = random.choice(['Are there any other people you want to talk about?', f'Tell me about your {object}.'])
    elif object in school:
        selection = random.choice(['Is there anything else about school that you want to talk about?', f'Tell me about your {object}.'])
    elif object == 'school':
        selection = random.choice(['Is there anything specific about school you want to talk about?', 'Tell me about your experience with school.'])
    elif object in work:
        selection = random.choice(['Is there anything else about work you want to talk about?', f'Tell me about your {object}.'])
    # if the subject referenced is not in one of the four lists, use a more general response
    else:
        selection = random.choice([f'Your {object}?', f'Tell me more about your {object}'])
    # randomly decide whether or not to use the user's name and then print the response
    # fixCapitalization makes sure the sentence starts with a capitalized name followed by a sentence where only "I" or "I'm" is capitalized
    nameSelection = random.choice([selection, fixCapitalization(f'{name}, {selection}')])
    print(nameSelection)
    # object will be the new value of the memory variable
    return object

# fixCapitalization takes a sentence and returns that sentence where only the first word, "I", and "I'm" are capitalized
# this is used when the user's name is prepended to ELIZA's response to make sure capitalization wasn't messed up
def fixCapitalization(sentence):
    sentence = sentence.lower().capitalize()
    sentence = re.sub(r'\bi\b','I', sentence)
    sentence = re.sub(r"\bi'm\b", "I'm", sentence)
    return sentence

# the main function of the program - runs when the file is loaded
# starts by greeting the user and asking for a name, stops when 'bye' or 'goodbye' is received
def runEliza():
    print("Hello, I'm a psychotherapist. What is your name?")
    inputStr = input()
    # if an empty string or whitespace is entered as a name, ask again for name
    # 'not inputStr' check is inputStr is empty, isspace checks if whitespace
    # https://docs.python.org/3.10/library/stdtypes.html?highlight=isspace#str.isspace
    # https://stackoverflow.com/a/53522
    while not inputStr or inputStr.isspace():
        print("Hello, I'm a psychotherapist. What is your name?")
        inputStr = input()
    name = readName(inputStr)
    print(f"Hello {name}, how can I help you today?")
    inputStr = input()
    memory = None
    # taking input and responding until checkGoodbye detects a goodbye message
    while(not checkGoodbye(inputStr)):
        # if readStatement or pronounStatement returns something, 
        # it is stored in the memory variable for the next response
        memory = elizaRespond(inputStr, memory, name)
        inputStr = input()
    print(f"Goodbye {name}. Thank you for talking to me")

# call runEliza when the eliza.py file is run
if __name__ == "__main__":
        runEliza()