import pandas as pd
import matplotlib.pyplot as plt
import warnings

from sklearn.ensemble import IsolationForest
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from func import get_data, create_dates_for_forecast

warnings.simplefilter("ignore")


def get_plot():
    # Скачивание данных, исключение 90-х и перевод M2 и FX в приросты
    df = get_data()
    df = df[df['dates'] > '2000-01-01']
    df['m2'] = df['m2'] / df['m2'].shift(1) - 1
    df['fx'] = df['fx'] / df['fx'].shift(1) - 1

    # "Подстригание" квантилей
    df.loc[df['ipc'] > df['ipc'].quantile(0.99), 'ipc'] = df['ipc'].quantile(0.99)
    df.loc[df['ipc'] < df['ipc'].quantile(0.01), 'ipc'] = df['ipc'].quantile(0.01)
    df.loc[df['m2'] > df['m2'].quantile(0.99), 'm2'] = df['m2'].quantile(0.99)
    df.loc[df['m2'] < df['m2'].quantile(0.01), 'm2'] = df['m2'].quantile(0.01)
    df.loc[df['fx'] > df['fx'].quantile(0.99), 'fx'] = df['fx'].quantile(0.99)
    df.loc[df['fx'] < df['fx'].quantile(0.01), 'fx'] = df['fx'].quantile(0.01)

    df['year'] = df['dates'].apply(lambda x: x.year)
    df['month'] = df['dates'].apply(lambda x: x.month)

    for l in range(1, 9):
        df['ipc_' + str(l)] = df['ipc'].shift(l)
        if l >= 6:
            df['m2_' + str(l)] = df['m2'].shift(l)
            df['fx_' + str(l)] = df['fx'].shift(l)
        else:
            df['year_' + str(l)] = df['year'].shift(l)
            df['month_' + str(l)] = df['month'].shift(l)

    df.dropna(inplace=True)

    dates = df['dates'].values

    y_train = df[['ipc', 'ipc_1', 'ipc_2', 'ipc_3', 'ipc_4', 'ipc_5']]
    x_train = df.drop(['dates', 'ipc', 'ipc_1', 'ipc_2', 'ipc_3', 'ipc_4', 'ipc_5', 'm2', 'fx'], axis=1)
    iso_forest = IsolationForest()
    iso_forest.fit(x_train)
    x_train['outlier'] = iso_forest.predict(x_train)

    params = {'n_estimators': 100, 'max_depth': 4, 'min_samples_split': 2,
              'min_samples_leaf': 2, 'learning_rate': 0.5, 'subsample': 1
              }

    gbr = MultiOutputRegressor(GradientBoostingRegressor(loss="quantile", alpha=0.5, **params))
    gbr.fit(x_train, y_train)
    y_pred = gbr.predict(x_train)
    error_pred = y_train - y_pred
    error_q_025 = error_pred.quantile(0.025).values
    error_q_975 = error_pred.quantile(0.975).values

    dates_to_forecast = create_dates_for_forecast(pd.to_datetime(dates[-1]))
    dict_to_forecast = {
        'dates': dates_to_forecast,
        'year': [x.year for x in dates_to_forecast],
        'month': [x.month for x in dates_to_forecast]
    }
    df_to_forecast = pd.DataFrame(dict_to_forecast)

    for l in range(3):
        if l == 0:
            df_to_forecast['ipc_' + str(6 + l)] = df.iloc[-(6 + l):, 1].values
            df_to_forecast['m2_' + str(6 + l)] = df.iloc[-(6 + l):, 2].values
            df_to_forecast['fx_' + str(6 + l)] = df.iloc[-(6 + l):, 3].values
        else:
            df_to_forecast['ipc_' + str(6 + l)] = df.iloc[-(6 + l):(-l), 1].values
            df_to_forecast['m2_' + str(6 + l)] = df.iloc[-(6 + l):(-l), 2].values
            df_to_forecast['fx_' + str(6 + l)] = df.iloc[-(6 + l):(-l), 3].values

    for l in range(1, 6):
        df_to_forecast['year_' + str(l)] = df_to_forecast['year'].shift(l)
        df_to_forecast['month_' + str(l)] = df_to_forecast['month'].shift(l)

    df_to_forecast.dropna(inplace=True)
    x_to_forecast = df_to_forecast.drop(['dates'], axis=1)
    x_to_forecast['outlier'] = iso_forest.predict(x_to_forecast)
    forecast = gbr.predict(x_to_forecast)
    forecast_025 = forecast[0] + error_q_025
    forecast_975 = forecast[0] + error_q_975
    forecast = forecast[0][::-1]
    forecast_025 = forecast_025[::-1]
    forecast_975 = forecast_975[::-1]

    dates_to_plot = [pd.Timestamp(d) for d in dates] + [pd.Timestamp(d) for d in dates_to_forecast]
    ipc_to_plot = df.ipc.values.tolist() + forecast.tolist()

    plt.figure(figsize=(10, 10))
    plt.plot(dates_to_plot[-36:], ipc_to_plot[-36:], "b-", markersize=10, label="ИПЦ")
    plt.plot(dates_to_forecast, forecast, "r-", label="Прогноз ИПЦ")
    plt.plot(dates_to_forecast, forecast_975, "k-")
    plt.plot(dates_to_forecast, forecast_025, "k-")
    plt.fill_between(
        dates_to_forecast, forecast_025, forecast_975, alpha=0.4, label="95% доверительный интервал"
    )
    plt.legend(loc="lower right")
    plt.grid(color='g', linestyle='--', linewidth=0.5)

    return plt
