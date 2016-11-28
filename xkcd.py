#! python2
#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Imports
import urllib, re, io, os, urllib2, bs4, sys
from PIL import Image
import argparse



## Comic grabber class
class Comic_grabber():
        '''
        This class contains the methods that allow the search and download of a concrete xkcd comic
        '''
        def __init__(self, comic_to_grab='', show_image=True):
                self.comic_number = comic_to_grab
                self.comic_name = self.grab_name_from_number()
                self.show = show_image
                self.txt_explanation = None


        # Grab comic image name from number
        def grab_name_from_number(self):
                # build the url for the asked number comic and, once opened, read its html content.
                url='http://xkcd.com/'+self.comic_number+'/'
                text=urllib.urlopen(url).read()

                # regex for retrieving image name
                regex = 'http://imgs.xkcd.com/comics/(.*\.\w{1,3})'
                # search and return image name
                matches = re.findall(regex,text)
                if matches != []:
                        return matches[0]
                else:
                        return None


        # Download image
        def download_image(self):
                try:
                        # build image url
                        url='http://imgs.xkcd.com/comics/'+self.comic_name
                        # retrieve image from the url
                        # this downloads and saves the image in the script path with name comic_name
                        i=urllib.URLopener()
                        s=i.retrieve(url,self.comic_name)
                        image=Image.open(self.comic_name)
                        image.save(self.comic_name)
                        # show comic in UI
                        return True
                except:
                        print "An error ocurred while downloading comic"
                        return False

        def show_image(self):
                im = Image.open(os.getcwd()+'\\'+self.comic_name)
                im.show()

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

parser.add_argument('comics', metavar='N', type=int, nargs='*', help='comic numbers')
parser.add_argument('-g','--get', help='get comic images', action='store_true')
parser.add_argument('-s','--show', help='show comic images', action='store_true')
parser.add_argument('-e','--explain', help='get comic explanations', action='store_true')

args = parser.parse_args()

## Main function
def main():
        if args.get == True and args.comics != []:
                comics = [Comic_grabber(str(comic_n), args.show) for comic_n in args.comics]
                images = [comic.download_image() for comic in comics]
                explanations = []
                if args.explain == True:
                        explanations = [comic.get_explanation() for comic in comics]
                        for comic in comics:
                                print '-'*30+comic.comic_name+'-'*30+'\n'
                                print comic.txt_explanation
                                print '-'*80+'\n'
                for comic in comics:
                        if comic.show == True:
                                comic.show_image()
        else: 
                comics = []
                get_more_comics = True
                while get_more_comics:
                    comic_n = raw_input("Enter comic number: ")
                    comics += [Comic_grabber(comic_n)]
                    s=comics[-1].download_image()
                    if s:
                        print comics[-1].get_explanation()
            
                    more_comics = raw_input("Want to search for another comic? (y/n): ")
                    if more_comics != 'y':
                            get_more_comics = False
                            sys.exit()



# Main program
if __name__=="__main__":
        main()
    

    
    
