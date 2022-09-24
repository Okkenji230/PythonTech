import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

df1 = pd.read_excel('データ解析講座一日目演習.xlsx',sheet_name='家計指標',index_col=0)
print(df1.columns)

# plot a histogram of df1['世帯主収入'] using seaborn
sns.distplot(df1['世帯主収入'], kde=False, rug=True)
plt.show()
