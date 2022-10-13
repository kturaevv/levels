import yfinance
import streamlit as st
import pandas as pd
import altair as alt

from support_resistance import KmeansSupportResistance

def progress():
    # Add a placeholder
    latest_iteration = st.empty()
    bar = st.progress(0)

    for i in range(100):
        # Update the progress bar with each iteration.
        latest_iteration.text(f'Iteration {i+1}')
        bar.progress(i + 1)
    'Done!'

@st.cache(show_spinner=True)
def get_trading_pair(name="BTC-USD", period="5d", interval="30m") -> pd.DataFrame:
    # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    btc = yfinance.Ticker(name)
    df = btc.history(period=period, interval=interval)
    df.drop(columns=['Volume', 'Dividends', 'Stock Splits'], inplace=True)
    df.reset_index(inplace=True)
    return df

@st.cache(show_spinner=True, allow_output_mutation=True)
def chart_(data: pd.DataFrame, height=600):
        
    base = alt.Chart(data).encode(
        alt.X('Datetime:T', axis=alt.Axis(labelAngle=-45)),
        color=alt.condition("datum.Open <= datum.Close", alt.value("#06982d"), alt.value("#ae1325"))
    )

    chart = alt.layer(
        base.mark_rule().encode(alt.Y('Low:Q', title='Price', scale=alt.Scale(zero=False)), alt.Y2('High:Q')),
        base.mark_bar().encode(alt.Y('Open:Q'), alt.Y2('Close:Q')),
    ).properties(height=600).interactive()

    return chart

@st.cache(show_spinner=True, allow_output_mutation=True)
def levels_(data: pd.DataFrame, saturation_point=0.5, color_value="#fa8d0b"):
    levels = KmeansSupportResistance(data[['Low']], saturation_point=saturation_point).levels
    levels = pd.DataFrame({'Low': levels})
    line = alt.Chart(levels).mark_rule().encode(y='Low:Q', color=alt.value(color_value))
    return line