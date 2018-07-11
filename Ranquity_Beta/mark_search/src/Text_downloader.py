from TextRank import TextRank
import numpy
import nltk
import requests
import os 
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import numpy as np

output_path = os.path.join(os.path.dirname('__file__'), '..', ) + '/output/'
if os.path.exists(output_path):
    pass
else:
    os.makedirs(output_path)

class Scrape_Page(object):
    '''The object for the scraped page
    '''
    @staticmethod
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
    
    @staticmethod
    def _requesting(url, base_url, timeout = 10, parser = 'lxml'):
        '''
        Makes the request to the given url, escaopes after specified timeout.
        Returns BeautifulSoup object.
        :param url: The url to investigate
        :param timeout: timeout of the request
        :param parser: The parser used to create the soup object 
        '''
        try:
            response = requests.get(url, timeout = timeout)
        except:
            search_url = 'http://' + base_url + url
            response = requests.get(search_url, timeout = timeout)
        html = response.content
        response.close()
        soup = BeautifulSoup(html, 'lxml')
        return(soup)
    
    @classmethod
    def return_text(cls, url, base_url):
        '''
        Returns the text part as one string from the page
        :param url: The page url to be scraped
        '''
        soup = cls._requesting(url, base_url)
        p_list = soup.findAll('p')
        whole_text = '{}\n'.format(url)
        for tag in p_list:
            whole_text += tag.text
        return(whole_text)
    
    @classmethod
    def return_links(cls, url, base_url,  return_internal=True, only_from_tag = None):
        '''
        Returns the links in the give page.
        :param url: the page on which we are looking for links
        :param return_internal: return Links that are from the same mother domain?
        '''
        if only_from_tag != None:
            soup = cls._requesting(url, base_url)
            tags = soup.findAll(only_from_tag)
            link_list = []
            for tag in tags:
                if tag.find('a'):
                    link_list.append(tag.find('a').get('href'))
            return link_list
        else:
            soup = cls._requesting(url)
            all_a = soup.findAll('a')
            link_list = []
            for tag in all_a:
                try:
                    link_list.append(tag.get('href'))
                except:
                    pass
            if return_internal == False:
                home_url = urlparse(url)[1]


                for sub_link in link_list:
                    try:
                        if home_url == urlparse(sub_link)[1]:
                            link_list.remove(sub_link)
                            print(sub_link)

                    except Exception as e:

                        print(e)
                return link_list


            else:
                return link_list
    @classmethod
    def save_pages_text(cls, url, return_internal = False, project_name = None):
        '''
        Uses return_links to save the p tags of the html body
        :param: return_internal if true, it returns also links that are pointing to the same page
        :param: project_name is the name used for the folder
        '''
        base_url = urlparse(url)[1]
        link_list = Scrape_Page.return_links(url, base_url, only_from_tag= 'p', return_internal=return_internal)
        link_list = list(set(link_list))
        print('There are {} links to be scraped'.format(len(link_list)))
        if project_name!= None:
            pass
        else:
            project_name = input('Please provide project name: ')
        project_folder_name = output_path + '/{}/'.format(project_name)
        project_raw_data = project_folder_name + '/raw_data/'
        if not os.path.exists(project_folder_name):
            os.makedirs(project_folder_name)
            os.makedirs(project_raw_data)
        else:
            if not os.path.exists(project_raw_data):
                os.makedirs(project_raw_data)
        print(len(link_list))
        for l in link_list:
            try:    
                text = Scrape_Page.return_text(url=l, base_url=base_url)
                save_file = open(project_raw_data + '{}.txt'.format(len(os.listdir(project_raw_data))), 'w')
                save_file.write('{}'.format(text))
                save_file.close()
                cls._random_sleep()
                print('Done with {}'.format(len(os.listdir(project_raw_data))))
            except Exception as e:
                print(e)
        print('Finished')
        
home_url = input('Please provide the base url: ')
Scrape_Page.save_pages_text(home_url)
