#! python2
#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Imports
import urllib
#import re
import io
import os
import urllib2
import bs4
import requests
import json
import sys
import argparse
import platform
import random
from PIL import Image

successful_download = 'Successfully downloaded comic '
successful_downloads = 'Comics downloaded successfully'

## Comic instance class
class ComicInstance():
    """
    This class contains the methods that allow the search and download of a concrete xkcd comic
    from its number
    """
    def __init__(self, comic_to_grab = ''):
        self.comic_number = comic_to_grab
        self._URL_init = 'https://xkcd.com/'
        if comic_to_grab == '':
            self._URL_end = 'info.0.json'
            self._EXPLAIN_TAIL_URL = 'Main_Page'
        else:
            self._URL_end = '/info.0.json'
            self._EXPLAIN_TAIL_URL = self.comic_number
        self._EXPLAIN_URL = 'http://www.explainxkcd.com/wiki/index.php/'
        self._IMG_EXTENSION = {'jpg':'JPEG', 'png':'PNG', 'gif':'GIF'}
        self._IMG_DIR = os.getcwd() + '/comic_images/' 
        self.image_url, self.comic_name = self.get_comic_data()
        self.txt_explanation = None

    # Grab comic data name from number
    def get_comic_data(self):
    	"""
    	This method obtains the comic image data from the comic number.
    	To do so, it builds the api url for the asked comic number and queries
    	the xkcd webpage. From the JSON response it extracts the comic title
    	and the image url.

    	:return: image url, title or None, None
    	"""
        url = self._URL_init \
            + self.comic_number \
            + self._URL_end
        resp = requests.get(url)
        if resp.status_code == 200:
            data = json.loads(resp.text)             
            return data['img'], data['safe_title'].replace('/', '_')    
        return None, None          

    # Download image
    def download_image(self):
        try:
	        # retrieve image from the url
            # this downloads and saves the image in the script path with name comic_name
            page = urllib.URLopener()
            image = page.retrieve(self.image_url,
                         self.comic_name)
            self._save_comic()
            return True
        except:
            print "An error ocurred while downloading comic " \
                  + str(self.comic_number)
            return False
	
    # Save image
    def _save_comic(self):
        with Image.open(self.comic_name) as image:
        # TODO -> Windows check
            if not os.path.exists(self._IMG_DIR):
                os.makedirs(self._IMG_DIR)
            image.save(self._IMG_DIR + self.comic_name + "." + self.image_url[-3:], self._IMG_EXTENSION[self.image_url[-3:]])
        os.remove(self.comic_name)

    # Show image
    def show_image(self):
        if platform.system() == 'Linux':
            im = Image.open(self._IMG_DIR + self.comic_name + self.image_url[-4:])
            im.show()
        else:
            os.startfile(self._IMG_DIR + '\\'+self.comic_name)

    def _get_soup_from_url(self, url):
        opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        response = opener.open(url)
        return bs4.BeautifulSoup(response.read(),'html.parser')

    # Get explanation from explainxkcd
    def get_explanation(self):
        if self.txt_explanation is None:
            # build url for explanation
            url = self._EXPLAIN_URL + self._EXPLAIN_TAIL_URL
            # get html from url
            soup = self._get_soup_from_url(url)

            div = soup.find('div', attrs = {'id':'mw-content-text', 'class':'mw-content-ltr'})

            # Find all of the text between paragraph tags and strip out the html
            paragraph_text = [paragraph.getText() for paragraph in div.find_all('p')]
            # make sure all characters are ascii encoded
            explanation_text = [text.encode('ascii','ignore') for text in paragraph_text] 
            if self.comic_number != '':
                explanation = '\n'.join(map(str, explanation_text))

            else:
                exp=[]
                i = 2
                while explanation_text[i] != 'Is this out of date? Clicking here will fix that.\n':
                        exp += explanation_text[i]
                        i+=1
                explanation = '\n'.join(map(str, exp))
            self.txt_explanation = explanation
            return explanation
        else:
            return self.txt_explanation


## Command line argument parsing
parser = argparse.ArgumentParser(description='Program to download xkcd comics')

parser.add_argument('comics', metavar = 'N', type = str, nargs = '*', help = 'Comic numbers. Can be a combination of ranges: i-j and individual comics: i, or left blank which, when combined with the flag -g will download the latest comic')
parser.add_argument('-g','--get', help = 'get comic images', action = 'store_true')
parser.add_argument('-s','--show', help = 'show comic images', action = 'store_true')
parser.add_argument('-e','--explain', help = 'get comic explanations', action = 'store_true')
parser.add_argument('-a','--all', help = 'download all published comics', action = 'store_true')
parser.add_argument('-r','--random', help = 'download a random comic', action = 'store_true')

args = parser.parse_args()

## Helper functions
def get_max_comic(file):
    current_max = None
    increase = True
    with open(file, "r") as f:
        current_max = f.readline()
    while increase:
        with open(file, "w") as f:
            f.write(current_max)
        current_max = str(int(current_max) + 1)
        comic = ComicInstance(current_max)
        if comic.get_comic_data()[0] is None:
            increase = False

    return int(current_max) 

def pretty_print(comic):
    if platform.system() == 'Linux':
        rows, cols = os.popen('stty size', 'r').read().split()
        free_side_cols = (int(cols) - len(comic.comic_name))/2
        print '-' * free_side_cols + comic.comic_name + '-' * free_side_cols + '\n'
        print comic.get_explanation()
        print '-' * int(cols) + '\n'
    else:
        print comic.comic_name + '\n'
        print comic.get_explanation()

def show_and_explain(args, comic, pretty_format=True):
    if args.show:
        comic.show_image()
    if args.explain:
        if pretty_format:
            pretty_print(comic)
        else:
            print comic.get_explanation()

def download_all_comics(args):
    # download all comics
    index = 1
    while True:
        if index != 404:
            comic = ComicInstance(str(index))
            downloaded = comic.download_image()
            if downloaded:
                print successful_download + str(index)
                show_and_explain(args, comic)
            else:
                print 'Exiting'
                return False
        index += 1

def download_random_comic(args):
    min_comic = 1
    max_comic = get_max_comic('xkcd_max.txt') + 1
    comic = ComicInstance(str(random.choice(range(min_comic, max_comic))))
    downloaded = comic.download_image()
    if downloaded:
        print successful_download
        show_and_explain(args, comic)

def download_last_comic(args):
    last_comic = ComicInstance('')
    download_succesful = last_comic.download_image()
    if download_succesful:
        print successful_download
        show_and_explain(args, last_comic)

def download_specific_comics(args):
    # Check if there was a comic range specified in the arguments
    if any('-' in r_comic for r_comic in args.comics):
        # get lowerbounds and upperbounds of ranges in sublists inside the list of desired comic numbers
        comics_range = [r.split('-') for r in args.comics]
        # generate the desired ranges and store them as sublists inside the list of desired comic numbers
        comics = [range(int(i[0]), int(i[1]) + 1) if len(i) > 1 else int(i[0]) for i in comics_range]
        # Flatten list of lists to get all individual comic numbers to download
        flatten = lambda *args: (result for mid in args for result in (flatten(*mid) if isinstance(mid, list) else (mid,)))
        comics_n = list(flatten(comics))
    else:        
        comics_n = [int(comic) for comic in args.comics]
    
    comics = [ComicInstance(str(comic_n)) for comic_n in comics_n]
    images = [comic.download_image() for comic in comics]
    
    if False not in images:
        print successful_downloads 
        for comic in comics:
            show_and_explain(args, comic)

def download_comic():
    comics = []
    get_more_comics = True
    while get_more_comics:
        comic_n = raw_input("Enter comic number: ")
        comics += [ComicInstance(comic_n)]
        s = comics[-1].download_image()
        if s:
            print successful_downloads
            comics[-1].show_image()                        
            pretty_print(comics[-1])

        more_comics = raw_input("Want to search for another comic? (y/n): ")
        if more_comics != 'y':
            get_more_comics = False
            sys.exit()

## Main function
def main():
    if args.all:
        download_all_comics(args)

    elif args.random:
        download_random_comic(args)
   
    elif args.get and args.comics != []:
        download_specific_comics(args)

    elif args.get and args.comics == []:
        download_last_comic(args)

    else: 
        download_comic()
    return

# Main program
if __name__=="__main__":
    main()
