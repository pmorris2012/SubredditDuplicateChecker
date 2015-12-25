#built-in modules
from time import sleep
from StringIO import StringIO
from requests import get
from pickle import loads, dumps
from os.path import isfile
from random import randint

#non-standard modules - need to be installed
from praw import Reddit
from PIL import Image

from ImageHash import pHash

'''
user_agent - a unique id to access reddit
subreddit - the name of the subreddit to check (accepts multireddit syntax)
interval - check for new posts every interval seconds
num_posts - the number of posts to grab each check
'''
def run(user_agent, subreddit, interval = 15, num_posts = 5):
    #dictionary of posts, key = post id, value = submission
    seen = {}
    # dictionary of hashes, key = hash, value = list of posts
    hashes = {}

    #if a saved state exists, load it
    if isfile("s_" + subreddit + ".txt") and isfile("h_" + subreddit + ".txt"):
        with open("s_" + subreddit + ".txt") as f:
            seen = loads(f.read())
        with open("h_" + subreddit + ".txt") as f:
            hashes = loads(f.read())

    #establish connection with reddit and get subreddit object
    r = Reddit(user_agent=user_agent)
    sub = r.get_subreddit(subreddit)

    while True:
        #get new posts
        new = sub.get_new(limit=num_posts)
        for submission in new:
            #if we've already seen this post, ignore it
            if seen.has_key(submission.id):
                continue
            #if this post doens't link to imgur, ignore it
            if "imgur.com/" not in submission.url:
                continue
            split = submission.url.split(".com/")
            #if the post has a / after the .com/, it links to an album. ignore
            if "/" in split[1]:
                continue

            #mark this post as seen - add it to the table
            seen[submission.id] = submission

            #chop off a file extension after the . to get the id
            imgur_id = split[1].split(".")[0]

            #get the image from the url
            res = get("https://i.imgur.com/" + imgur_id + ".jpg")
            img = Image.open(StringIO(res.content))

            #hash the image
            hash = pHash(img, 64)

            #if this post is a duplicate, add it to the list for that hash
            if hashes.has_key(hash):
                print "{0} copied {1}!!!".format(submission.id, hashes[hash][0])
                hashes[hash].append(submission.id)
            else:
                print "new post found: {0}".format(submission.id)
                hashes[hash] = [submission.id]

            #dump the updated seen and hashes objects to a file
            with open("s_" + subreddit + ".txt", "w") as f:
                f.write(dumps(seen))
            with open("h_" + subreddit + ".txt", "w") as f:
                f.write(dumps(hashes))

        #wait the desired interval of time before checking again
        sleep(interval)

if __name__ == "__main__":
    run("duplicatechecker" + str(randint(0, 9999)), "pics", num_posts = 10)
