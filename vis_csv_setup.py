import pandas as pd

def setup_csv_no_columns_vis_csv():
    # Read the first CSV file
    df1 = pd.read_csv('sentiment_per_day.csv')

    # Read the second CSV file
    df2 = pd.read_csv('Sentiment_Data.csv')

    # Replace the data in the "Y" column of df2 with the data from the "avg_sentiment_no_columns" column of df1
    df2['Y'] = df1['avg_sentiment_no_comments']

    # Save the updated df2 to a new CSV file
    df2.to_csv('sentiment_data_vis_no_comments.csv', index=False)

setup_csv_no_columns_vis_csv()