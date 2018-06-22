import os
import requests
from bs4 import BeautifulSoup
import pickle
import numpy as np
import time


output_path = os.path.join(os.path.dirname('__file__'), '..') +'/output/'

def _random_sleep(minimum=3, maximum=10, sd=1):
        """
        sets a random time to sleep between requests, drawing random values from an exponential distribution
        if no parameters are set, the values [3, 10, 1] have been pre-specified

        :param minimum: the min time of the timer <float>
        :param maximum: the max time of the timer <float>
        :param sd: the standard deviation <float>
        :return: time.sleep( value drawn )
        """
        value = minimum + sd * np.random.exponential()
        if value > maximum:
            value = maximum + np.random.uniform(0, 1)
        time.sleep(value)


def make_request(url, method, **kwargs):
    """
    Request an article from The Evening Stardard
    
    :param url: the address to which the request is made
    :param method: the HTTP method ('get', 'post')
    :param **kwargs: any other arguments for the request builder
    :return: the html code of the page as a bs4 element
    """
    if method == 'post':
        response = requests.post(url, **kwargs)
    else:
        response = requests.get(url, **kwargs)

    # check for json
    if 'html' or 'text' in response.headers['Content-Type']:
        content = response.content
        response.close()
        return BeautifulSoup(content, 'html.parser')
    else:
        response.close()
        return None

def article_scraper(url, identifier):
    """
    calls the request function and parses the response
    :param url: the url of the article
    :param identifier: the hash.md5 identifier created when collecting initial urls
    :return: dicionary containing the data collected
    """
    soup = make_request(url=url, method='get', allow_redirects=False)  
    if soup:
        _random_sleep(
            minimum=1,
            maximum=5,
            sd=1
        )

        title = soup.find('h1', attrs={'class':'headline'}).text.strip()

        body = soup.find('div', attrs={'class':'body-content'})
        tag_box = soup.find('aside', attrs={'class':'tags'})

        if (body, tag_box):
            text = [x.text.strip() for x in body.findAll('p')]
            text = ''.join(x for x in text)

            tags = [tag.text.strip() for tag in tag_box.findAll('a')]

            answer_dict = {
                "Title" : title,
                "Link" : url,
                "Text" : text,
                "Tags" : tags
            }
            return answer_dict

def save_output(identifier, file_dict, checkfile=False):
    """
    save the output of the data scraped or if 'checkfile=True' it checks if the
    file has already been collected and passes it.
    
    """
    file_save_name = 'labeled_newspaper_articles.pickle'
    if checkfile:
        with open(output_path + file_save_name, 'rb') as handle:
            existing_files = pickle.load(handle)
        if identifier not in existing_files.keys():
            return True
        else:
            return False

    if os.path.isfile(output_path + file_save_name):
        with open(output_path + file_save_name, 'rb') as handle:
            existing_files = pickle.load(handle)

        if identifier not in existing_files.keys():
            existing_files.update({identifier : file_dict})
            with open(output_path + file_save_name, 'wb') as handle:
                pickle.dump(existing_files, handle,         protocol=pickle.HIGHEST_PROTOCOL)
    else:
        with open(output_path + file_save_name, 'wb') as handle:
            articles = {identifier : file_dict}
            pickle.dump(articles, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('../src/evening_standard_id_link_dict.pickle', 'rb') as handle:
    master_dict = pickle.load(handle)

for ID, partial_extension in list(master_dict.items()):
    try:
        not_scraped = save_output(ID, {}, checkfile=True)
        if not_scraped:
            print('not_scraped')
            data_dict = article_scraper('https://www.standard.co.uk' + partial_extension, ID)
            if data_dict:
                save_output(ID, data_dict)
                print('saved!')
            else:
                print('no data_dict...')
        else:
            print('already_done')
            pass
    except AttributeError as e:
        print(e)
        pass
