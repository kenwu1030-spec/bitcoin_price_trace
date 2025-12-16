import streamlit as st
from transformers import pipeline
import pandas as pd
from datetime import datetime
import re

# 页面配置
st.set_page_config(page_title="信贷智能初审系统", page_icon="🏦", layout="wide")

# 缓存模型加载
@st.cache_resource
def load_models():
    # 文本风险分类 - 使用金融情感分析模型
    risk_classifier = pipeline("text-classification", 
                              model="ProsusAI/finbert",
                              top_k=None)
    # 命名实体识别 - 提取收入等关键信息
    ner_model = pipeline("ner", 
                        model="dslim/bert-base-NER",
                        aggregation_strategy="simple")
    return risk_classifier, ner_model

risk_classifier, ner_model = load_models()

# 收入真实性校验函数
def verify_income(text, stated_income):
    # 提取文本中的数字
    numbers = re.findall(r'\d+(?:,\d{3})*(?:\.\d+)?', text.replace(',', ''))
    numbers = [float(n) for n in numbers]
    
    # 检查陈述收入是否在文本提及的范围内
    if stated_income in numbers:
        return "✅ 一致", 100
    elif any(abs(stated_income - n) / stated_income < 0.1 for n in numbers if n > 0):
        return "⚠️ 基本一致", 80
    else:
        return "❌ 不一致", 30

# 风险评分函数
def calculate_risk_score(sentiment_result, income_score):
    # FinBERT 返回 positive/negative/neutral
    sentiment_map = {"positive": 80, "neutral": 50, "negative": 20}
    sentiment_score = max([sentiment_map.get(s['label'].lower(), 50) 
                          for s in sentiment_result], default=50)
    
    # 综合评分 (60% 文本风险 + 40% 收入真实性)
    final_score = sentiment_score * 0.6 + income_score * 0.4
    
    if final_score >= 70:
        return final_score, "🟢 低风险 - 建议通过", "green"
    elif final_score >= 50:
        return final_score, "🟡 中风险 - 人工复核", "orange"
    else:
        return final_score, "🔴 高风险 - 建议拒绝", "red"

# UI 界面
st.title("🏦 客户信贷申请智能初审系统")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 申请信息录入")
    
    applicant_name = st.text_input("申请人姓名", placeholder="张三")
    application_text = st.text_area(
        "申请陈述 (描述收入来源、工作情况、贷款用途等)",
        height=150,
        placeholder="我在某科技公司工作5年，月收入15000元，工作稳定。申请贷款用于购买家庭用车..."
    )
    stated_income = st.number_input("申报月收入 (元)", min_value=0, value=15000, step=1000)

with col2:
    st.subheader("⚙️ 系统信息")
    st.info(f"📅 审核时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.info("🤖 模型: FinBERT + BERT-NER")

if st.button("🚀 开始智能初审", type="primary", use_container_width=True):
    if not application_text:
        st.error("请输入申请陈述！")
    else:
        with st.spinner("AI 分析中..."):
            # 1. 文本风险分类
            risk_result = risk_classifier(application_text)[0]
            
            # 2. 收入真实性校验
            income_status, income_score = verify_income(application_text, stated_income)
            
            # 3. 综合评分
            final_score, decision, color = calculate_risk_score(risk_result, income_score)
        
        st.markdown("---")
        st.subheader("📊 初审结果")
        
        # 结果展示
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("综合评分", f"{final_score:.1f}", delta=None)
        with col_b:
            st.metric("收入校验", income_status.split()[0], delta=None)
        with col_c:
            st.markdown(f"### :{color}[{decision.split()[1]}]")
        
        # 详细分析
        with st.expander("📋 详细分析报告"):
            st.write("**文本情感分析:**")
            for item in risk_result:
                st.write(f"- {item['label']}: {item['score']:.2%}")
            
            st.write(f"\n**收入真实性:** {income_status} (得分: {income_score})")
            st.write(f"**申报收入:** ¥{stated_income:,.0f}")
            
            st.write(f"\n**最终建议:** {decision}")

# 侧边栏 - 批量处理
with st.sidebar:
    st.header("📦 批量处理")
    uploaded_file = st.file_uploader("上传 CSV 文件", type=['csv'])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write(f"已加载 {len(df)} 条记录")
        if st.button("批量审核"):
            st.info("批量处理功能开发中...")
    
    st.markdown("---")
    st.markdown
Checkpoint
Restore
# 我想做一个追踪比特币实时币价的 应用。 在币安抓数据， 显示代码 只做这个需求

Kiro
好的，我来帮你做一个追踪比特币实时币价的应用，从币安抓取数据并显示。

这是一个简洁的实现方案，使用 Streamlit + 币安 API：

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
