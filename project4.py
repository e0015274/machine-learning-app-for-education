from nltk.corpus import wordnet as wn
from textblob import TextBlob, Word
from string import punctuation
import re


def get_similar_words(word):
    # In the absence of a better method, take the first synset
    synsets = wn.synsets(word, pos='n')

    # If there aren't any synsets, return an empty list
    if len(synsets) == 0:
        return []
    else:
        synset = synsets[0]

    # Get the hypernym for this synset (again, take the first)
    hypernym = synset.hypernyms()[0]

    # Get some hyponyms from this hypernym
    hyponyms = hypernym.hyponyms()

    # Take the name of the first lemma for the first 8 hyponyms
    similar_words = []
    for hyponym in hyponyms:
        similar_word = hyponym.lemmas()[0].name().replace('_', ' ')

        if similar_word != word:
            similar_words.append(similar_word)

        if len(similar_words) == 8:
            break

    return similar_words

def evaluate_sentence(sentence):
    if sentence.tags[0][1] == 'RB' or len(sentence.words) < 6:
        # This sentence starts with an adverb or is less than five words long
        # and probably won't be a good fit
        return None

    #punctuation= punctuation+'“'+'”'

    tag_map = {word.lower(): tag for word, tag in sentence.tags}

    replace_nouns = []
    for word, tag in sentence.tags:
        # For now, only blank out non-proper nouns that don't appear in the article title
        #if tag == 'NN':
        if tag == 'NN' and len(word) > 5:
            # Is it in a noun phrase? If so, blank out the last two words in that phrase
            for phrase in sentence.noun_phrases:
                if phrase[0] == '\'':
                    # If it starts with an apostrophe, ignore it
                    # (this is a weird error that should probably
                    # be handled elsewhere)
                    break

                if word in phrase:
                    # Blank out the last two words in this phrase
                    [replace_nouns.append(phrase_word) for phrase_word in phrase.split()[-2:]]
                    break

            # If we couldn't find the word in any phrases,
            # replace it on its own
            if len(replace_nouns) == 0:
                replace_nouns.append(word)
            break

    if len(replace_nouns) == 0:
        # Return none if we found no words to replace
        return None

    trivia = {
        #'title': 'some title',
        #'url': 'some url',
        'answer': ' '.join(replace_nouns)
    }

    if len(replace_nouns) == 1:
        # If we're only replacing one word, use WordNet to find similar words
        trivia['similar_words'] = get_similar_words(replace_nouns[0])[-4:]
    else:
        # If we're replacing a phrase, don't bother - it's too unlikely to make sense
        trivia['similar_words'] = []

    # Blank out our replace words (only the first occurrence of the word in the sentence)
    replace_phrase = ' '.join(replace_nouns)
    blanks_phrase = ('__________ ' * len(replace_nouns)).strip()

    expression = re.compile(re.escape(replace_phrase), re.IGNORECASE)
    sentence = expression.sub(blanks_phrase, str(sentence), count=1)

    trivia['question'] = sentence
    return trivia

def generate_qns(text):
    s = text
    s = s.replace('\n', ' ')
    s = TextBlob(s)
    s_sent = s.sentences
    t_sentences = []
    t_map = []
    for sentence in s_sent:
        t_map.append({word.lower(): tag for word, tag in sentence.tags})
        trivia = evaluate_sentence(sentence)
        if trivia:
            t_sentences.append(trivia)


    return t_sentences

