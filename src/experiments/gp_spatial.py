import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import QuantileTransformer


def get_data(file):
    df = pd.read_csv(file)
    qt = QuantileTransformer(output_distribution='normal', random_state=42, n_quantiles=100)
    qt.fit(df.spat.y)

    df = df[df.timestamp == '2021-03-31 15:00:00+00:00']
    x = df[['lon', 'lat']].values
    y = qt.transform(df.spat.y.values).flatten()



    return x, y


if __name__ == '__main__':
    data_file = 'DATA/processed/dataset.csv'
    x, y = get_data(data_file)
    fig = plt.figure(figsize=(12, 12))
    ax = fig.gca()
    plt.scatter(x[:, 0], x[:, 1], c=y, s=400)
    plt.colorbar()
    plt.show()
