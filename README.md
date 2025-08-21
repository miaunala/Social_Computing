# Tool Collection for Social Computing Group Project: Bud Light

## generate_data.py

This file executes a python script that collects data from Reddit posts that contain "bud light". Posts are fetched from the [PushshifAPI](https://github.com/pushshift/api) for any day in the specified time period. Comments from the posts are fetched using the [Reddit API](https://praw.readthedocs.io/en/stable/). Important fields from the posts and comments are written into .csv files.

### mentions_counter.csv

| date       | counter |
| ---------- | :-----: |
| 2023-03-01 |   35    |
| ...        |   ...   |

This file stores the number of Reddit posts found that contain the word "bud light" for the given date.

- date: Date for which the posts were gathered
- counter: number of posts found that contain "bud light" for that date

### posts.csv

| id      |    date    |   title    |  subreddit  |    self_text     | advertisement | score | mean_sentiment |
| ------- | :--------: | :--------: | :---------: | :--------------: | :-----------: | :---: | :------------: |
| 11fmeum | 2023-03-01 | some title | r/bud_light | post description |      no       |  59   |      0.2       |
| ...     |    ...     |    ...     |     ...     |       ...        |      ...      |  ...  |      ...       |

This file stores each post that was gathered containing the word "bud light"

- id: unique id of the Reddit post
- date: date when the post was created
- title: title of the post
- subreddit: subreddit where the post was posted to (or username (e.g. u/random_name) if the post was posted to a user's profile)
- slef_text: description of the post that the author wrote
- advertisement: yes / no / "". Whether the post is tagged as an advertisement
- score: score of the post (upvotes, downvotes)
- mean_sentiment: sentiment score of the post (including title, self_text and top 20 comments)

### comments.csv

| id      | parent_post | score |     body     |
| ------- | :---------: | :---: | :----------: |
| jaklqco |   11fmeum   |  43   | some opinion |
| ...     |     ...     |  ...  |     ...      |

This file stores up to 20 comments for each post found containing "bud light".

- id: Unique id of the comment
- parent_post: id of the post under which the comment was posted
- score: score of the comment (upvotes, downvotes)
- body: text that was commented

**Important:** Not all posts have comments! Some posts have 0 comments or are not accessible anymore. For such posts, no comments will be found in the comments.csv file.

## bud_stock_prices.csv

This file contans the dates and closing prices of the BUD stock (gathered from Google Finances).

### mentions_counter.csv

| Date       | Close   |
| ---------- | :-----: |
| 2023-03-01 |   90.51 |
| ...        |   ...   |

Please note that the stock market is closed on the weekends. Therefore, Saturdays and Sundays are not accounted for.

## sentiment_analyzer.py

Sentiment_analyzer.py is a python script which analyzes the sentiment of reddit posts and their corresponding comments stored in the `posts.csv` and the `comments.csv`.

### How it works

For each post in the `posts.csv`, the script rates the sentiment in the title and, if existing, the text of the post. The sentiment analysis is done with [VADER](https://vadersentiment.readthedocs.io/en/latest/). Based on the `id` of the post, all the corresponding post comments can be fetched from the `comments.csv` file. Each comment itself runs through vaders sentiment analysis and gets a score. After all the comments of a single post have been analyzed, the avereage sentiment a post gets calculated as follows:

```math
avg_sentiment = (title_sentiment + text_sentiment + sum_of_comments_sentiment) / (1 + 1 + nr_of_comments)
```

For each post, the sentiment score then gets written back into the posts.csv file.
Since we are interested in the daily average sentiment, a `sentiment_per_day.csv` gets initialized. By iterating through all posts in `posts.csv` and reading out the average sentiment for each post, we can calculate the daily average sentiment and store it in the `sentiment_per_day.csv`
