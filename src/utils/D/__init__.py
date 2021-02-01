import pandas as pd
from matplotlib import pyplot as plt
from tqdm import tqdm


def get_datetime(i, data_original):
    date = data_original.iloc[i]['<DATE>']
    time = data_original.iloc[i]['<TIME>']
    return pd.to_datetime(f'{date}-{time}', format='%Y%m%d-%H%M%S')


def map_to_time(datetimes):
    result = []
    for i, x in enumerate(datetimes):
        result.append(x.time())
    return result


def make_datetime(df):
    result = []
    for i, row in tqdm(df.iterrows()):
        date = row['<DATE>']
        time = row['<TIME>']
        result.append(pd.to_datetime(f'{date}-{time}', format='%Y%m%d-%H%M%S'))

    return result


def filter_dict(dictionary, condition):
    keys_to_delete = []
    for key in dictionary:
        if condition(dictionary[key]):
            keys_to_delete.append(key)

    for key in keys_to_delete:
        dictionary.pop(key)

    return dictionary


def cum_hist(X, Y, bins, title='No title'):
    assert (len(X) == len(Y))
    x_min = min(X)
    x_max = max(X)

    XY = []

    bins = bins if bins else np.linspace(x_min, x_max, 100)

    for i in range(len(X)):
        XY.append({
            'x': X[i],
            'y': Y[i]
        })

    for i in range(len(bins) - 1):
        xy_i = list(filter(lambda x: bins[i] <= x['x'] < bins[i + 1], XY))
        value = 0
        for j in range(len(xy_i)):
            value += xy_i[j]['y']
        plt.bar(bins[i] / len(xy_i), value, color='b')

    plt.title(title)
    plt.show()


def add_col(data, column_name, array):
    assert(len(data) == len(array))
    data[column_name] = array
    return data
