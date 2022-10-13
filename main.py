import streamlit as st
import pandas as pd

from utils import get_trading_pair, levels_, chart_

PERIOD = ['1d','5d','1mo','3mo','6mo','1y','2y','5y','10y','ytd','max']
INTERVAL = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

st.title('Automatic support resistance levels.')

pair, period, interval, saturation_point = st.columns(4)

pair = pair.text_input("Currency Pair", "BTC-USD", max_chars=10)
period = period.selectbox("Period", PERIOD, 1)
interval = interval.selectbox("Interval", INTERVAL, 4)
sp = saturation_point.slider('Select saturation point.', min_value=0.0, max_value=1.0, value=0.5, step=0.05)
# h = chart_height.slider("Chart Height", min_value=300, max_value=1200, value=600, step=10)

data = get_trading_pair(pair, period, interval)

levels = levels_(data, saturation_point=sp)

st.altair_chart((chart_(data) + levels), use_container_width=True)
