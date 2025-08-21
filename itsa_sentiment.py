''' Interrupted Time Series Analysis
Step 1: bring the csv files in order that we need
Step 2: run the regression
Step 3: plot the regression

'''

from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
from statsmodels.graphics.gofplots import qqplot
import scipy as sp

# Read the data

df = pd.read_csv('Sentiment_Data.csv')


# ARIMA
arima_results = ARIMA(df["Y"], exog=df[["T","D","P"]], order=(1,0,0)).fit()
print(arima_results.summary())


# Define the start and end points
start = 33
end = 62

# Get predictions
predictions = arima_results.get_prediction(start=0, end=end-1, exog=df[["T","D","P"]])
print(predictions.summary_frame(alpha=0.05))

# Model predictions means
y_pred = predictions.predicted_mean

# counterfactual assumes no interventions
cf_df = df.copy()
cf_df["D"] = 0.0
cf_df["P"] = 0.0

# Counterfactual mean and 95% confidence interval
y_cf = arima_results.get_forecast(steps=end-start, exog=cf_df[["T","D","P"]][start:])

# Plot section
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(16,10))

# Plot sentiment data
ax.scatter(df["T"], df["Y"], facecolors='none', edgecolors='steelblue', label="Sentiment per day", linewidths=2)

# Plot model mean sentiment prediction
ax.plot(df["T"][:start], y_pred[:start], 'b-', label="Model prediction")
ax.plot(df["T"][start:], y_pred[start:], 'b-')

# Plot counterfactual mean sentiment with 95% confidence interval
ax.plot(df["T"][start:], y_cf.predicted_mean, 'k.', label="Counterfactual")
ax.fill_between(df["T"][start:], y_cf.conf_int()["lower Y"], y_cf.conf_int()["upper Y"], color='k', alpha=0.1, label="Counterfactual 95% CI")

# Plot line marking intervention moment
ax.axvline(x=33.5, color='r', label='Intervention')

ax.legend(loc='best')
plt.ylim([-1, 1])
plt.xlabel("Days")
plt.ylabel("Sentiment per day")
plt.show()
plt.close()

# ARIMA Residuals
fig, ax = plt.subplots(figsize=(10, 6))
sm.qqplot(arima_results.resid, sp.stats.t, fit=True, line="45", ax=ax)
ax.set_title("ARIMA QQ Plot")
plt.show()