README

WHAT
  bookcover_collage exists to make a collage of cover images of the books you have read. Sometimes it is hard to remember all of the things you have read, and looking at a big page full of book covers provides a nice sense of accomplishment. bookcover_collage takes a list of book titles, and queries Goodreads.com to grab cover images for each title. After obtaining the cover images, bookcover_collage sticks them together as a single collage.

USAGE
  - Compile a list of the books you have read
  - Pass the list to get_all_images()
  - Wait
  - Run make_collage()
    - No arguments needed if using the default parameters
  - Collage should be saved in the working directory as collage.jpg

EXAMPLE USAGE
  - get_all_images(["lord of the rings", "war and peace", "eat, pray, love"])
  - make_collage()

OPTIONS
  - get_all_images() has a boolean parameter rand_delay which controls whether or not to insert a random delay between requests. I am not sure what Goodreads' policy on scraping is, but you can turn the delay off by setting rand_delay=False, which will significantly speed up the program.
  - make_collage() has an integer parameter width, which specifies the width (in bookcovers) of the collage
  - All of the functions provided have a parameter that points to the directory that houses the cover images (make sure that if you change it, you use the same directory for all of the functions!)

NOTES
  This isn't 100% accurate. The script naively assumes the first result returned by Goodreads is the proper cover, which is not always the case. Fortunately this is rare, and easy enough to fix manually (simply download the appropriate cover image, put it in the directory with the other images, and rerun make_collage()). A similar fix is possible in the even rarer case in which Goodreads returns no images.
