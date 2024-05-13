import datetime
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request


def get_eom(year, month):
    buf_date_1 = datetime.datetime(year, month, 28)
    buf_date_2 = buf_date_1 + datetime.timedelta(days=4)
    res_date = buf_date_2 - datetime.timedelta(days=buf_date_2.day)

    return res_date


def get_trimmed_down(min_date, dates, values):
    while dates[0] < min_date:
        dates = dates[1:]
        values = values[1:]

    return dates, values


def get_trimmed_up(max_date, dates, values):
    while dates[-1] < max_date:
        buf_date = dates[-1] + datetime.timedelta(days=1)
        buf_date = get_eom(buf_date.year, buf_date.month)
        dates.append(buf_date)
        values.append(np.nan)

    return dates, values


def get_data():
    ipc_data_file = []
    rosstat_ipc_page = urllib.request.urlopen("https://rosstat.gov.ru/statistics/price")
    ipc_soup = BeautifulSoup(rosstat_ipc_page, "html.parser")

    for link in ipc_soup.findAll('a'):
        href = link.get("href")
        if href:
            if "/storage/mediabank/ipc_mes" in href:
                ipc_data_file = 'https://rosstat.gov.ru' + href
                break

    if not ipc_data_file:
        raise Exception("Проверьте ссылку на файл для ИПЦ")

    try:

        ipc_data = pd.read_excel(ipc_data_file, sheet_name='01')
        ipc_years = ipc_data.loc[2].values.tolist()[1:]
        ipc_years = [int(year) for year in ipc_years]
        ipc_months = list(range(1, 13))
        ipc_dates = []
        ipc_values = []

        i = 1
        for y in ipc_years:
            ipc_values += ipc_data.iloc[4:16, i].values.tolist()
            i += 1
            for m in ipc_months:
                ipc_dates.append(get_eom(y, m))

        while np.isnan(ipc_values[-1]):
            ipc_values = ipc_values[:-1]
            ipc_dates = ipc_dates[:-1]

        start_date_ipc = ipc_dates[0]
        end_date_ipc = ipc_dates[-1]

    except Exception:
        raise Exception("Проверьте файл для ИПЦ")

    try:

        m2_data = pd.read_excel('https://www.cbr.ru/vfs/statistics/ms/ms_m21.xlsx', sheet_name='M2')
        m2_dates = m2_data.iloc[4:, 0].values.tolist()
        m2_dates = [d - datetime.timedelta(days=1) for d in m2_dates]
        m2_values = m2_data.iloc[4:, 1].values.tolist()

        start_date_m2 = m2_dates[0]

    except Exception:
        raise Exception("Проверьте файл для M2")

    try:
        d = str(end_date_ipc.day)
        m = str(end_date_ipc.month)
        y = str(end_date_ipc.year)

        if int(m) < 10:
            m = '0' + m

        url_fx = 'https://cbr.ru/Queries/UniDbQuery/DownloadExcel/'
        url_fx += '98956?Posted=True&so=1&mode=1&VAL_NM_RQ=R01235&From=01.07.1992&To='
        url_fx += d + '.' + m + '.' + y + '&FromDate=' + '07%2F01%2F1992&ToDate=' + m + '%2F' + d + '%2F' + y

        fx_data = pd.read_excel(url_fx, sheet_name='RC')
        fx_data = fx_data.groupby([fx_data['data'].dt.year, fx_data['data'].dt.month])['curs'].median()
        fx_dates = []

        for ind in fx_data.index:
            fx_dates.append(get_eom(ind[0], ind[1]))

        fx_values = fx_data.values.tolist()
        fx_values[:66] = [x / 1000 for x in fx_values[:66]]

        start_date_fx = fx_dates[0]

    except Exception:
        raise Exception("Проверьте файл для курса валюты")

    start_date = max(start_date_ipc, start_date_m2, start_date_fx)

    ipc_dates, ipc_values = get_trimmed_down(start_date, ipc_dates, ipc_values)
    fx_dates, fx_values = get_trimmed_down(start_date, fx_dates, fx_values)
    m2_dates, m2_values = get_trimmed_down(start_date, m2_dates, m2_values)

    fx_dates, fx_values = get_trimmed_up(start_date, fx_dates, fx_values)
    m2_dates, m2_values = get_trimmed_up(start_date, m2_dates, m2_values)

    res_dict = {
        'dates': ipc_dates,
        'ipc': ipc_values,
        'm2': m2_values,
        'fx': fx_values
    }
    res = pd.DataFrame.from_dict(res_dict)

    return res


def create_dates_for_forecast(last_date):
    dates_to_predict = [last_date]
    for i in range(6):
        date_buf = dates_to_predict[i] + datetime.timedelta(days=1)
        dates_to_predict.append(get_eom(date_buf.year, date_buf.month))
    dates_to_predict = dates_to_predict[1:]
    return dates_to_predict

