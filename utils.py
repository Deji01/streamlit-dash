from math import isnan


def fillna_mode(dataframe):
    """Replace nan values in a row with the most common value (mode)"""
    opts = list(dataframe.columns)
    df = dataframe[opts].mode(axis=1).reset_index()
    mode_lst = list(zip(df.iloc[:, 0], df.iloc[:, 1]))
    for idx in dataframe.index:
        for index, value in enumerate(dataframe.loc[idx].values):
            if isnan(value):
                value = dict(mode_lst)[idx]
                dataframe.loc[idx].values[index] = value
    return dataframe


def style_negative(value, props=""):
    "Styles negative values in  a dataframe"
    try:
        return props if value < 0 else None
    except:
        pass


def style_positive(value, props=""):
    "Styles positive values in  a dataframe"
    try:
        return props if value > 0 else None
    except:
        pass
