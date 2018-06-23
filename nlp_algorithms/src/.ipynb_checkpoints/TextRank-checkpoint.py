import numpy as np
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance


class TextRank(object):
    """
    compute the n more important sentences from a text
    """
    
    def __init__():
        """
        Initialises all the variables
        """
        pass
    
    def _build_similarity_matrix(self, sentences, stop_words):
        """
        """
        pass
    
    def _pageRank(S, eps=.0001, d=.85):
        """
        
        """
        P = np.ones(len(A)) / len(A)
        while True:
            new_P = np.ones(len(A)) * (1 - d) / (len(A)) + d * A.T.dot(P)
            delta = abs(new_P - P).sum()
            if delta <= eps:
                return new_P
            else:
                P = new_P
    
    def _sentence_similarity(sent1, sent2, stopwords=None):
        """
        Returns 1 minus the cosine of the angle between vectors v and u. This is
        equal to 1 - (u.v / |u||v|).
        
        https://www.nltk.org/_modules/nltk/cluster/util.html
        
        NOTE: 'euclidean_distance' can also be computed using nltk
        """
        if stopwords is None:
            stopwords = list()
        
        sent1 = [w.lower for w in sent1]
        sent2 = [w.lower for w in sent2] 
    
        all_words = list(set(sent1 + sent2))
        
        # initialising vectors for the sentences
        vector1 = [0] * len(all_words)
        vector2 = [0] * len(all_words)

        # build the vector for the first sentence
        for w in sent1:
            if w in stopwords:
                continue
            else:
                vector1[all_words.index(w)] += 1
        
        # build the vector for the second sentence
        for w in sent2:
            if w in stopwords:
                continue
            else:
                vector2[all_words.index(w)] += 1

        return cosine_distance(vector1, vector2)
    
    def textrank(self, sentences, top_n=5, stopwords=None):
        """
        sentences = a list of sentences [[w11, w12, ...], [w21, w22, ...], ...]
        top_n = how may sentences the summary should contain
        stopwords = a list of stopwords
        """
        S = build_similarity_matrix(sentences, stop_words) 
        sentence_ranks = pageRank(S)

        # Sort the sentence ranks
        ranked_sentence_indexes = [item[0] for item in sorted(enumerate(sentence_ranks), key=lambda item: -item[1])]
        selected_sentences = sorted(ranked_sentence_indexes[:top_n])
        summary = itemgetter(*selected_sentences)(sentences)
        return summary