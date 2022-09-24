import matplotlib.pyplot as plt
import pandas as pd

df1 = pd.read_excel('データ解析講座一日目演習.xlsx',sheet_name='家計指標',index_col=0)
print(df1.columns)
fig, ax = plt.subplots(figsize=(8,4))
ax.hist(df1['実収入'])

ax.set_title("Histogram of annual income")
ax.set_xlabel("value")
ax.set_ylabel("Frequency")
plt.show()
