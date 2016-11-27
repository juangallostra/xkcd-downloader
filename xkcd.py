#! python2
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# imports needed
import urllib, re, io, os, urllib2, bs4
from PIL import Image

# Grab comic image name from number
def grab_name_from_number(number):
        # build the url for the asked number comic and, once opened, read its html content.
        url='http://xkcd.com/'+number+'/'
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
def download_image(comic_name):

        try:

                # build image url
                url='http://imgs.xkcd.com/comics/'+comic_name
                # retrieve image from the url
                # this downloads and saves the image in the script path with name comic_name
                i=urllib.URLopener()
                s=i.retrieve(url,comic_name)
                image=Image.open(comic_name)
                
                # convert and show comic in UI
                image.show()
                image.save(comic_name)
                return True
        except:
            print "An error ocurred while downloading comic"
            return False


def get_explanation(number):
        # build url for explanation

        if number != '':
                url='http://www.explainxkcd.com/wiki/index.php/'+number
                print url
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


        if number != '':
                explanation = '\n'.join(map(str, text))

        else:
                exp=[]
                i=2
                while text[i]!='Is this out of date? Clicking here will fix that.\n':
                        exp += text[i]
                        i+=1
                explanation = '\n'.join(map(str, exp))

        return explanation


# Main program
if __name__=="__main__":
    comic_n = raw_input("Enter comic number:")
    n=grab_name_from_number(comic_n)
    print n
    s=download_image(n)
    if s:
        print get_explanation(comic_n)
    
