import sys
import os

import re
import pandas as pd
import nltk

from TextRank import TextRank # own packages at the end


class RawText(object):
    """
    The class that will be used to perform all operations on the downloaded texts.
    """

    def __init__(self, file_name):
      self.file_name = file_name


    def _read_file(self):
        """
        :param file_name:  given filename after raw_data_path to be read.
        :return: the url and the text that it found in the given file
        """

        file_to_read = open(raw_data_path + self.file_name, 'r')
        raw_text = file_to_read.read()
        file_to_read.close()
        url = raw_text.split('\n')[0]
        text = str(raw_text.split('\n')[1:])
        # tuples can not be overwritten
        # see https://www.pythonlearn.com/html-008/cfbook011.html
        return list((url, text))

    def _get_text(self):
        """
        Just returns the text.
        :param file_name: given filename from which text will be extracted.
        :return:
        """

        text = self._read_file(self.file_name)[1]
        return text

    def _get_url(self):
        """
        Just returns url.

        :param file_name:
        :return:
        """
        url = self._read_file(self.file_name)[0]
        return url

    def print_text(self):
        """
        Uses read_file to print the text body of the input.
        :param file_name: given filename after raw_data_path to be printed.
        :return:
        """

        text = self._get_text(self.file_name)
        print(text)

    def print_url(self):
        """

        :param file_name: given filename from which url will be extracted.
        :return:
        """

        url = self._get_url(self.file_name)
        print(url)

    def text_rank_sentences(self, no_jobs=5):
        """
        Uses Text_Rank.py to return the most important sentences.
        :param file_name: given filename after raw_data_path to be read.
        :param no_jobs: How many sentences to be returned (AS A LIST)

        :return:
        """

        text = self._get_text(self.file_name)
        sentences_list = TextRank.fit(text, n_jobs=no_jobs)
        return sentences_list

    def print_ranked_sentences(self):
        sentences_list = self.text_rank_sentences(self.file_name)
        for id_sent, sentence in enumerate(sentences_list):
            sentence = sentence.replace(u'\xa0', u' ')
            print('{}:  {}'.format(id_sent + 1, sentence))

    def get_sentences_with_numbers(self):
        """
        Returns sentences that have numbers in it.
        :param file_name: given filename after raw_data_path to be read.
        :return:
        """

        text = self._get_text(self.file_name)
        sentences_with_numbers = []
        for sent in nltk.sent_tokenize(text):
                if bool(re.search(r'\d', sent)):
                    sent = sent.replace(u'\xa0', u' ')
                    sentences_with_numbers.append(sent)

        return sentences_with_numbers

    def get_number_and_keyword_sentences(self, keyword_list_1, keyword_list_2=None):
        """
        Returns all sentences that have numbers in them AND include some specified keywords.
        :param file_name:
        :param keyword_list_1: The ultimate keyword list.
        :param keyword_list_2: The topic-specific keyword list.
        :return:
        """
        print(self.file_name)

        # # NOTE: why is keyword_list_2 not used anywhere?
        number_sentences = self.get_sentences_with_numbers(self.file_name)
        return_list = []
        for sentence in number_sentences:
            if any(word in sentence.lower() for word in keyword_list_1):
                return_list.append(sentence)
            elif any(word in sentence.lower() for word in keyword_list_2):
                return_list.append(sentence)
            else:
                pass
        return return_list

    @staticmethod
    def loop_through_sentences(sentences_list, url):
        """
        The interface shown for each sentence
        :param sentences_list:
        :param url:
        :param file_name:
        :return:
        """

        help_string = '''
        This is the help message.
        Press 'y' to add sentence to the saved sentences.
        Press 'n' to go to next sentence
        Press 'h' for help message
        Press 'q' to quit()
        '''

        yes_sentences = []
        for sentence in sentences_list:
            if sentence not in list(pd.read_csv(project_folder + 'urls_and_sentences.csv')['sentence']):
                print(sentence)
                answer = input('y, n, h, q: ')
                if answer == 'y':
                    yes_sentences.append(sentence)
                    try:
                        sub_df = pd.read_csv(project_folder + 'urls_and_sentences.csv')
                    except Exception:
                        sub_df = pd.DataFrame(columns=['url', 'sentence'])
                    sub_df.loc[len(sub_df)] = [url, sentence]

                    sub_df.to_csv(project_folder + 'urls_and_sentences.csv', index=False)
                    print('Sentence added')
                elif answer == 'n':
                    pass
                elif answer == 'h':
                    print(help_string)
                elif answer == 'q':
                    print('Quitting!')
                    sure = input('SURE?')
                    if sure == 'y':
                        sys.exit(0)
                    else:
                        pass

            else:
                pass
        done_file = open(project_folder + 'done_links.txt', 'a')
        done_file.write('{}\n'.format(url))
        print('You are done with {}'.format(self.file_name))

    def interface(self, numbered_sentences=True, text_ranked=True, numbered_and_keywords=False):
        """
        Takes the file and shows the user one by one, to decide if they are important
        :param file_name:
        :param numbered_sentences:
        :param text_ranked:
        :param numbered_and_keywords:
        :return:
        """

        ultimate_keyword_list = [
            'thousand',
            'thousands',
            'hundred',
            'hundreds',
            'millions',
            'million',
            'euro ',
            'dollar',
            'user',
            'users',
            'tonnes',
            'tonne',
            'liter',
            'litre',
            'liters',
            'downloads',
            'likes',
            'eur',
            'usd'
        ]

        sentences_list = []
        # All sentences from the Text_Rank
        if text_ranked:  # this evaluates as True
            for sentence in self.text_rank_sentences(self.file_name):
                sentences_list.append(sentence)
        else:
            pass
        # All sentences that have some numbers in them
        if numbered_sentences:
            for sentence in self.get_sentences_with_numbers(self.file_name):
                sentences_list.append(sentence)
        else:
            pass
        #
        if numbered_and_keywords:
            for sentence in self.get_number_and_keyword_sentences(
                    file_name=self.file_name, keyword_list_1=ultimate_keyword_list , keyword_list_2=None):
                sentences_list.append(sentence)

        print('There are {} sentences'.format(len(sentences_list)))
        url = self._get_url(self.file_name)
        done_list_file = open(project_folder + 'done_links.txt', 'r')
        done_url_list = done_list_file.read().split('\n')
        done_list_file.close()

        if url not in done_url_list:
            if os.path.exists(processed_data_path + self.file_name):
                print('This file has already been processed.')
            answer = None
            while answer not in ['Start', 'quit']:
                answer = input('What now? ')
                if answer == 'Start':
                    self.loop_through_sentences(sentences_list, url, self.file_name)
                elif answer == 'quit':
                    sys.exit('You have decided to quit.')
                else:
                    print('\'Start\' to start processing or \'quit\' for quitting: ')
        else:
            print('Seems like this page has been processed before.')


"""
Asking for project name, and creating folders:
project folder
"""

project_name = input('Project name:')
output_path = os.path.join(os.path.dirname('__file__'), '..', ) + '/output/'
try:
    project_folder = os.path.join(os.path.dirname('__file__'), '..', ) + '/output/{}/'.format(project_name)
except:
    sys.exit('Please run Text_downloader.py first')

    '''
except:
    os.makedirs(output_path + '/{}/'.format(project_name))
    project_folder = os.path.join(os.path.dirname('__file__'), '..', ) + '/output/{}/'.format(project_name)
    '''
if os.path.exists(project_folder + '/raw_data/'):
    raw_data_path = project_folder + '/raw_data/'
else:
    print('raw_data folder does not exist, run Text_downloader.py, to create one!' )
if os.path.exists(project_folder + '/processed_data/'):
    pass
else:
    os.makedirs(project_folder + '/processed_data/')
processed_data_path = project_folder + '/processed_data/'

'''
Checking if service files exist.
'''
if os.path.exists(project_folder + 'done_links.txt'):
    pass
else:
    done_links_file = open(project_folder + 'done_links.txt', 'w')
    done_links_file.close()
    print('Created done_links.txt')
if os.path.exists(project_folder + 'urls_and_sentences.csv'):
    pass
else:
    df = pd.DataFrame(columns=['url', 'sentence'])
    df.to_csv(project_folder + 'urls_and_sentences.csv', index=False)
    print('Created urls_and_sentences.csv')
done_links_path = project_folder + 'done_links.txt'
urls_and_sentences_path = project_folder + 'urls_and_sentences.csv'

input_file_name = input('Enter the number which txt you want to process: ') + '.txt'
do_numbered = input('Do you want to use numbered sentences? ')
if do_numbered == 'y':
    do_numbered = True
else:
    do_numbered = False
do_text_rank = input('Do you want to use text_ranked sentences? ')
if do_text_rank == 'y':
    do_text_rank = True
else:
    do_text_rank = False
do_num_and_key = input('Do you want to search for sentences with numbers AND keywords? ' )
if do_num_and_key == 'y':
    do_num_and_key = True
else:
    do_num_and_key = False


X = RawText(file_name=input_file_name)

interface(, numbered_sentences=do_numbered, text_ranked=do_text_rank, numbered_and_keywords=do_num_and_key)
