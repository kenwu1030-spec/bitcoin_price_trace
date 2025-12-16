import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

st.set_page_config(page_title="比特币实时币价", page_icon="₿", layout="wide")

st.title("₿ 比特币实时币价追踪")

# 币安API端点
BINANCE_API = "https://api.binance.com/api/v3"

def get_btc_price():
    """获取BTC/USDT实时价格"""
    try:
        response = requests.get(f"{BINANCE_API}/ticker/price", params={"symbol": "BTCUSDT"})
        data = response.json()
        return float(data['price'])
    except:
        return None

def get_btc_24h_stats():
    """获取24小时统计数据"""
    try:
        response = requests.get(f"{BINANCE_API}/ticker/24hr", params={"symbol": "BTCUSDT"})
        return response.json()
    except:
        return None

# 创建占位符用于实时更新
price_placeholder = st.empty()
stats_placeholder = st.empty()
chart_placeholder = st.empty()

# 初始化价格历史
if 'price_history' not in st.session_state:
    st.session_state.price_history = []
    st.session_state.time_history = []

# 自动刷新控制
auto_refresh = st.sidebar.checkbox("自动刷新", value=True)
refresh_interval = st.sidebar.slider("刷新间隔(秒)", 1, 10, 3)

# 主循环
while True:
    current_price = get_btc_price()
    stats = get_btc_24h_stats()
    
    if current_price and stats:
        # 更新历史数据
        st.session_state.price_history.append(current_price)
        st.session_state.time_history.append(datetime.now().strftime("%H:%M:%S"))
        
        # 只保留最近50个数据点
        if len(st.session_state.price_history) > 50:
            st.session_state.price_history.pop(0)
            st.session_state.time_history.pop(0)
        
        # 显示当前价格
        price_change = float(stats['priceChangePercent'])
        color = "green" if price_change >= 0 else "red"
        
        with price_placeholder.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("当前价格", f"${current_price:,.2f}", f"{price_change:+.2f}%")
            with col2:
                st.metric("24h最高", f"${float(stats['highPrice']):,.2f}")
            with col3:
                st.metric("24h最低", f"${float(stats['lowPrice']):,.2f}")
        
        # 显示详细统计
        with stats_placeholder.container():
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("24h成交量", f"{float(stats['volume']):,.0f} BTC")
            with col2:
                st.metric("24h成交额", f"${float(stats['quoteVolume'])/1e6:,.0f}M")
            with col3:
                st.metric("24h涨跌", f"${float(stats['priceChange']):+,.2f}")
            with col4:
                st.metric("更新时间", datetime.now().strftime("%H:%M:%S"))
        
        # 显示价格走势图
        if len(st.session_state.price_history) > 1:
            df = pd.DataFrame({
                '时间': st.session_state.time_history,
                '价格': st.session_state.price_history
            })
            with chart_placeholder:
                st.line_chart(df.set_index('时间'))
    
    if not auto_refresh:
        break
    
    time.sleep(refresh_interval)
