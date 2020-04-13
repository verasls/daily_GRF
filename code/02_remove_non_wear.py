import pandas as pd


raw_acc = pd.read_csv("../data/068_4th_gt3x.csv", delimiter=",")
print(raw_acc.iloc[3864100 - 1, :])
