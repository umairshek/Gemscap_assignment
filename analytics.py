import pandas as pd
import numpy as np
import statsmodels.api as sm

def compute_analytics(df1, df2, window=20):
    # Take only required columns
    p1 = df1["price"].reset_index(drop=True)
    p2 = df2["price"].reset_index(drop=True)

    # Make both same length
    min_len = min(len(p1), len(p2))
    p1 = p1.iloc[-min_len:]
    p2 = p2.iloc[-min_len:]

    df = pd.DataFrame({
        "price1": p1.values,
        "price2": p2.values
    })

    # OLS Hedge Ratio
    X = sm.add_constant(df["price2"])
    model = sm.OLS(df["price1"], X).fit()
    hedge_ratio = model.params["price2"]

    # Spread
    df["spread"] = df["price1"] - hedge_ratio * df["price2"]

    # Rolling stats
    df["mean"] = df["spread"].rolling(window).mean()
    df["std"] = df["spread"].rolling(window).std()
    df["zscore"] = (df["spread"] - df["mean"]) / df["std"]

    # Rolling correlation
    df["correlation"] = df["price1"].rolling(window).corr(df["price2"])

    return df.dropna(), hedge_ratio
