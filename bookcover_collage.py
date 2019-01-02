#bookcover_collage
#Small-Star

import requests
import webbrowser
import os
import bs4
import shutil
import string
import warnings
import time
import random
import math
from PIL import Image
from difflib import SequenceMatcher

def get_cover_image(title, author, verbose=True, directory='./coverdir'):
    #Requires at least title; author is optional
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
        print('--- Pulling search page for %s by %s: %s' %(title, author, search_url))

    #Get search page
    res = requests.get(search_url, verify=False)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "html.parser")

    #Get all of the returned results, and match the titles and authors for similarity
    t_result = soup.select('.bookTitle')
    if author != None:
        a_result = []
        for t in t_result:
            #Messy way to pull out the first author per title
            a = t.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.get_text().split("(",1)[0].split(",",1)[0].rstrip()
            a_result.append(a)

    if len(t_result) == 0:
        #If no results at all are returned, return no image
        print('No results found')
        return 0
    
    if (len(t_result) != len(a_result)) and author != None:
        print('Error: Record set returned has uneven numbers of authors and titles')
        return 0

    similarity_list = []

    #Compare each result with the queried title and author, giving a similarity score
    for r in range(len(t_result)):
        sim = SequenceMatcher(None, title.lower(), t_result[r].get_text().lstrip().rstrip().lower()).ratio()
        if author != None:
            sim += SequenceMatcher(None, author.lower(), a_result[r].lstrip().rstrip().lower()).ratio()
        similarity_list.append(sim) 

    #The result we want is probably the one with the highest similarity index
    most_similar_index = similarity_list.index(max(similarity_list))
    result_ck = t_result[most_similar_index].get('href')
    top_result_url = "http://www.goodreads.com" + result_ck

    if verbose:
        print('--- Pulling book page: %s' %top_result_url)        
        print('------ Title: %s' %t_result[most_similar_index].get_text())
        if author != None:
            print('------ Author: %s' %a_result[most_similar_index])
            
    #Get the book's page
    res2 = requests.get(top_result_url, verify=False)
    res2.raise_for_status()
    soup2 = bs4.BeautifulSoup(res2.text, "html.parser")

    #Select the cover image <img id="coverImage" src="XXX"
    cover_img_url_t = soup2.select('img' '#coverImage')
    if len(cover_img_url_t) == 0:
        return 0
    else:
        cover_img_url = cover_img_url_t[0].get('src')

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
        return 1
    except IOError:
        print ("Error writing image to %s" %fname)

def get_all_images(title_list, author_list, verbose=True, directory='./coverdir', rand_delay=True):
    #Assumes input is a list of strings; each string being a title of a book

    if not os.path.exists(directory):
        os.makedirs(directory)

    missing_titles = []
    
    for t in range(len(title_list)):
        fname = directory + "/" + title_list[t] + ".jpg"
        
        if verbose:
            print('Checking %s...' %title_list[t]) 
            
        if not os.path.isfile(fname):
            #Image has not already been obtained

            #Skip this one if it is a short story - it won't be on Goodreads
            if title_list[t].find("[Short Story]") != -1:
                missing_titles.append(title_list[t])
                continue
            
            #Add in a random delay; unsure if scraping is tolerated
            if rand_delay:
                time.sleep(random.randrange(1,30))

            r = get_cover_image(title_list[t], author_list[t], verbose=verbose, directory=directory)
            if r != 1:
                missing_titles.append(title_list[t])

        else:
            #Image already exists
            print('=== %s exists' %fname)
            continue

    print("Number of images that could not be found: %s" %len(missing_titles))
    print(missing_titles)

def make_collage(width=10,verbose=True, directory='./coverdir', output_filename="collage.jpg"):
    #Concatenate all images in target directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f != output_filename]

    images, sizes = [], []

    #Read images out of the specified directory
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

    #Find the largest image; using the variably sized images provided looked sloppy
    largest_size = (0,0)
    for s in sizes:
        if s[0]*s[1] > largest_size[0]*largest_size[1]:
            largest_size = s
        
    if verbose:
        
        print('List of images found: \n')
        print("\n".join(images))
        print('Total Area (Before Resize): %s' %sum([s[0]*s[1] for s in sizes]))
        ta = largest_size[0]*largest_size[1]*len(images)
        print('Total Area (After Resize): %s' %ta)

    #Make a new image 
    collage = Image.new("RGB", (width*largest_size[0], math.ceil(len(images)/width)*largest_size[1]))

    w_ctr, h_ctr = 0, 0

    #Resize and concatenate all images
    for i in images:
        tmp = Image.open(i)
        tmp = tmp.resize(largest_size)

        #Check to make sure image will not go out of bounds
        if (w_ctr + tmp.size[0]) > width*largest_size[0]:
            h_ctr += tmp.size[1]
            w_ctr = 0
            
        collage.paste(tmp,(w_ctr,h_ctr))
        w_ctr += tmp.size[0]

    #Save output
    collage.save(output_filename)

