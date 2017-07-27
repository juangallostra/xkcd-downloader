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
    '''
    This class contains the methods that allow the search and download of a concrete xkcd comic
    '''
    def __init__(self, comic_to_grab='', show_image=True):
        self.comic_number = comic_to_grab
        self._URL_init = 'https://xkcd.com/'
        if comic_to_grab == '':
            self._URL_end = 'info.0.json'
        else:
            self._URL_end = '/info.0.json'
        self._IMG_EXTENSION = {'jpg':'JPEG', 'png':'PNG'}
        self.image_url, self.comic_name = self.grab_image_url()
        self.show = show_image
        self.txt_explanation = None

    # Grab comic image name from number
    def grab_image_url(self):
        # build the url for the asked number comic and, once opened, read its html content.
        url = self._URL_init \
             +self.comic_number \
             +self._URL_end
        resp = requests.get(url)
        if resp.status_code == 200:
            data = json.loads(resp.text)             
            return data['img'], data['safe_title']    
        return None, None          

    # Download image
    def download_image(self):
        try:
            # retrieve image from the url
            # this downloads and saves the image in the script path with name comic_name
            i = urllib.URLopener()
            s=i.retrieve(self.image_url,
                         self.comic_name)
            with Image.open(self.comic_name) as image:
                image.save(self.comic_name, self._IMG_EXTENSION[self.image_url[-3:]])
            # show comic in UI
            return True
        except:
            print "An error ocurred while downloading comic " \
                  +str(self.comic_number)
            return False
    # Show image
    def show_image(self):
        if platform.system() == 'Linux':
            im = Image.open(self.comic_name)
            im.show()
        else:
            os.startfile(os.getcwd()+'\\'+self.comic_name)

    # Get explanation from explainxkcd
    def get_explanation(self):
        # build url for explanation
        if self.comic_number != '':
            url='http://www.explainxkcd.com/wiki/index.php/'+self.comic_number
        else:
            url='http://www.explainxkcd.com/wiki/index.php/Main_Page'

        # get html from url
        opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        response = opener.open(url)
        page = bs4.BeautifulSoup(response.read(),'html.parser')

        div = page.find('div', attrs={'id':'mw-content-text', 'class':'mw-content-ltr'})

        # Find all of the text between paragraph tags and strip out the html
        text = [t.getText() for t in div.find_all('p')]
        text = [t.encode('ascii','ignore') for t in text] # make sure all characters are ascii encoded

        if self.comic_number != '':
            explanation = '\n'.join(map(str, text))

        else:
            exp=[]
            i=2
            while text[i]!='Is this out of date? Clicking here will fix that.\n':
                    exp += text[i]
                    i+=1
            explanation = '\n'.join(map(str, exp))
        self.txt_explanation = explanation
        return explanation


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
        current_max = str(int(current_max)+1)
        comic = ComicInstance(current_max, False)
        if comic.grab_image_url()[0] is None:
            increase = False

    return int(current_max) 

## Main function
def main():
    if args.all:
        # download all comics
        index = 1
        while True:
		if index != 404:
            		comic = ComicInstance(str(index), False)
            		downloaded = comic.download_image()
            		if downloaded:
                		print successful_download+str(index)
                		if args.show:
                    			comic.show_image()
            		else:
                		print 'Exiting'
                		return 
            	index += 1

    elif args.random:
        min_comic = 1
        max_comic = get_max_comic('xkcd_max.txt')+1
        comic = ComicInstance(str(random.choice(range(min_comic, max_comic))))
        downloaded = comic.download_image()
        if downloaded:
            print successful_download
            if args.show:
                comic.show_image()
   
    elif args.get and args.comics != []:
            # Check if there was a comic range specified in the arguments
            if any('-' in r_comic for r_comic in args.comics):
                    # get lowerbounds and upperbounds of ranges in sublists inside the list of desired comic numbers
                    comics_range = [r.split('-') for r in args.comics]
                    # generate the desired ranges and store them as sublists inside the list of desired comic numbers
                    comics = [range(int(i[0]),int(i[1])+1) if len(i)>1 else int(i[0]) for i in comics_range]
                    # Flatten list of lists to get all individual comic numbers to download
                    flatten = lambda *args: (result for mid in args for result in (flatten(*mid) if isinstance(mid, list) else (mid,)))
                    comics_n = list(flatten(comics))
            else:        
                    comics_n = [int(comic) for comic in args.comics]
            
            comics = [ComicInstance(str(comic_n), args.show) for comic_n in comics_n]
            images = [comic.download_image() for comic in comics]
            
            if False not in images:
                    print successful_downloads 
            
            explanations = []
            if args.explain:
                    explanations = [comic.get_explanation() for comic in comics]
                    for comic in comics:
                            print '-'*30+comic.comic_name+'-'*30+'\n'
                            print comic.txt_explanation
                            print '-'*80+'\n'
                            
            for comic in comics:
                    if args.show:
                            comic.show_image()
                            
    elif args.get and args.comics == []:
            last_comic = ComicInstance('',True)
            download_succesful = last_comic.download_image()
            if download_succesful:
                    print successful_download
                    if args.show:
                            last_comic.show_image()                        
            if args.explain:
                    print last_comic.get_explanation()
    else: 
            comics = []
            get_more_comics = True
            while get_more_comics:
                comic_n = raw_input("Enter comic number: ")
                comics += [ComicInstance(comic_n)]
                s=comics[-1].download_image()
                if s:
                    print successful_downloads
                    comics[-1].show_image()                        
                    print comics[-1].get_explanation()
        
                more_comics = raw_input("Want to search for another comic? (y/n): ")
                if more_comics != 'y':
                        get_more_comics = False
                        sys.exit()
    return

# Main program
if __name__=="__main__":
        main()
