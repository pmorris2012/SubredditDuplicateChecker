#built-in modules
from time import sleep
from StringIO import StringIO
from requests import get
from pickle import loads, dumps
from os.path import isfile, exists
from os import makedirs
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
def run(user_agent, sub, interval = 60, num_posts = 20):
    #dictionary of posts, key = post id, value = submission
    seen = {}
    #dictionary of hashes, key = hash, value = list of posts
    hashes = {}
    #dictionary of posts where an offense has occured
    #key = post id, value = post id
    offenses = {}
    #dictionary of users who have offended, key = user, value = list of posts
    offenders = {}


    #if a saved state exists, load it
    if isfile("save/s_" + sub + ".txt") and isfile("save/h_" + sub + ".txt")\
    and isfile("save/o_" + sub + ".txt") and isfile("save/u_" + sub + ".txt"):
        with open("save/s_" + sub + ".txt", "r") as f:
            seen = loads(f.read())
        with open("save/h_" + sub + ".txt", "r") as f:
            hashes = loads(f.read())
        with open("save/o_" + sub + ".txt", "r") as f:
            offenses = loads(f.read())
        with open("save/u_" + sub + ".txt", "r") as f:
            offenders = loads(f.read())

    #establish connection with reddit and get subreddit object
    r = Reddit(user_agent=user_agent)
    subreddit = r.get_subreddit(sub)

    while True:
        print "checking for posts"
        try:
            #get new posts
            new = subreddit.get_new(limit=num_posts)
            for submission in new:
                #if we've already seen this post, ignore it
                if seen.has_key(submission.id):
                    continue
                #if this post doens't link to imgur, ignore it
                if "imgur.com/" not in submission.url:
                    continue
                split = submission.url.split(".com/")
                #if the post has a / after the .com/, it's an album, so ignore
                if "/" in split[1]:
                    continue

                #mark this post as seen - add it to the table
                seen[submission.id] = submission

                #chop off a file extension after the . to get the id
                split[1] = split[1].replace("?", ".")
                imgur_id = split[1].split(".")[0]

                #get the image from the url
                res = get("https://i.imgur.com/" + imgur_id + ".jpg")
                img = Image.open(StringIO(res.content))

                #hash the image
                hash = pHash(img, 64)

                #if this post is a duplicate, add it to the list for that hash
                if hashes.has_key(hash):
                    orig = hashes[hash][0]
                    post = submission.id
                    if submission.author == seen[orig].author:
                        print "{0} posted duplicate posts {1} and {2}".format(
                            submission.author, post, orig)
                    else:
                        print "{0} copied {1}!!!".format(post, orig)
                        offenses[post] = orig
                        offenders.setdefault(submission.author, []).append(post)
                    hashes[hash].append(submission.id)
                else:
                    print "new post found: {0}".format(submission.id)
                    hashes[hash] = [submission.id]

                #ensure the save directory exists
                if not exists("save"):
                    makedirs("save")
                #dump the updated seen and hashes objects to a file
                with open("save/s_" + sub + ".txt", "w") as f:
                    f.write(dumps(seen))
                with open("save/h_" + sub + ".txt", "w") as f:
                    f.write(dumps(hashes))
                with open("save/o_" + sub + ".txt", "w") as f:
                    f.write(dumps(offenses))
                with open("save/u_" + sub + ".txt", "w") as f:
                    f.write(dumps(offenders))

        except Exception as e:
            print e.message

        #wait the desired interval of time before checking again
        sleep(interval)

if __name__ == "__main__":
    run("duplicatechecker" + str(randint(0, 9999)), "pics+funny+me_irl")
