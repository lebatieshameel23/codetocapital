# Merge Shipping Tracking into Orders with 10 Lines of Python
# From the CodeToCapital YouTube channel. Test on a copy of your files first.
import pandas as pd
orders = pd.read_csv("orders.csv")
carrier = pd.read_csv("carrier.csv")
merged = orders.merge(
    carrier[["order_id", "tracking"]],
    on="order_id",
    how="left",
)
merged["status"] = "Shipped"
merged.to_csv("out.csv", index=False)
