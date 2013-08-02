import json
from optparse import make_option
from django.core.management.base import BaseCommand
from common import facebook
import urlparse

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--data',
            action='store_true',
            dest='data',
            default=False,
            help='data'),
        )

    def handle(self, *args, **options):
        err = self.stderr
        out = self.stdout
        if options['data']:
            get_data(args)

def get_data(args):
    access_code = args[0]
    object = args[1]
    fb = facebook.GraphAPI(access_code)
    response_data = []
    posts = fb.get_connections(object, "posts")
    response_data.append(posts)
    try:
        count = 0
        while count < 500:
            count += 1
            print "Page", count
            if "paging" in posts:
                path,args = request_package(posts["paging"])
                posts = fb.request(path=path, args=args)
                response_data.append(posts)
    except:
        pass
    analyse_response_data(response_data, object)

def analyse_response_data(response_data, object):
    likes = []
    comments = []
    names = []
    for posts in response_data:
        for post in posts["data"]:
            if "likes" in post:
                for like in post["likes"]["data"]:
                    likes.append(like)
            if "comments" in post:
                for comment in post["comments"]["data"]:
                    comments.append(comment["from"])
    flikes = open("%s_likes" % str(object),"w")
    fcomments = open("%s_comments" % str(object),"w")
    fnames = open("%s_names" % str(object),"w")

    for el in likes:
        names.append(el["name"])
    for el in comments:
        names.append(el["name"])
    for name in list(set(names)):
        fnames.write("%s\n" % name)

    likes = list(set([l["id"] for l in likes]))
    comments = list(set([c["id"] for c in comments]))
    for like_id in likes:
        flikes.write("%s\n" % like_id)
    for comment_id in comments:
        fcomments.write("%s\n" % comment_id)
    fnames.close()
    flikes.close()
    fcomments.close()

def request_package(paging_data):
    p = urlparse.urlparse(paging_data["next"])
    args = urlparse.parse_qs(p.query)
    for a in args.keys():
        args[a] = args[a][0]
    return p.path[1:], args