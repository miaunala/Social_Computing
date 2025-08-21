import nltk
import csv
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import os
from datetime import datetime, timedelta


# for each post, get comments -> make sentiments analysis on each comment. 
# Calculate average sentiment on each post and save it. 

POSTS_FILE = "posts.csv"
POSTS_NO_COMMENTS = "posts_no_comments.csv"
DAILY_AVG_FILE = "sentiment_per_day.csv"

COMMENT_BODY = 3

POST_ID = 0
POST_TITLE = 2
POST_TEXT = 4

def file_exists(filename):
    cwd = os.getcwd()
    file_path = os.path.join(cwd, filename)
    
    return os.path.exists(file_path)
        

def isNaN(num):
    return num != num

def add_column(input_file, output_file, column_name):
    with open(input_file, 'r') as file_in, open(output_file, 'w', newline='') as file_out:
        reader = csv.reader(file_in)
        writer = csv.writer(file_out)
        
        header = next(reader)  # Read the header
        header.append(column_name)  # Add the new column name
        
        writer.writerow(header)  # Write the updated header
        
        for row in reader:
            row.append(0.0)  # initialize column
            writer.writerow(row)  # Write the updated row


def init_sentiment_per_day_csv(file_name:str):
    
    if file_exists(file_name):
        print("file already exists")
        return

    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['date', 'avg_sentiment', 'avg_sentiment_no_comments']) #writes header 

# TODO: Implement updating mechanism or at leas make sure it doens't append things that already exist.
def write_avg_sentiment_per_day(date:datetime):
    ''' 
    Calculates average sentiment per day (with and without comments considered in each post) and saves it into the sentiment_per_day.csv
    '''

    df = pd.read_csv(POSTS_NO_COMMENTS)
    print(date)
    filtered_df = df[df["date"]==str(date)]
    total_with_comments = 0
    total_without_comments = 0

    for _,post in filtered_df.iterrows():
        if isNaN(post["avg_sentiment"]):
            raise Exception("This post is missing a avg_sentiment!") 

        total_with_comments += post["avg_sentiment"]    
        if isNaN(post["sentiment_no_comments"]):
            raise Exception("This post is missing sentiment_no_comments!") 

        total_without_comments += post["sentiment_no_comments"]    
        
    # calculating daily avg sentiment of current date
    daily_avg = 0
    if len(filtered_df) >0:
        daily_avg = total_with_comments / len(filtered_df)
    
    daily_avg_no_comments = 0
    if len(filtered_df) > 0:
        daily_avg_no_comments = total_without_comments / len(filtered_df)

    # writing result into csv
    with open(DAILY_AVG_FILE,'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date,daily_avg,daily_avg_no_comments])


def update_daily_avg(start_date:str, end_date:str):
    try:
        start_date = datetime.strptime(start_date,'%Y-%m-%d').date()
        end_date = datetime.strptime(end_date,'%Y-%m-%d').date()
    except:
        print("an error has occured while converting to datetime")
        return

    current_date = start_date
    
    # iterating through each day and writing the avg sentiment 
    while current_date <= end_date:
        write_avg_sentiment_per_day(current_date)
        print(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)


def get_avg_sentiment_per_post(tot_com_score: float, com_cnt:int, title_score:float, text_score):
    # still works if tot_com_score com_cnt are 0
    if text_score:
        return (tot_com_score + title_score + text_score) / (com_cnt + 2)
    
    return (tot_com_score + title_score) / (com_cnt + 1)


def get_speficif_post_comments(post_id):
    df = pd.read_csv('comments.csv')

    post_comments = df.loc[df["parent_post"]== post_id] 
    return post_comments


def analyze_post(post, include_comments:bool ):
    analyzer = SentimentIntensityAnalyzer()

    id = post["id"]
    title = post["title"]
    text = post["self_text"]
    
    title_score = analyzer.polarity_scores(title)["compound"]
    text_score = analyzer.polarity_scores(text)["compound"] if not isNaN(text) and len(text) > 0 else  None

    # handling posts which have no comments 
    total_comment_score =0
    comment_cnt = 0       

    if include_comments:
        try:
            comments_df = get_speficif_post_comments(id)
        except:
            print("This post has no comments.")
            avg_sentiment = (title_score + text_score) / 2
            return avg_sentiment

            

        #calculating scores of all comments    
        for index, comment in comments_df.iterrows():
            comment_score = analyzer.polarity_scores(comment[COMMENT_BODY])["compound"]
            total_comment_score += comment_score
            comment_cnt +=1

    
    return get_avg_sentiment_per_post(total_comment_score, comment_cnt, title_score, text_score) 
    


def start_analyzer(include_comments:bool):
    new_csv_name = "posts_no_comments.csv"
    if include_comments:
        posts_df = pd.read_csv(POSTS_FILE)
        
        for index, post in posts_df.iterrows():
            avg_sentiment = analyze_post(post, include_comments)
            posts_df.at[index,"avg_sentiment"] = avg_sentiment


        posts_df.to_csv(POSTS_FILE, index=False)
    else:
        #creates copy of POST_FILE and adds column to it
        if not file_exists("sentiment_no_comments"):
            add_column(POSTS_FILE, new_csv_name, "sentiment_no_comments")
        posts_df= pd.read_csv(new_csv_name)
        
        for index, post in posts_df.iterrows():
            avg_sentiment = analyze_post(post, include_comments)
            posts_df.at[index,"sentiment_no_comments"] = avg_sentiment
        posts_df.to_csv(new_csv_name, index=False)

#init_sentiment_per_day_csv("sentiment_per_day.csv")

start_analyzer(include_comments=False)

update_daily_avg("2023-03-01", "2023-05-01")