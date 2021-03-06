# coding: utf-8
# SNLP - SoSe 2019 - ASSINGMENT IV

import math
import re
from collections import Counter
from matplotlib import pyplot as plt
import numpy as np


def tokenize(text):
    "List all the word tokens (consecutive letters) in a text. Normalize to lowercase."
    return re.findall('[a-z]+', text.lower())


def word_ngrams(sent, n):
    """Givne a sent as str return n-grams as a list of tuple"""

    sent = tokenize(sent)
    if n > 1:
        sent.insert(0, '<s>')
        sent.append('</s>')
    ngrams = []
    if n == 1:
        for i in range(len(sent)):
            ngrams.append((sent[i],))
    else:
        for i in range(1, len(sent)):
            ngrams.append((sent[i - 1], sent[i]))

    return ngrams


class ngram_LM:
    """A class to represent a language model."""

    def __init__(self, n, ngram_counts, vocab, unk=False):
        """"Make a n-gram language model, given a vocab and
            data structure for n-gram counts."""

        self.n = n
        self.vocab = vocab
        self.V = len(vocab)
        self.ngram_counts = ngram_counts
        if n > 1:
            self.unigram_counts = Counter()
            for word in self.ngram_counts.items():
                self.unigram_counts.update({(word[0][0],): word[1]})

            assert sum(ngram_counts.values()) == sum(
                self.unigram_counts.values())

    def perplexity(self, T, alpha):
        res = 0
        M = 0
        for sent in T:
            M += len(sent)
            for word in sent:
                res += self.logP(word[0], word[-1 + self.n], alpha=alpha)
        return 2**(-res / M)

    def unseen(self, T):
        unseen = 0
        M = 0
        for word in T.keys():
            if self.ngram_counts[word] == 0:
                unseen += 1
        return unseen / len(T)

    def estimate_prob(self, history, word):
        if self.n == 1:
            return self.ngram_counts[(word,)] / sum(self.ngram_counts.values())

        if self.n > 1:
            return self.ngram_counts[(history, word)] / self.unigram_counts[(history,)]

    def estimate_smoothed_prob(self, history, word, alpha=0.5):
        """
        Estimate probability of a word given a history with Lidstone smoothing.

        :param history: a predecessor word: '' - for n=1 and string - for n=2
        :param word: a word conditioned on a predecessor word; string
        :param alpha: a smoothing parameter in (0,1]; float
        :return: the probability of a word conditioned on a predecessor word; float
        """
        if self.n == 1:
            return (alpha + self.ngram_counts[(word,)]) / \
                   (alpha * self.V + sum(self.ngram_counts.values()))

        if self.n > 1:
            return (alpha + self.ngram_counts[(history, word)]) / \
                   (alpha * self.V + self.unigram_counts[(history,)])

    def logP(self, history, word, alpha=0.5):
        """Return base-2 log probablity."""

        prob = self.estimate_smoothed_prob(history, word, alpha=alpha)
        return math.log(prob, 2)

    def score_sentence(self, sentence):
        """Given a sentence, return score."""

        sent = tokenize(sentence)
        sent.insert(0, '<s>')
        sent.append('</s>')
        M = len(sent)
        score = 0
        for i in range(1, M):
            score += - self.logP(sent[i - 1], sent[i])
        return score / M

    def prob_dist(self, h):
        prob = dict()
        for word in self.vocab:
            prob[word] = self.estimate_prob(h, word)
        return sorted(prob.items(), reverse=True, key=lambda kv: (kv[1], kv[0]))

    def test_LM(self):
        """Test whether or not the probability mass sums up to one."""

        print('\nTEST STARTED FOR n = ' + str(self.n))

        precision = 10 ** -8

        if self.n == 1:

            P_sum = sum(self.estimate_prob('', w) for w in self.vocab)
            assert abs(
                1.0 - P_sum) < precision, 'Probability mass does not sum up to one.'

        elif self.n == 2:
            histories = ['the', 'in', 'at', 'blue', 'white']

            for h in histories:
                P_sum = sum(self.estimate_prob(h, w) for w in self.vocab)

            for h in histories:
                P_sum = sum(self.estimate_prob(h, w) for w in self.vocab)
                assert abs(
                    1.0 - P_sum) < precision, 'Probability mass does not sum up to one for history' + h

        print('Test successful!')

    def test_smoohted_LM(self):
        """
        Test whether or not the smoothed probability mass sums up to one.
        """
        self.n = self.n
        precision = 10 ** -7
        print('\nTEST SMOOTHED LM STARTED FOR n = ' + str(self.n))

        if self.n == 1:
            P_sum = sum(self.estimate_smoothed_prob('', w) for w in self.vocab)
            assert abs(
                1.0 - P_sum) < precision, 'Probability mass does not sum up to one.'

        elif self.n == 2:
            histories = ['the', 'in', 'at', 'blue', 'white']
            for h in histories:
                P_sum = sum(self.estimate_smoothed_prob(h, w)
                            for w in self.vocab)
                assert abs(1.0 - P_sum) < precision, 'Probability mass does not sum up to one for history "{}"'.format(
                    h)

        print('Test successful!')


if __name__ == '__main__':
    plot = False
    corpora = '../corpora/corpus.sent.en.train'
    test_copora = '../corpora/lm_eval/'
    with open(corpora, 'r', encoding='utf-8') as file:
        content = file.readlines()
    corpus = tokenize(' '.join(content))
    VOCAB = set(corpus)

    unigram_COUNTS = Counter()
    bigram_COUNTS = Counter()
    for line in content:
        unigram_COUNTS.update(word_ngrams(line, 1))
        bigram_COUNTS.update(word_ngrams(line, 2))

    unigram_LM = ngram_LM(1, unigram_COUNTS, VOCAB)
    VOCAB.update(('<s>', '</s>'))
    bigram_LM = ngram_LM(2, bigram_COUNTS, VOCAB)

    for filename in ['simple.test', 'wiki.test']:
        bigram_corp = []
        unigram_corp = []
        unigrams = Counter()
        bigrams = Counter()
        file = open(test_copora + filename, 'r', encoding='utf-8')
        for line in file:
            unigram = word_ngrams(line, 1)
            bigram = word_ngrams(line, 2)
            unigram_corp.append(unigram)
            bigram_corp.append(bigram)
            unigrams.update(unigram)
            bigrams.update(bigram)
        print('\nunigram perplexities for ' + filename)
        print('with smoothed probabilities:')
        print(unigram_LM.perplexity(unigram_corp, 0.2))

        print('\nbigram perplexities for ' + filename)
        print('with smoothed probabilities:')
        print(bigram_LM.perplexity(bigram_corp, 0.2))

        print(
            '\n File ' + filename + ' has ' + str(unigram_LM.unseen(unigrams) * 100) + '\% unseen unigrams and ' + str(
                bigram_LM.unseen(bigrams) * 100) + '\% unseen bigrams')

        if plot:
            plt.figure(filename)
            log = []
            log2 = []
            for alpha in np.arange(0.1, 1.1, 0.1):
                log.append(unigram_LM.perplexity(unigram_corp, alpha))
                log2.append(bigram_LM.perplexity(bigram_corp, alpha))

            plt.subplot(2, 1, 1)
            plt.plot(np.arange(0.1, 1.1, 0.1), log)
            plt.title('unigrams of ' + filename, fontdict={'fontsize': 5})
            plt.ylabel('perplexity')
            plt.xlabel('alpha')

            plt.subplot(2, 1, 2)
            plt.plot(np.arange(0.1, 1.1, 0.1), log2)
            plt.title('bigrams of ' + filename, fontdict={'fontsize': 5})
            plt.ylabel('perplexity')
            plt.xlabel('alpha')

            plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95,
                                hspace=0.25, wspace=0.35)
            plt.savefig(filename + '_perplexity.png')
            plt.show()

    # Yoda's phrases assessment
    print('\nYODA\'S PHRASES ASSESSMENT')
    with open('../corpora/lm_eval/yodish.sent', 'r', encoding='utf-8') as yoda_file:
        yoda_phrases = yoda_file.readlines()

    with open('../corpora/lm_eval/english.sent', 'r', encoding='utf-8') as eng_file:
        eng_phrases = eng_file.readlines()

    scores = []
    # Handling phrases consisting of several sentences
    for phrase_y, phrase_en in zip(yoda_phrases, eng_phrases):
        p_y = re.findall(r'\w[\w\s,]+', re.sub(r'\.\.\.', '', phrase_y))
        p_en = re.findall(r'\w[\w\s,]+', re.sub(r'\.\.\.', '', phrase_en))
        if len(p_y) == 0:
            continue
        score_y = sum([bigram_LM.score_sentence(p) for p in p_y]) / len(p_y)
        score_en = sum([bigram_LM.score_sentence(p) for p in p_en]) / len(p_en)
        scores.append((phrase_y, phrase_en, score_y, score_en))

    print('\nSCORES OF THE PAIRS')
    for score in scores:
        print('\n{} | {}\n({} | {})'.format(
            score[0], score[1], score[2], score[3]))

    difference = [abs(score[2] - score[3]) for score in scores]

    min_dif = min(difference)
    max_dif = max(difference)
    phrase_min = (yoda_phrases[difference.index(min_dif)],
                  eng_phrases[difference.index(min_dif)])
    phrase_max = (yoda_phrases[difference.index(max_dif)],
                  eng_phrases[difference.index(max_dif)])
    print('\nMINIMUM DIFFERENCE:\n{}\n{}'.format(phrase_min, min_dif))
    print('\nMAXIMUM DIFFERENCE:\n{}\n{}'.format(phrase_max, max_dif))

    plt.figure(1)
    m = 1
    for pair in [phrase_min, phrase_max]:
        for phrase in pair:
            sent = tokenize(phrase)
            sent.insert(0, '<s>')
            sent.append('</s>')
            logs = []
            for i in range(1, len(sent)):
                logs.append(-bigram_LM.logP(sent[i - 1], sent[i]))
            plt.subplot(2, 2, m)
            plt.plot(range(1, len(sent)), logs)
            plt.xticks(np.arange(1, len(sent), 1))
            plt.yticks(np.arange(5, 16, 2.5))
            plt.title(phrase, fontdict={'fontsize': 5})
            plt.ylabel('Negative log probability')
            plt.xlabel('Word index')
            m += 1

    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95,
                        hspace=0.25, wspace=0.35)
    plt.savefig('logP(w,h).png')
    plt.show()
