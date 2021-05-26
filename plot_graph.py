import json
import os
from datetime import datetime

import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objs as go

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


def draw_treemap():
    DATA = pd.read_csv(os.path.join(THIS_FOLDER, 'static/data/summary.csv'))
    DATA.rename(columns={'total_confirmed': '총확진자', 'total_cases_per_1m_population': '백만명당 확진자',
                         'total_deaths': '총사망자', 'total_deaths_per_1m_population': '백만명당 사망자',
                         'death_rate': '확진자 중 사망자 비율',
                         'population': '인구'}, inplace=True)
    # Numerical columns of DATA
    cols_dd = ['총확진자', '백만명당 확진자', '총사망자', '백만명당 사망자', '확진자 중 사망자 비율', '인구']
    # Define which trade will be visible:
    visible = np.array(cols_dd)

    # Define traces and buttons:
    traces = []
    buttons = []
    for value in cols_dd:
        traces.append(go.Treemap(labels=DATA["country"], parents=["country"] * len(DATA["country"]), visible=True if value==cols_dd[0] else False, values=DATA[value]))
        buttons.append(dict(label=value, method='update', args=[{'visible': list(visible == value)}, {'title': f"<b>{value}</b>"}]))

    updatemenus = [{'active': 0, 'buttons': buttons}]

    # Show figure
    fig = go.Figure(data=traces,
                    layout=dict(updatemenus=updatemenus))
    # This is in order to get the first title displayed correctly
    first_title = cols_dd[0]
    fig.update_layout(title=f"2020.01.20 ~ 2021.05.23 국가별 <b>{first_title}</b> 현황")
    treemapJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return treemapJSON


def draw_geo_map():
    daily = pd.read_csv(os.path.join(THIS_FOLDER, 'static/data/daily.csv'))
    daily["date"] = pd.to_datetime(daily["date"], format='%Y-%m-%d')
    daily.sort_values(by='date', inplace=True)
    fig = px.choropleth(daily, locations="country",
                        color=(daily["daily_new_cases"]),
                        locationmode='country names', hover_name="country",
                        animation_frame=daily["date"].dt.strftime('%Y-%m-%d'),
                        color_continuous_scale=px.colors.sequential.matter)
    fig.update_layout(title="<b>2020년 1월 부터 2021년 5월까지 일일 확진자수</b>")
    geo_mapJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return geo_mapJSON


def draw_barchart():
    DATA = pd.read_csv(os.path.join(THIS_FOLDER, 'static/data/summary.csv'))
    DATA.rename(columns={'total_vaccinations': '백신 접종 횟수', 'percentage_vaccinated': '백신 접종 횟수 / 인구 비율',
                         'fully_vaccintated_rate': '접종 완료 인구 비율'}, inplace=True)
    # Numerical columns of DATA
    cols_dd = ['백신 접종 횟수', '백신 접종 횟수 / 인구 비율', '접종 완료 인구 비율']
    # Define which trade will be visible:
    visible = np.array(cols_dd)

    # Define traces and buttons:
    traces = []
    buttons = []
    for value in cols_dd:
        DATA = DATA.sort_values(value, ascending=False).dropna(subset=[value]).iloc[:20]
        traces.append(go.Bar(hoverinfo='skip', visible=True if value==cols_dd[0] else False, x=DATA['country'], y=DATA[value],),)
        buttons.append(dict(label=value, method='update', args=[{'visible': list(visible==value)}, {'title': f"<b>{value} 상위 20개국 현황</b>"}]))

    updatemenus = [{'active': 0, 'buttons': buttons}]

    # Show figure
    fig = go.Figure(data=traces,
                    layout=dict(updatemenus=updatemenus))

    # This is in order to get the first title displayed correctly
    first_title = cols_dd[0]
    fig.update_layout(
        title=f"<b>백신 접종 상위 20개국 현황</b>",
        xaxis_title=f"Top 20 Countries",
        yaxis_title=value,
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode="x"
    )
    barJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return barJSON


def case_vacc():
    daily = pd.read_csv(os.path.join(THIS_FOLDER, 'static/data/daily.csv'))
    vacc = pd.read_csv(os.path.join(THIS_FOLDER, 'static/data/vacc.csv'))
    new_daily = daily[['date', 'country', 'daily_new_cases', 'daily_new_deaths']].sort_values(by="date")
    new_vacc = vacc[['date', 'country', 'daily_vaccinations', 'daily_vaccinations_per_million']].sort_values(by="date")
    new_vacc.date = new_vacc.date.apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
    new_daily.date = new_daily.date.apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))

    # use only common countries and dates 
    countries = new_vacc.dropna(subset=['daily_vaccinations'])['country'].unique()
    dates = new_vacc.dropna(subset=['daily_vaccinations'])['date'].unique()
    country_mask = new_daily.country.apply(lambda x: x in countries)
    date_mask = new_daily.date.apply(lambda x: x in dates)
    fig = go.Figure(data=[
        go.Bar(
            name="New Cases",
            x=new_daily[country_mask & date_mask][new_daily['country'] == 'USA']['date'],
            y=new_daily[country_mask & date_mask][new_daily['country'] == 'USA']['daily_new_cases'],
            marker_color="crimson",
        ),
        go.Bar(
            name="Vaccinated",
            x=new_vacc[new_vacc['country'] == 'USA']['date'],
            y=new_vacc[new_vacc['country'] == 'USA']['daily_vaccinations'],
            marker_color="lightseagreen"
        ),

    ])

    fig.update_layout(
        title="USA 일간 백신 접종, 일간 신규 확진 그래프",
        xaxis_title="Date",
        yaxis_title="Count",
        plot_bgcolor='rgba(0,0,0,0)',
        barmode='stack',
        hovermode="x"
    )

    case_vaccJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return case_vaccJSON


def draw_geo_scatter():
    # Create a Continent column:
    data = pd.read_csv(os.path.join(THIS_FOLDER, 'static/data/summary.csv'))
    data['confirmed_rate'] = data['total_confirmed']*100/data['population']
    data['death_rate'] = data['total_deaths']*100/data['total_confirmed']
    data['fully_vaccintated_rate'] = data['people_fully_vaccinated']*100/data['population']
    data = data.dropna()
    cols = ['confirmed_rate', 'death_rate', 'percentage_vaccinated', 'fully_vaccintated_rate']
    scatters = []
    for value in cols:
        fig = px.scatter_geo(data, locations="country", color="continent",
                             locationmode='country names',
                             hover_name="country", size=value,
                             projection="natural earth")
        txt = value
        fig.update_layout(title=txt, title_x=0.45)
        scatters.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))
    return scatters
