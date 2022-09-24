import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import statsmodels.api as sm
from statsmodels.formula.api import ols

# seabornライブラリで日本語表示を可能にする
sns.set(font=['MS Gothic'])
df1 = pd.read_excel('データ解析講座一日目演習.xlsx',sheet_name='家計指標',index_col=0)
print(df1.columns)

# plot a correlation between df1['世帯主収入'] and df1['食料費割合'] using seaborn
# sns.jointplot(x='世帯主収入', y='食料費割合', data=df1)
# plt.show()
# regression of df1['世帯主収入'] and df1['食料費割合'] using statsmodels

X = df1['世帯主収入']
y = df1['食料費割合']
X = sm.add_constant(X)
model = sm.OLS(y,X)
results = model.fit()
print(results.summary())

# regression of df1['世帯主収入'] and df1['食料費割合'] using seaborn
sns.regplot(x='世帯主収入', y='食料費割合', data=df1)
plt.show()