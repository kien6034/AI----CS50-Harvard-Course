import nltk
import sys
from os import listdir
from os.path import isfile, join
import string
import time
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 3

start_time = time.time()
def main():
    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    
    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    infos = dict()
    for f in listdir(directory):
        f_path = join(directory, f) 
        if isfile(f_path) and f.endswith(".txt"):
            with open(f_path, "r", encoding="utf8") as file:
                infos[f] = file.read()

    return infos

def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    
    words = []
    
    for word in nltk.word_tokenize(document):
        word = word.lower()
        #remove word if it is in puncutaion list
        if not all(char in string.punctuation for char in word):
            #remove stopwords
            if word not in nltk.corpus.stopwords.words("english"):
                words.append(word)

    return words
    

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    # documents = {
    #     '1.txt': ['he','she', 'he'],
    #     '2.txt': ['cry', 'he', 'sky'],
    #     '3.txt': ['she', 'she', 'sky']
    # }
    counts = dict()

  
    #calculate how many documents content each word
    for document in documents:
        appear_word = []
        for word in documents[document]:
            if word not in appear_word:
                if word in counts:
                    counts[word] += 1
                else:
                    counts[word] = 1
            appear_word.append(word)
    
    document_len = len(documents)
 
    idfs = dict()
    #calculate idf value
    for word in counts:
        idfs[word] = math.log(len(documents) / counts[word])  # e logarit 
    
    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """

    tf_idfs = dict()

    
    #calculate tf idfs
    for filename in files:
        tf_idfs[filename] = 0
        for word in query:
            if files[filename].count(word) != 0:
                tf_idfs[filename] += files[filename].count(word) * idfs[word]

    return [key for key, value in sorted(tf_idfs.items(), key=lambda item: item[1], reverse=True)][:n]  # reverse = true: decensding order
   

def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    
    sentence_rank = list()

    for sentence in sentences:
        sentence_weight = [sentence, 0, 0] # name + matching word measure + query term density

        for word in query:
            if word in sentences[sentence]:
                #Compute the idfs 
                sentence_weight[1] += idfs[word]

                #compute the query term density - proportion of word in the sentence that are also words in the query 
                sentence_weight[2] += sentences[sentence].count(word) / len(sentences[sentence])
        sentence_rank.append(sentence_weight)

    return [sentence for sentence, mwm, qtd in sorted(sentence_rank, key=lambda item: (item[1], item[2]), reverse=True)][:n]


if __name__ == "__main__":
    main()
