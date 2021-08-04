from numpy import array
import pandas as pd
from typing import List
import run_config as rc

def unnormalize(
    x:array,
    x_mean:pd.Series,
    x_std:pd.Series
)->array:
    x_df = pd.DataFrame(x,columns = x_mean.keys())
    x_df = x_df * x_std + x_mean
    return x_df.to_numpy()

def convert_array_to_df(
    x:array,
    col_names:List[str]
) -> pd.DataFrame:
    return pd.DataFrame(x,columns = col_names)

def merge_two_dataframes(
    df_1:pd.DataFrame,
    df_2:pd.DataFrame
)->pd.DataFrame:
    return pd.concat([df_1,df_2], axis = 1)

def match_data_to_column_type(
    df:pd.DataFrame,
    column_types:rc.COLUMN_TYPE,
    categorical_threshold = 0.3
)->pd.DataFrame:
    result = df
    for col_idx in range(df.shape[1]):
        for row_idx in range(df.shape[0]):
            entry = 0
            actual_data = df.iloc[row_idx,col_idx]
            if column_types[col_idx] == rc.COLUMN_TYPE.CATEGORICAL:
                if actual_data < categorical_threshold:
                    entry = 0
                else:
                    entry = 1
            elif column_types[col_idx] == rc.COLUMN_TYPE.NON_NEGATIVE_NUMERICAL:
                entry = max(0,actual_data)
            result.iloc[row_idx,col_idx] = entry

    return result

def work(
    array:array,
    headings:List[str],
    column_types:List[rc.COLUMN_TYPE],
    mean:pd.Series,
    std:pd.Series
)->pd.DataFrame:
    return match_data_to_column_type(
        convert_array_to_df(
            unnormalize(
                array,
                mean,
                std
            ),
            headings
        ),
        column_types 
    )