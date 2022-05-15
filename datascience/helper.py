import pandas as pd

def mean_impute(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    Imputes NaN values in a given column based on the mean of the neighbours. Code taken from:
    https://stackoverflow.com/questions/69899351/interpolate-function-in-pandas-dataframe
    """
    return df[col].interpolate(limit=1).mul(~(df[col].shift(-1).isna() & df[col].isna())).fillna(0)