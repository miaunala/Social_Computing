import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import os
from scipy.signal import detrend
from dtaidistance import dtw
from dtaidistance import dtw_visualisation as dtwvis
from sklearn.metrics.pairwise import euclidean_distances

data = pd.read_csv('C:/Users/whatt/iCloudDrive/UZH/Master/FS23/Computational Linguistics/Social Computing/Final project/SentimentAnalyzer/Sentiment_Stock_forSimilarity.csv')
selected = ['Sentiment', 'Stock']
data = data.loc[data["Data"].isin(selected)]
print(data)

# Scaling
scaled = dict()
for item in data["Data"].unique():
    series = data[data["Data"] == item]["Y"].values
    scaled[item] = (series - series.mean()) / series.std()
scaled = pd.DataFrame(scaled)
print(scaled)

# Plotting
plt.figure(figsize=(10, 6))
for column in scaled.columns:
    plt.plot(scaled[column], label=column)
plt.xlabel('Time')
plt.ylabel('Scaled Value')
plt.title('Scaled Data')
plt.legend()
plt.grid(True)
plt.show()


#Detrending
detrended = dict()
for j in selected:
    detrended[j] = detrend(scaled[j])
detrended = pd.DataFrame(detrended, index=sorted(data["T"].unique()))
print(detrended)

# Plotting
plt.figure(figsize=(10, 6))
for column in detrended.columns:
    plt.plot(detrended[column], label=column)
plt.xlabel('Time')
plt.ylabel('Detrended Value')
plt.title('Detrended Data')
plt.legend()
plt.grid(True)
plt.show()


#Smoothing
smoothed = detrended.rolling(5).mean()
print(smoothed)


# Plotting
plt.figure(figsize=(10, 6))
for column in smoothed.columns:
    plt.plot(smoothed[column], label=column)
plt.xlabel('Time')
plt.ylabel('Smoothed Value')
plt.title('Smoothed Data')
plt.legend()
plt.grid(True)
plt.show()

# Pearson's correlation with smoothed
print(pd.DataFrame.corr(smoothed))


# Euclidean Distance with smoothed
smoothed_dropped = smoothed.dropna()

euc_dist = euclidean_distances(smoothed_dropped.T)
print(pd.DataFrame(euc_dist,index=selected, columns=selected))


# Dynamic Time Warping with smoothed
dtw_dist = dtw.distance_matrix_fast(smoothed.T.values)
pd.DataFrame(dtw_dist,index=selected,columns=selected)

fig, ax = plt.subplots(2,1,figsize=(1280/96, 720/96))
path = dtw.warping_path(smoothed["Sentiment"].values, smoothed["Stock"].values)
dtwvis.plot_warping(smoothed["Sentiment"].values, smoothed["Stock"].values, path, fig=fig, axs= ax)

ax[0].set_title("DTW Warping Path between Sentiment and Stock")
fig.tight_layout()

plt.show()

