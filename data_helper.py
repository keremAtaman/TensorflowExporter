import pandas as pd
from numpy import array
from numpy import reshape
from math import floor

def convert_to_numpy(df:pd.DataFrame):
    return df.to_numpy()


def drop_low_stdev_columns(df:pd.DataFrame, std_minimum:float = 0.0):
    """Drops columns from the given DataFrame whose stdev is <= std_minimum

    Args:
        df (pd.DataFrame): Input dataframe
        std_minimum (float, optional):  The minimum stdev allowed. 
            Any column whose stdev is <= this will be dropped
            Defaults to 0.0.

    Returns:
        list(str): The names of dropped columns
        pd.DataFrame: The dataframe with the columns dropped
    """
    cols_= df.std() <= std_minimum
    cols_index = cols_.index
    dropped_cols = []
    for i in range(len(cols_)):
        if cols_[i]:
            dropped_cols.append(cols_index[i])
    return [dropped_cols,df.drop(df.std()[cols_].index.values, axis=1)]

def _create_dataset(dataset, look_back=1):
	dataX, dataY = [], []
	for i in range(len(dataset)-look_back-1):
		a = dataset[i:(i+look_back), 0]
		dataX.append(a)
		dataY.append(dataset[i + look_back, 0])
	return array(dataX), array(dataY)

def reshape_input_for_nn(x:array, time_steps = 64,samples = None):
    if samples == None:
        samples = 1
    num_rows_to_remove = x.shape[0]%(time_steps * samples)
    if num_rows_to_remove > 0:
        x = x[:-num_rows_to_remove, :]
    else:
        return x.reshape(samples,time_steps,x.shape[1])

def create_training_and_testing_arrays(x:array,y:array,train_data_percentage=1):
    train_size = round(len(x) * train_data_percentage)
    train_x = x[0:train_size,:]
    train_y = y[0:train_size,:]
    test_x = x[train_size:len(x),:]
    test_y = y[train_size:len(x),:]
    return [train_x,train_y,test_x,test_y]

# FIXME: this whole function is a patchwork mess
def create_input_and_output_arrays_for_nn(
        input_df,
        label_df,
        look_back,
        cols_to_drop,
        input_mean:pd.Series = pd.Series(),
        input_std:pd.Series = pd.Series(),
        label_mean:pd.Series = pd.Series(),
        label_std:pd.Series = pd.Series())->dict:
    #drop cols
    [input_df,label_df] = equalize_num_inputs_with_num_labels(input_df,label_df,look_back)
    [input_array,dropped_cols,input_df_mean,input_df_std] = create_input_array(input_df,cols_to_drop,input_mean,input_std)
    [label_array,label_df_mean,label_df_std] = create_label_array(label_df,label_mean,label_std)
    [train_x,train_y,test_x,test_y] = create_training_and_testing_arrays(input_array,label_array)
    train_x = reshape_input_for_nn(train_x,look_back,train_y.shape[0])
    return {'train_x':train_x,
            'train_x_mean': input_df_mean,
            'train_x_std':input_df_std,
            'train_y':train_y,
            'train_y_mean':label_df_mean,
            'train_y_std':label_df_std,
            'dropped_input_cols':dropped_cols}


def create_input_array(
    input_df:pd.DataFrame, 
    cols_to_drop = None,
    mean:pd.Series = pd.Series(),
    std:pd.Series = pd.Series()):
    #input_array creation
    #drop non-numerical columns
    input_df = input_df.reset_index(drop=True)
    input_df = input_df.drop(columns = ['event_type'])
    #convert NaNs to zeros
    input_df = input_df.fillna(0)
    #get rid of 0 variance columns
    if cols_to_drop == None:
        #drop cols as normal
        [dropped_cols,input_df] = drop_low_stdev_columns(input_df)
    else:
        #drop the specified columns
        input_df = input_df.drop(columns = cols_to_drop)
        dropped_cols = cols_to_drop
    #normalize and keep the normalizers
    if len(mean) == 0:
        mean = input_df.mean()
    if len(std) == 0:
        std = input_df.std()
    input_df=(input_df-mean)/std
    
    #convert to numpy array
    input_array = input_df.to_numpy()

    return [input_array,dropped_cols,mean,std]

def create_label_array(
    label_df:pd.DataFrame,
    mean:pd.Series = pd.Series(),
    std:pd.Series = pd.Series()):
    #drop non-numerical columns
    label_df = label_df.drop(columns = ['event_ts'])
    #normalize
    if len(mean) == 0:
        mean = label_df.mean()
    if len(std) == 0:
        std = label_df.std()
    label_df = (label_df-mean)/std
    #convert NaNs to zeros
    label_df = label_df.fillna(0)
    #convert to numpy array
    label_array = label_df.to_numpy()
    return [label_array,mean,std]

def equalize_num_inputs_with_num_labels(input_df:pd.DataFrame,label_df,look_back):
        label_timestamps = label_df['event_ts']
        if(len(label_timestamps) == len(input_df)):
            return input_df
        input_df = input_df.set_index(['event_ts'])
        new_label_df = label_df
        new_input_df = pd.DataFrame()
        idx = 0
        for label_timestamp in label_timestamps:
            mini_input_df = input_df.loc[pd.Timestamp.min:label_timestamp]
            if len(mini_input_df) < look_back:
                new_label_df = new_label_df.drop(new_label_df.index[0])
                continue
            mini_input_df = mini_input_df.tail(look_back)
            new_input_df = new_input_df.append(mini_input_df)
            idx+=1
        return [new_input_df,new_label_df]