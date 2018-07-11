import os 
import requests
from bs4 import BeautifulSoup
import re
from nltk import sent_tokenize
import pandas as pd

#Getting the preffered word_list
if os.path.isfile('search_words.txt') == False:
    print('Please create search_words.txt in order to have searchable words.')
with open('search_words.txt', 'r') as handle:
    raw_text = handle.read()
    yeswords = raw_text.split('YESWORDS: ')[1].split('NOWORDS')[0].replace('\n', '').replace(' ', '').split(',')[:-1]
    nowords =  raw_text.split('NOWORDS: ')[1].replace('\n', '').replace(' ', '').split(',')

basic_timeout = 10
output_path = os.path.join(os.path.dirname('__file__'), '..', ) +'/output/'

class NumberCollector(object):
    """
    This class is responsible for collecting the relevant sentences (Sentences that have numbers and also one of the keywords)
    """
    @classmethod
    def requesting(cls, url, timeout=10):       
        """
        Requesting for the site and returning the html.
        :param url: Url to be searched
        :param timeout: timeout after which request times out.
        """
        try:
            
            response = requests.get(url, timeout=timeout)
            html = response.content
            response.close()
            return html
        except Exception as e:
           # print(e)
            pass

    @classmethod
    def return_soup(cls, html):
        soup = BeautifulSoup(html, 'lxml')
        return soup

    @classmethod
    def numbered_sentences(cls, url, tag_to_search = 'p'):
        """
        Taking the scraped html and searching the p tags and looking for sentences that have both numbers 
        and a keyword in them.
        Keywords are taken from the search_word.txt
        """
        
        my_soup = cls.return_soup(cls.requesting(url))
        sentences = []
        for tag in my_soup.findAll(tag_to_search):
            for sentence in sent_tokenize(tag.text):
                sentences.append(sentence)

        useful_sentences = []
        for c, sentence in enumerate(sentences):
            if re.search(r'\d', sentence):
                if any(word in sentence.lower() for word in yeswords):
                    useful_sentences.append(sentence)

        print('There are {} useful sentences'.format(len(useful_sentences)))
        for sentence in useful_sentences:
            try:
                df = pd.read_csv(output_path + 'urls_and_sentences.csv')
            except:
                df = pd.DataFrame(columns=['url', 'sentence'])
            df.loc[len(df)] = [url, sentence]

            df.to_csv(output_path + 'urls_and_sentences.csv', index=False)
            
