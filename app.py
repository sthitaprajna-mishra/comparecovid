import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# fetch data from api endpoint
DATA_URL=('https://api.covid19india.org/csv/latest/state_wise_daily.csv')

def load_data():
    data=pd.read_csv(DATA_URL)
    return data
covid_data=load_data()

# read states list
states = pd.read_csv('state_abbreviations.csv')

# sidebar text
st.sidebar.markdown("### Corona Comparator")
st.sidebar.markdown("Compare the second wave of Covid-19 in 2021 with the first wave \
    which occurred in 2020, for each state/UT in India.")
st.sidebar.markdown("Choose 'Total' for comparison at the national level.")

# select state
state_name = st.sidebar.selectbox('Select a State', states['State/ UT'])
select = states.loc[states[states['State/ UT'] == state_name].index[0]]['Abbreviation']

# select status
select_status = st.sidebar.radio("Covid-19 case status", ('Confirmed', 'Recovered', 'Deceased'))

# trace option
trace = st.sidebar.checkbox("Add Trace", True, key=1)
st.sidebar.markdown("Adding a trace will create a straight line on the plot passing through the current day. \
This will allow the viewer to draw finer comparisons between the two line plots.")

# profile links
st.sidebar.markdown("------")
st.sidebar.markdown("### Created By- ")
st.sidebar.markdown("#### Sthitaprajna Mishra")
st.sidebar.markdown("------")
st.sidebar.markdown("[LinkedIn](https://www.linkedin.com/in/sthitaprajna-mishra-b63940153/)")
st.sidebar.markdown("[Medium](https://www.medium.com/@sthitaprajna360/)")
st.sidebar.markdown("[GitHub](https://github.com/sthitaprajna-mishra)")

# get dataframe for selected state
def get_state_dataframe(dataset, abbv):
    state_data = dataset[['Date', 'Date_YMD', 'Status', abbv]]
    return state_data
state_data = get_state_dataframe(covid_data, select)

# state 2020 df
end_date = '2020-12-31'
state_20 = state_data.loc[state_data['Date_YMD'] <= end_date]

# state 2020 status df
state_20_status = state_20[state_20['Status']==select_status]
state_20_status['Date_YMD'] = state_20_status['Date_YMD'].str[5:]

# state 2021 status df
state_21_status = state_data.loc[(state_data['Date_YMD']>='2021-03-14') & (state_data['Status']==select_status)]
state_21_status['Date_YMD'] = state_21_status['Date_YMD'].str[5:]

# merge 2021 data with 2020 data
state_21_list = list(state_21_status[select])
n = len(state_20_status) - len(state_21_status)
zeroes_list = [0]*n
state_21_list.extend(zeroes_list)
state_20_status['OR_21'] = state_21_list

# replace 0s with NaN
state_20_status['OR_21'] = state_20_status['OR_21'].replace(0, np.nan)

# -------------- PLOT ---------------
fig = px.line(state_20_status,
        x=state_20_status['Date'].str[:6],
        y=[select, 'OR_21'], 
        labels = {'OR':'2020', 'OR_21':'2021'},
       title="Covid-19 %s Cases 2020 vs 2021 in %s" % (select_status, state_name if state_name != 'Total' else 'India'))

def customLegendPlotly(fig, nameSwap): 
    for i, dat in enumerate(fig.data): 
        for elem in dat: 
            if elem == 'hovertemplate': 
                fig.data[i].hovertemplate = fig.data[i].hovertemplate.replace(fig.data[i].name, nameSwap[fig.data[i].name]) 
        for elem in dat: 
            if elem == 'name': 
                fig.data[i].name = nameSwap[fig.data[i].name] 
    return fig

fig = customLegendPlotly(fig=fig, nameSwap = {select: '2020', 'OR_21':'2021'})

# if all values are NaN in 2021
value = True
for i in state_20_status['OR_21'].isnull():
    if not i:
        value = False

if trace and not value:
    result = pd.Series(state_20_status['OR_21']).last_valid_index()
    today_x = state_20_status.loc[result]['Date'][:6]
    today_y = int(state_20_status.loc[result]['OR_21'])
    fig.add_trace(
        go.Scatter(
            name='trace',
            x=['14-Mar', '31-Dec'],
            y=[today_y, today_y],
            mode="lines",
            line=dict(
                dash='dash',
                color='green',
                width=0.5
            ),
            showlegend=True),
    )
    fig.add_trace(
        go.Scatter(
            name='trace',
            x=[today_x, today_x],
            y=[0, today_y],
            mode="lines",
            line=dict(
                dash='dash',
                color='green',
                width=0.5
            ),
            showlegend=False),
    )

fig.update_layout(xaxis=dict(tickangle=-90), xaxis_title='Timeline', yaxis_title='Number of Patients')
st.plotly_chart(fig)