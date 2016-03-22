#bookcover_collage


#Get list of books
#For each book, get bookcover
#Combine all images


import requests
import webbrowser
import os
import bs4
import shutil
import string
import warnings

def get_cover_image(title,verbose=True,directory='D:\Misc\Projects\Bookcover Collage\coverdir'):
    #Sample goodreads query URL: http://www.goodreads.com/search?utf8=%E2%9C%93&q=atlas+shrugged&search_type=books

    fname = directory + "\\" + title + ".jpg"

    #Check and make sure the image hasn't been pulled already
    if os.path.isfile(fname):
        if verbose:
           print('%s already exists' %fname)
        return 0
    
    #Form querystring by concatenating search_url_beg + search string + search_url_end
    search_url_beg = "http://www.goodreads.com/search?utf8=%E2%9C%93&q="
    search_url_end = "&search_type=books"
    search_title = string.join(title.split(),'+')
    search_url = search_url_beg + title + search_url_end
    
    if verbose:
        print('Pulling search page for %s : %s' %(title, search_url))

    #Get search page
    res = requests.get(search_url, verify=False)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "html.parser")

    #The first result is probably the one we want
    result = soup.select('.bookTitle')[0].get('href')
    top_result_url = "http://www.goodreads.com" + result

    if verbose:
        print('Pulling book page: %s' %top_result_url)        

    #Get the book's page
    res2 = requests.get(top_result_url, verify=False)
    res2.raise_for_status()
    soup2 = bs4.BeautifulSoup(res2.text, "html.parser")

    #Select the cover image <img id="coverImage" src="XXX"
    cover_img_url = soup2.select('img' '#coverImage')[0].get('src')

    if verbose:
        print('Pulling cover: %s' %cover_img_url)

    #Getting cover image
    res3 = requests.get(cover_img_url, verify=False)
    res3.raise_for_status()

    #Chunk to file
    try:
        with open(fname, 'wb') as f:
            for chunk in res3.iter_content():
                f.write(chunk)

        if verbose:
            print('Image written: %s' %fname)
    except IOError:
        print "Error writing image to %s" %fname

