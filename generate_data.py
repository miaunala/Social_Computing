import requests as rq
import csv
from datetime import datetime
import praw
import logging
import time
import re
from configparser import ConfigParser


def generate_data():

    logging.basicConfig(
        filename="generate_data.log", encoding="utf-8", level=logging.INFO
    )

    # Read config.ini file
    config_object = ConfigParser()
    config_object.read("config.ini")

    # Get the password
    userinfo = config_object["USERINFO"]

    # prepare reddit object for PRAW use -> used to fetch comments
    reddit = praw.Reddit(
        client_id=userinfo["client_id"],
        client_secret=userinfo["client_secret"],
        user_agent=userinfo["user_agent"],
        ratelimit_seconds=300,
    )

    with open("mentions_counter.csv", "w", newline="") as f1, open(
        "posts.csv", "w", newline=""
    ) as f2, open("comments.csv", "w", newline="") as f3:
        f1_writer, f2_writer, f3_writer = csv.writer(f1), csv.writer(f2), csv.writer(f3)
        prepare_files(f1_writer, f2_writer, f3_writer)

        base_query = (
            "https://api.pushshift.io/reddit/search/submission/?q=mormons&size=1000"
        )

        # 01.03.23 00:00:00 (GMT)
        after = 1359673198
        # 01.03.23 23:59:59 (GMT)
        before = 1325372400
        # end after 61 days -> 01.05.23 (including)
        nr_days = 31

        for i in range(nr_days):

            # assemble query and get data from API
            q = base_query + "&after=" + str(after) + "&before=" + str(before)
            try:

                # Pushshift API call
                r = rq.get(q).json()

                # related_cnt countes the number of posts that pass the "relatad check"
                # this is then written into the mentions counter, s.t. the mentions_counter then
                # only contains the number of posts that are actually related...
                related_cnt = 0

                # get date for posts.csv and mentions_counter.csv
                date = datetime.utcfromtimestamp(after).strftime("%Y-%m-%d")

                # iterate through all posts of that day that contain "bud light"
                for post in r["data"]:

                    # check if the post is actually related to the beer bud ligth
                    if not check_related(post):
                        logging.info(
                            "post: " + post["id"] + " is not related to mormons"
                        )
                        continue

                    related_cnt += 1

                    id = post["id"]
                    title = post["title"]
                    subreddit = post["subreddit_name_prefixed"]
                    self_text = post["selftext"]

                    # sometimes the promoted field is not in the results wtf:
                    try:
                        is_ad = "yes" if post["promoted"] else "no"
                    except Exception as e:
                        is_ad = ""
                        logging.info(' "promoted" field not found for post: ' + str(id))

                    # score is the sum of all upvotes (+1) and downvotes (-1)
                    # score has to be fetched with the Reddit API (PRAW). The
                    # score entry of the PushshiftAPI is outdated...
                    score = get_top_20_comments(reddit, id, f3_writer)

                    # write the post info into posts.csv
                    f2_writer.writerow(
                        [id, date, title, subreddit, self_text, is_ad, score, ""]
                    )

                # write the number of related posts of that day to mentions_counter.csv
                f1_writer.writerow([date, related_cnt])

                logging.info(
                    "Retrieved data from PushshiftAPI for time-frame: "
                    + str(after)
                    + "-"
                    + str(before)
                )

            except Exception as e:
                logging.error(
                    "An error occured while requesting data from Pushshift API for time-frame: "
                    + str(after)
                    + "-"
                    + str(before)
                )
                logging.error(e)

            # update timeframe for the next day
            # 86400 seconds in a day...
            after += 86400
            before += 86400


# checks whether the post is related to the beer bud light
def check_related(post):

    title = post["title"]
    self_text = post["selftext"]
    is_related = False

    if (re.search(r"\bmormons\b", title, re.I)) or (
        re.search(r"\bmormons\b", self_text, re.I)
    ):
        is_related = True

    return is_related


# write the top 20 comments of a post into comments.csv
# return the score of the post passed to this function
def get_top_20_comments(reddit, post_id, f3_writer):

    # Reddit API rate limit is 60 req per minute
    # This is an extra safety percation, in theory the reddit object
    # sould be capable of handling rate limits on its own...
    time.sleep(2.0)

    # reference to which post the comments are written under
    parent_post = post_id
    parent_score = 0

    # get submission in PRAW
    try:
        submission = reddit.submission(post_id)
        submission.comment_sort = "top"
        parent_score = submission.score

        # sort the comments by "top"
        comments = submission.comments.list()
        logging.info("No_comments of post " + post_id + " = " + str(len(comments)))

        # if the post has more than 20 comments, just take 20
        if len(comments) >= 20:
            for comment, i in zip(comments, range(20)):
                id = comment.id
                score_of_comment = comment.score
                body = comment.body

                # write the comment-row in the comments.csv
                f3_writer.writerow([id, parent_post, score_of_comment, body])

        # If there are less than 20 comments in the post, just take all
        else:
            for comment in comments:
                id = comment.id
                score_of_comment = comment.score
                body = comment.body

                # write the comment-row in the comments.csv
                f3_writer.writerow([id, parent_post, score_of_comment, body])

        logging.info("Retrieved data from Reddit for post_id: " + str(parent_post))

    except Exception as e:
        logging.error(
            " An error occured while retrieving data from Reddit for post_id: "
            + str(parent_post)
        )
        logging.error(e)

    return parent_score


# creates three .csv files where we store our data:
def prepare_files(f1_writer, f2_writer, f3_writer):

    # create excel file with cols: date and counter
    f1_fields = ["date", "counter"]
    f1_writer.writerow(f1_fields)
    logging.info("Created mentions_counter.csv")

    # create excel file with cols: id, date, title, self_text and comments
    f2_fields = [
        "id",
        "date",
        "title",
        "subreddit",
        "self_text",
        "Advertisement",
        "score",
        "avg_sentiment",
    ]
    f2_writer.writerow(f2_fields)
    logging.info("Created posts.csv")

    # create excel file with cols: id, parent_post, score and body
    f3_fields = ["id", "parent_post", "score", "body"]
    f3_writer.writerow(f3_fields)
    logging.info("Created comments.csv")


if __name__ == "__main__":
    generate_data()
