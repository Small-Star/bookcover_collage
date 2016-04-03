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
import time
import random
from PIL import Image

def get_cover_image(title, verbose=True, directory='./coverdir'):
    #Sample goodreads query URL: http://www.goodreads.com/search?utf8=%E2%9C%93&q=atlas+shrugged&search_type=books

    fname = directory + "/" + title + ".jpg"
        
    #Check and make sure the image hasn't been pulled already
    if os.path.isfile(fname):
        if verbose:
           print('%s already exists' %fname)
        return 0
    
    #Form querystring by concatenating search_url_beg + search string + search_url_end
    search_url_beg = "http://www.goodreads.com/search?utf8=%E2%9C%93&q="
    search_url_end = "&search_type=books"
    search_title = str.join('+',title.split())
    search_url = search_url_beg + title + search_url_end
    
    if verbose:
        print('--- Pulling search page for %s : %s' %(title, search_url))

    #Get search page
    res = requests.get(search_url, verify=False)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "html.parser")

    #The first result is probably the one we want
    result = soup.select('.bookTitle')[0].get('href')
    top_result_url = "http://www.goodreads.com" + result

    if verbose:
        print('--- Pulling book page: %s' %top_result_url)        

    #Get the book's page
    res2 = requests.get(top_result_url, verify=False)
    res2.raise_for_status()
    soup2 = bs4.BeautifulSoup(res2.text, "html.parser")

    #Select the cover image <img id="coverImage" src="XXX"
    cover_img_url = soup2.select('img' '#coverImage')[0].get('src')

    if verbose:
        print('--- Pulling cover: %s' %cover_img_url)

    #Getting cover image
    res3 = requests.get(cover_img_url, verify=False)
    res3.raise_for_status()

    #Chunk to file
    try:
        with open(fname, 'wb') as f:
            for chunk in res3.iter_content():
                f.write(chunk)

        if verbose:
            print('---Image written: %s' %fname)
    except IOError:
        print ("Error writing image to %s" %fname)

def get_all_images(title_list, verbose=True, directory='./coverdir'):
    #Assumes input is a list of strings; each string being a title of a book

    if not os.path.exists(directory):
        os.makedirs(directory)

    for t in title_list:
        fname = directory + "/" + t + ".jpg"
        
        if verbose:
            print('Checking %s...' %t) 
        
        if not os.path.isfile(fname):
            #Image has not already been obtained
            #Add in a random delay; unsure if scraping is tolerated
            time.sleep(random.randrange(1,30))
            get_cover_image(t, verbose)

        else:
            #Image already exists
            print('=== %s exists' %fname)
            continue

def make_collage(width=1280,verbose=True, directory='./coverdir'):
    #Concatenate all images in target directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f != "collage.jpg"]

    images = []
    sizes = []

    for f in files:
        #Filter out all but .jpgs
        try:
            fname = directory + "/" + f
            if Image.open(fname).format == 'JPEG':
                im_size = Image.open(fname).size
                images.append(fname)
                sizes.append(im_size)
        except IOError:
            pass
        
    if verbose:
        print('List of images found: %s' %images)
        print('Total Area: %s' %sum([s[0]*s[1] for s in sizes]))

    #Make a new image ***FIX STATIC SIZE ***
    collage = Image.new("RGB", (width, 5000))

    w_ctr, h_ctr = 0, 0
    
    for i in images:
        tmp = Image.open(i)

        #Check to make sure image will not go out of bounds
        if (w_ctr + tmp.size[0]) >= width:
            h_ctr += tmp.size[1]
            w_ctr = 0
            
        collage.paste(tmp,(w_ctr,h_ctr))
        w_ctr += tmp.size[0]
    collage.save(directory + "/" + "collage.jpg")

        
    ###TODO
    ###Cleanup
