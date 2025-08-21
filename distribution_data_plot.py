'''import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import jarque_bera
from scipy.stats import boxcox

# Define the data
data = pd.DataFrame({
    'Y': [0.173430576, 0.058729494, 0.284691582, -0.344140556, 0.27985, -0.16965, 0.025146667, 0.169, 0.413975,
          -0.0237125, 0.257534343, 0.319986111, 0.45886, 0.201758318, 0.197597475, -0.194400352, -0.088347436,
          0.258038889, 0.154970076, 0.136627367, 0.131587753, 0.085913731, 0.341154905, 0.240681484, 0.5591,
          0.299404848, -0.345225, 0.081826316, 0.053677497, -0.089747143, 0.187288321, 0.200517857, 0.118819804,
          -0.085806052, 0.010743984, -0.002752769, 0.04276551, 0.03727584, -0.04746808, -0.035769494, -0.067691556,
          -0.029684798, -0.023097183, -0.002604186, 0.03769472, -0.05772885, -0.020361556, -0.069596054,
          -0.120935604, -0.099898246, 0.054994783, -0.06253495, -0.01287051, -0.085548383, 0.031786078,
          -0.125362601, -0.074437931, -0.0559012, -0.002126275, 0.005593403, 0.128902723, -0.038373888],
    'T': [i+1 for i in range(62)],
    'D': [0] * 33 + [1] * 29,
    'P': [0] * 33 + [i+1 for i in range(29)]
})

# Plot the original data
plt.figure(figsize=(10, 4))
plt.plot(data['T'], data['Y'])
plt.xlabel('Time')
plt.ylabel('Y')
plt.title('Original Data')
plt.show()

# Apply transformations
data['Y_log'] = np.log(data['Y'])
data['Y_sqrt'] = np.sqrt(data['Y'])
data['Y_boxcox'], lam = boxcox(data['Y'] + 1)  # Adding 1 to handle zero values before transformation'''

'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import jarque_bera
from scipy.stats import boxcox

# Define the data
data = pd.DataFrame({
    'Y': [0.173430576, 0.058729494, 0.284691582, -0.344140556, 0.27985, -0.16965, 0.025146667, 0.169, 0.413975,
          -0.0237125, 0.257534343, 0.319986111, 0.45886, 0.201758318, 0.197597475, -0.194400352, -0.088347436,
          0.258038889, 0.154970076, 0.136627367, 0.131587753, 0.085913731, 0.341154905, 0.240681484, 0.5591,
          0.299404848, -0.345225, 0.081826316, 0.053677497, -0.089747143, 0.187288321, 0.200517857, 0.118819804,
          -0.085806052, 0.010743984, -0.002752769, 0.04276551, 0.03727584, -0.04746808, -0.035769494, -0.067691556,
          -0.029684798, -0.023097183, -0.002604186, 0.03769472, -0.05772885, -0.020361556, -0.069596054,
          -0.120935604, -0.099898246, 0.054994783, -0.06253495, -0.01287051, -0.085548383, 0.031786078,
          -0.125362601, -0.074437931, -0.0559012, -0.002126275, 0.005593403, 0.128902723, -0.038373888],
    'T': [i+1 for i in range(62)],
    'D': [0] * 33 + [1] * 29,
    'P': [0] * 33 + [i+1 for i in range(29)]
})

# Apply Box-Cox transformation
data['Y_boxcox'], lam = boxcox(data['Y'] + 1)  # Adding 1 to handle zero values before transformation

# Plot the transformed data
plt.figure(figsize=(10, 4))
plt.plot(data['T'], data['Y_boxcox'])
plt.xlabel('Time')
plt.ylabel('Y (Box-Cox transformed)')
plt.title('Box-Cox Transformed Data')
plt.show()'''
'''
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

# Read the data
df = pd.read_csv('Sentiment_Data.csv')

# Logarithmic transformation
df['Y_log'] = np.log(df['Y'])

# ARIMA
i = 0
j= 0
for i in range (0,20):
    for j in range(0,20):
        arima_results = sm.tsa.arima.ARIMA(df['Y_log'], exog=df[['T', 'D', 'P']], order=(i, 0, j)).fit()
        print(arima_results.summary())


# Diagnostic checking
residuals = arima_results.resid

# Plot residuals
fig, ax = plt.subplots(figsize=(10, 6))
sm.qqplot(residuals, line="45", ax=ax)
ax.set_title("ARIMA QQ Plot")
plt.show()

# Model predictions means
y_pred = arima_results.get_prediction(start=0, end=len(df)-1, exog=df[['T', 'D', 'P']]).predicted_mean

# Counterfactual assumes no interventions
cf_df = df.copy()
cf_df['D'] = 0.0
cf_df['P'] = 0.0

# Counterfactual mean and 95% confidence interval
y_cf = arima_results.get_forecast(steps=len(df), exog=cf_df[['T', 'D', 'P']])

# Plot section
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(16, 10))

# Plot sentiment data
ax.scatter(df['T'], df['Y'], facecolors='none', edgecolors='steelblue', label="Sentiment per day", linewidths=2)

# Plot model mean sentiment prediction
ax.plot(df['T'], np.exp(y_pred), 'b-', label="Model prediction")

# Plot counterfactual mean sentiment with 95% confidence interval
ax.plot(df['T'], np.exp(y_cf.predicted_mean), 'k.', label="Counterfactual")
ax.fill_between(df['T'], np.exp(y_cf.conf_int()['lower Y']), np.exp(y_cf.conf_int()['upper Y']), color='k', alpha=0.1, label="Counterfactual 95% CI")

# Plot line marking intervention moment
ax.axvline(x=33.5, color='r', label='Intervention')

ax.legend(loc='best')
plt.ylim([-1, 1])
plt.xlabel("Days")
plt.ylabel("Sentiment per day")
plt.show()'''

'''import pandas as pd
import numpy as np
import statsmodels.api as sm

# Read the data
df = pd.read_csv('Sentiment_Data.csv')

# Initialize p and q values
p = 0
q = 0

# Initialize significance thresholds
lb_threshold = 0.05
jb_threshold = 0.05

# Loop until Ljung-Box and Jarque-Bera tests are not significant
while True:
    # ARIMA
    arima_results = sm.tsa.arima.ARIMA(df['Y'], exog=df[['T', 'D', 'P']], order=(p, 0, q)).fit()
    print(arima_results.summary())

    # Check Ljung-Box and Jarque-Bera tests
    lb_p_value = arima_results.test_serial_correlation(method='ljungbox')[1][-1]
    jb_p_value = arima_results.test_normality(method='jarquebera')[1]

    if lb_p_value > lb_threshold and jb_p_value > jb_threshold:
        break

    # Increment p and q values
    p += 1
    q += 1

print("Optimal ARIMA order: ({}, 0, {})".format(p, q))'''

'''
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.diagnostic import acorr_ljungbox

# Read the data
df = pd.read_csv('Sentiment_Data.csv')

# Initialize p and q values
p = 0
q = 0

# Initialize significance thresholds
lb_threshold = 0.05
jb_threshold = 0.05

# Loop until Ljung-Box and Jarque-Bera tests are not significant
while True:
    # ARIMA
    arima_results = sm.tsa.arima.ARIMA(df['Y'], exog=df[['T', 'D', 'P']], order=(p, 0, q)).fit()
    print(arima_results.summary())

    # Check Ljung-Box and Jarque-Bera tests
    lb_p_value = acorr_ljungbox(arima_results.resid, lags=[arima_results.k_ar])[1][0]
    jb_p_value = arima_results.test_normality(method='jarquebera')[1]

    if lb_p_value > lb_threshold and jb_p_value > jb_threshold:
        break

    # Increment p and q values
    p += 1
    q += 1

print("Optimal ARIMA order: ({}, 0, {})".format(p, q))'''


import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.diagnostic import acorr_ljungbox

# Read the data
df = pd.read_csv('Sentiment_Data.csv')

# Initialize p and q values
p = 0
q = 0

# Initialize significance thresholds
lb_threshold = 0.05


# Loop until Ljung-Box and Jarque-Bera tests are not significant
while True:
    # ARIMA
    arima_results = sm.tsa.arima.ARIMA(df['Y'], exog=df[['T', 'D', 'P']], order=(p, 0, q)).fit()
    print(arima_results.summary())

    # Check Ljung-Box and Jarque-Bera tests
    lb_p_value = acorr_ljungbox(arima_results.resid, lags=[1])[1][0]



    if lb_p_value > lb_threshold :
        print("Optimal ARIMA order: ({}, 0, {})".format(p, q))
        break

    # Increment p and q values
    p += 1
    q += 1



'''
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.stattools import durbin_watson

# Read the data
df = pd.read_csv('Sentiment_Data.csv')

# Initialize p and q values
p = 0
q = 0

# Initialize significance thresholds
lb_threshold = 0.05
jb_threshold = 0.05

# Loop until Ljung-Box and Jarque-Bera tests are not significant
while True:
    # ARIMA
    arima_model = sm.tsa.ARIMA(df['Y'], exog=df[['T', 'D', 'P']], order=(p, 0, q))
    arima_results = arima_model.fit()
    print(arima_results.summary())

    # Check Ljung-Box and Jarque-Bera tests
    dw_stat = durbin_watson(arima_results.resid)

    if dw_stat >= 1.5 and dw_stat <= 2.5:
        break

    # Increment p and q values
    p += 1
    q += 1'''


