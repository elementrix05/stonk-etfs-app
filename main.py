import streamlit as st
st.set_page_config(layout="wide")
st.write('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)
import requests
import pandas as pd
import yfinance as yf  # yfinance library
import time
import datetime  # datetime library
from datetime import date
from streamlit_lightweight_charts import renderLightweightCharts
import plotly.graph_objects as go
import base64

##Header
LOGO_IMAGE = "Stonks-PNG-Image.png"
st.markdown(
  """
  <style>
  .container {
      display: flex;
      height:50px !important;
      width:300px !important;
  }
  .logo-text {
      float:right;
      font-weight:700 !important;
      font-size:25px !important;
      color: #f9a01b !important;
      margin-left:10px !important;

  }
  .logo-img {
      float:right;
  }
  </style>
  """,
  unsafe_allow_html=True
)

st.markdown(
  f"""
  <div class="container">
      <img class="logo-img" src="data:image/png;base64,{base64.b64encode(open(LOGO_IMAGE, "rb").read()).decode()}">
      <p class="logo-text">Stonk ETFs 📈</p>
  </div>
  """,
  unsafe_allow_html=True
)


##Sidebar

today = date.today()  # today's date
start = st.sidebar.date_input(
    'Start', datetime.date(2022, 1, 1))  # start date input
end = st.sidebar.date_input('End', datetime.date.today())  # end date input
#Read CSV 
etf_df = pd.read_csv('eq_etfseclist.csv',encoding='ISO-8859-1')
etfs = etf_df['Security Name']


#Defining Tabs 
tab1, tab2, tab3 = st.tabs(["Compare ETFs", "Realtime ETF Info", "About"])
with tab1:
  # dropdown for selecting assets
  dropdown = st.multiselect('Pick your assets', etfs)
  
  with st.spinner('Loading...'):  # spinner while loading
    time.sleep(2)
  
  chosen_etfs = []
  for etf in dropdown:
    chosen_etfs.append(etf_df[etf_df['Security Name'] == etf]['Symbol'].values[0]+'.NS')
    
  
  def relativereturn(df):  # function for calculating relative return
    rel = df.pct_change()  # calculate relative return
    cumret = (1+rel).cumprod() - 1  # calculate cumulative return
    cumret = cumret.fillna(0)  # fill NaN values with 0
    return cumret  # return cumulative return
  
  if len(chosen_etfs) > 0:
    relative_df = relativereturn(yf.download(chosen_etfs, start, end))['Adj Close']
    close_df = yf.download(chosen_etfs, start, end)['Adj Close']
    volume_df = yf.download(chosen_etfs, start, end)['Volume']
    chart = ('Line Chart', 'Bar Chart')
    # dropdown for selecting chart type
    dropdown1 = st.selectbox('Pick your chart', chart)
    with st.spinner('Loading...'):  # spinner while loading
        time.sleep(2)
  
    st.subheader('Relative Returns {}'.format(dropdown))
    if(dropdown1 == 'Line Chart'):
      st.line_chart(relative_df)
      st.write("### Closing Price of {}".format(dropdown))
      st.line_chart(close_df)  # display line chart
      st.write("### Volume of {}".format(dropdown))
      st.line_chart(volume_df)  # display line chart
    elif(dropdown1 == 'Bar Chart'):
      st.bar_chart(relative_df)
      st.write("### Closing Price of {}".format(dropdown))
      st.bar_chart(close_df)  # display line chart
      st.write("### Volume of {}".format(dropdown))
      st.bar_chart(volume_df)  # display line chart
  else:
    st.write("Please select at least one asset")
    
with tab2:

  var_etf = st.selectbox('Pick your asset', etfs)
  with st.spinner('Loading...'):  # spinner while loading
    time.sleep(2)
  etf1 = etf_df[etf_df['Security Name'] == var_etf]['Symbol'].values[0]+'.NS'
  etf2 = etf_df[etf_df['Security Name'] == var_etf]['Symbol'].values[0]
  ###ETF API
  baseurl = "https://www.nseindia.com/"
  url = f"https://www.nseindia.com/api/quote-equity?symbol={etf2}"
  headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36",
             'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
  session = requests.Session()
  request = session.get(baseurl, headers=headers, timeout=5)
  cookies = dict(request.cookies)
  response = session.get(url, headers=headers, timeout=5, cookies=cookies)
  data = response.json()
  nav = data.get('priceInfo').get('lastPrice')
  pct_chg = data.get('priceInfo').get('pChange')
  pct_chg = round(pct_chg,2)
  open = data.get('priceInfo').get('open')
  close = data.get('priceInfo').get('close')
  etf_selected = yf.Ticker(etf1)
  wkhi = etf_selected.info.get('fiftyTwoWeekHigh')
  wkmin = etf_selected.info.get('fiftyTwoWeekLow')
  #print(price)

  ###ETF API
  c1,c2,c3,c4,c5=st.columns(5)
  c1.metric(label="Real-time NAV", value='₹ '+str(nav), delta=str(pct_chg)+'%')
  c2.metric(label="Open", value=open)
  c3.metric(label="Close", value=close,)
  c4.metric(label="52 Week High", value=wkhi)
  c5.metric(label="52 Week Low", value=wkmin)

  period_list = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y"]
  period_ix = period_list.index("1d")
  interval_list = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
  interval_ix = interval_list.index("5m")
  plot_spot = st.empty() # holding the spot for the graph
  col1,col2 = st.columns(2)
  with col1:
    etf_period = st.selectbox('pick period', period_list, index=period_ix)
  with col2:
    etf_interval = st.selectbox("pick interval", interval_list, index=interval_ix)
  etf_selected_History = etf_selected.history(period=etf_period,interval=etf_interval)

  fig = go.Figure(data=[go.Candlestick(x=etf_selected_History.index,
                                       open=etf_selected_History['Open'],
                                       high=etf_selected_History['High'],
                                       low=etf_selected_History['Low'],
                                       close=etf_selected_History['Close'])])
  fig.update_layout(xaxis_rangeslider_visible=True,title='Candlestick Chart of {}'.format(var_etf),yaxis_title="Price(₹)",xaxis_title="Time")
  with plot_spot:
    st.plotly_chart(fig, theme='streamlit', use_container_width=True)

with tab3:
  st.subheader("About")

  st.markdown("""
      <style>
  .big-font {
      font-size:25px !important;
  }
  </style>
  """, unsafe_allow_html=True)
  st.markdown('<p class="big-font">StonkETFs is a web application  made for ambitious and woke users like you :) <br> StonkETFs provides you real-time insights on any ETFs (listed on NSE, India) also lets you compare between ETFs on important parameters & past performances...So that you can choose your investments wisely! <br> Cheers!</p>', unsafe_allow_html=True)
  st.subheader("This app wouldn't be possible without Python, Streamlit, Yfinance (Yahoo Finanace), Repl.it ")
  st.subheader('![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) (https://github.com/elementrix05)')
  st.subheader('![LinkedIn](https://img.shields.io/badge/linkedin-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white) (https://www.linkedin.com/in/niraj-wadile/)')