import numpy as np
from nltk import word_tokenize, sent_tokenize
from operator import itemgetter
from nltk.corpus import stopwords


class TextRank(object):
    """
    compute the n more important sentences from a text

    To use simply run:

                TextRank.fit(
                    X,
                    n_jobs,
                    stop_words,
                    pretty_print
                )

    X = the text as a string
    n_jobs = the number of sentences to return
    stop_words = words to be ommited ('to', 'the', etc...). A default is set
    pretty_print = set this to True, to see a print out of the top n_jobs returned
    """

    @staticmethod
    def tokenize(the_string):
        """
        takes a chunk of text and tokenizes it by sentences and then by words
        :param the_string:
        :return: a list of lists [sentences[words]]
        """
        sentence_list = sent_tokenize(the_string)
        sentence_list = [word_tokenize(x) for x in sentence_list]

        return sentence_list

    @staticmethod
    def _euclidean_distance(u, v):
        """
        Returns the euclidean distance between vectors u and v. This is equivalent
        to the length of the vector (u - v).

        https://www.nltk.org/_modules/nltk/cluster/util.html
        """
        diff = u - v
        return np.sqrt(np.dot(diff, diff))

    @staticmethod
    def _cosine_distance(u, v):
        """
        Returns 1 minus the cosine of the angle between vectors v and u. This is
        equal to 1 - (u.v / |u||v|).

        https://www.nltk.org/_modules/nltk/cluster/util.html
        """
        return 1 - (np.dot(u, v) / (np.sqrt(np.dot(u, u)) * np.sqrt(np.dot(v, v))))

    @classmethod
    def _sentence_similarity(cls, sentence1, sentence2, stop_words=None):
        """
        Returns 1 minus the cosine of the angle between vectors v and u. This is
        equal to 1 - (u.v / |u||v|).

        https://www.nltk.org/_modules/nltk/cluster/util.html

        NOTE: 'euclidean_distance' can also be computed using nltk
        :param sentence1:
        :param sentence2:
        :param stop_words:
        :return:
        """
        if stop_words is None:
            stop_words = list()

        sentence1 = [word.lower for word in sentence1]
        sentence2 = [word.lower for word in sentence2]

        all_words = list(set(sentence1 + sentence2))

        # initialising vectors for the sentences
        vector1 = [0] * len(all_words)
        vector2 = [0] * len(all_words)

        # build the vector for the first sentence
        for word in sentence1:
            if word in stop_words:
                continue
            else:
                vector1[all_words.index(word)] += 1

        # build the vector for the second sentence
        for word in sentence2:
            if word in stop_words:
                continue
            else:
                vector2[all_words.index(word)] += 1

        return cls._cosine_distance(vector1, vector2)

    @classmethod
    def _build_similarity_matrix(cls, sentences, stop_words):
        """

        :param sentences:
        :param stop_words:
        :return:
        """
        # create an empty similarity matrix
        S = np.zeros((len(sentences), len(sentences)))

        for idx1 in range(len(sentences)):
            for idx2 in range(len(sentences)):
                if idx1 == idx2:
                    continue
                else:
                    S[idx1][idx2] = cls._sentence_similarity(sentences[idx1], sentences[idx2], stop_words)

        # normalise the matrix row-wise
        for idx in range(len(S)):
            S[idx] /= S[idx].sum()

        return S

    @staticmethod
    def _sentence_rank(M, eps=1.0e-8, d=.85):
        """
        the ranking sentences problem is solved by using Larry Page's algorithm PageRank.

        https://en.wikipedia.org/wiki/PageRank

        :param M:
        :param eps: quadratic error for v
        :param d: damping factor (default value .85) .15 is the probability of the sentence not being important
        :return: a vector of ranks such that v_i is the i-th rank from [0, 1]
        """
        N = M.shape[1]
        v = np.random.rand(N, 1)
        v = v / np.linalg.norm(v, 1)
        last_v = np.ones((N, 1), dtype=np.float32) * np.inf
        M_hat = (d * M) + (((1 - d) / N) * np.ones((N, N), dtype=np.float32))

        while np.linalg.norm(v - last_v, 2) > eps:
            last_v = v
            v = np.matmul(M_hat, v)
        return v

    @classmethod
    def fit(cls, X, n_jobs=5, stop_words=stopwords.words('english'), pretty_print=False):
        """
        X = a list of sentences [[w11, w12, ...], [w21, w22, ...], ...]
        top_n =
        stopwords = a list of stopwords

        :param X:
        :param n_jobs: the number of sentences the summary should contain
        :param stop_words: a list of words that should be ignored when computing sentence_similarity
                            luckily, nltk provides one for english.
        :return: summary of the top n_jobs most common sentences.
        """
        tokenized_sentences = cls.tokenize(the_string=X)
        similarity_matrix = cls._build_similarity_matrix(tokenized_sentences, stop_words=stop_words)
        sentence_ranks = cls._sentence_rank(similarity_matrix)

        # Sort the sentence ranks
        ranked_sentence_indexes = [item[0] for item in sorted(enumerate(sentence_ranks), key=lambda item: -item[1])]
        selected_sentences = sorted(ranked_sentence_indexes[:n_jobs])
        summary = itemgetter(*selected_sentences)(tokenized_sentences)

        if pretty_print:
            for idx, s in enumerate(summary):
                print("%s. %s" % ((idx + 1), ' '.join(s)))
            return [' '.join(x) for y in summary for x in [y]]

        return [' '.join(x) for y in summary for x in [y]]
