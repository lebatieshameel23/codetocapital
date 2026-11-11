# Summarize Raw Expense CSVs with Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import pandas as pd

df = pd.read_csv("expenses.csv")
grouped = df.groupby("category")
summary = grouped["amount"].sum().round(2)
summary.to_csv("summary.csv")
print("Saved summary.csv")
