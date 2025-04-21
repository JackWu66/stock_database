import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import plotly.graph_objects as go
import os


def stockname(stock_id):
    cursor.execute(f"SELECT `stock_name` FROM stock_id_list WHERE stock_ID = '{stock_id}'")
    result = cursor.fetchone()
    return result[0] if result else ""


def get_capital(stock_id):
    cursor.execute(f"SELECT `資本額(萬張)` FROM stock_id_list WHERE stock_ID = '{stock_id}'")
    result = cursor.fetchone()
    return result[0] if result else None

st.title("📊 成交活躍度前30名趨勢圖")

def handle_checkbox_change(changed_label):
    if changed_label == "全部資本額" and st.session_state[f"check_全部資本額"]:
        # 全部資本額被選，取消其他
        for label in capital_ranges:
            if label != "全部資本額":
                st.session_state[f"check_{label}"] = False
    elif changed_label != "全部資本額" and st.session_state[f"check_{changed_label}"]:
        # 選了非全部資本額，取消全部資本額
        st.session_state[f"check_全部資本額"] = False

# 查詢當日股價
def get_stock_price(stock_id, date):
    cursor.execute(f"""
        SELECT `close` FROM `{stock_id}` WHERE `date` = %s
    """, (date,))
    row = cursor.fetchone()
    return row[0] if row else None

def get_all_stock_prices(stock_id, dates):
    # dates 是 list（例如 df.columns[::-1]），回傳一樣長度的股價 list
    prices = []
    for date in dates:
        cursor.execute(f"""
            SELECT `close` FROM `{stock_id}` WHERE `date` = %s
        """, (date,))
        row = cursor.fetchone()
        prices.append(row[0] if row else None)
    return prices


# 設定中文字體（macOS）
font_path = "/System/Library/Fonts/STHeiti Light.ttc"
plt.rcParams['font.family'] = fm.FontProperties(fname=font_path).get_name()

# 自訂 CSS 樣式
st.markdown("""
    <style>
    .custom-button {
        border: none;
        padding: 0.5rem 1rem;
        margin: 0.2rem 0;
        border-radius: 5px;
        background-color: #f0f0f0;
        color: #333;
        width: 100%;
        text-align: center;
        display: inline-block;
        font-size: 16px;
        cursor: pointer;
    }
    .custom-button:hover {
        background-color: #d0e7ff;
        color: #000;
    }
    .custom-button.selected {
        background-color: #4CAF50 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# MySQL 連線
try:
    db = mysql.connector.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME'],
        charset='utf8mb4',
    )
    print("✅ 成功連線到 Google Cloud SQL")
except Exception as e:
    print("❌ 連線失敗：", e)


cursor = db.cursor()



# 最新10個交易日
cursor.execute("SELECT DISTINCT date FROM `23001` ORDER BY date DESC LIMIT 10")
latest_10_dates = sorted([row[0] for row in cursor.fetchall()], reverse=True)

# 所有股票表
cursor.execute("""
    SELECT table_name FROM information_schema.tables
    WHERE table_schema = 'stockdatabase' AND table_name NOT IN ('23001', 'stock_id_list')
""")
all_stock_ids = [row[0] for row in cursor.fetchall()]

# 初始化 session_state
st.session_state.setdefault("selected_capital_labels", "全部資本額")
st.session_state.setdefault("selected_ref_date", latest_10_dates[0])

# 資本額範圍
cursor.execute("SELECT stock_ID, `資本額(萬張)` FROM stock_id_list")
rows = cursor.fetchall()
capital_dict = {row[0]: row[1] for row in rows if row[1] is not None}

capital_ranges = {
    "全部資本額": (0, float('inf')),
    "小於10億": (0, 10),
    "10~20億": (10, 20),
    "20~30億": (20, 30),
    "30~50億": (30, 50),
    "50~100億": (50, 100),
    "100~200億": (100, 200),
    "200~500億": (200, 500),
    "500~1000億": (500, 1000),
    "1000億以上": (1000, float('inf'))
}

# 資本額按鈕
st.subheader("📌 選擇資本額區間")
selected_ranges = []
cols = st.columns(3)
# 每個按鈕設定
for idx, (label, (min_cap, max_cap)) in enumerate(capital_ranges.items()):
    count = sum(1 for cap in capital_dict.values() if min_cap <= cap < max_cap)
    col = cols[idx % 3]
    checked = st.session_state.get(f"check_{label}", False)
    col.checkbox(
        f"{label}（{count}檔）",
        value=checked,
        key=f"check_{label}",
        on_change=handle_checkbox_change,
        args=(label,)
    )
    if st.session_state.get(f"check_{label}", False):
        selected_ranges.append(label)

st.session_state.selected_capital_labels = selected_ranges

# 再依選取狀態印出標示
selected_labels = st.session_state.selected_capital_labels
if not selected_labels:
    st.warning("請選擇至少一個資本額區間")
    st.stop()
# 顯示目前選取區間
st.success(f"✅ 已選擇資本額區間：{'、'.join(selected_labels)}")

# 收集多個範圍股票
selected_ranges_combined = [
    (label, capital_ranges[label]) for label in selected_labels if label in capital_ranges
]

# 透過 hidden field 處理點擊
capital_input = st.query_params.get("capital_label", None)
if capital_input:
    st.session_state.selected_capital_label = capital_input[0]

# 選定範圍
selected_labels = st.session_state.selected_capital_labels
st.write(f"✅ 已選擇資本額區間：**{'、'.join(selected_labels)}**")

# 合併所有範圍內的股票
filtered_stock_ids = []
for stock_id in all_stock_ids:
    if stock_id not in capital_dict:
        continue
    capital = capital_dict[stock_id]
    for label, (min_cap, max_cap) in selected_ranges_combined:
        if min_cap <= capital < max_cap:
            filtered_stock_ids.append(stock_id)
            break

# 每日前30名
top30_per_day = {}
for date in latest_10_dates:
    top30_list = []
    for stock_id in filtered_stock_ids:
        try:
            cursor.execute(f"DESC `{stock_id}`")
            columns = [row[0] for row in cursor.fetchall()]
            if "量資排名" not in columns or "量資比％" not in columns:
                continue
            cursor.execute(f"""
                SELECT `量資比％` FROM `{stock_id}` WHERE `date` = %s
            """, (date,))
            row = cursor.fetchone()
            if row and row[0] is not None:
                top30_list.append({"stock_ID": stock_id, "volume_ratio": float(row[0])})
        except mysql.connector.Error:
            continue
    sorted_top30 = sorted(top30_list, key=lambda x: -x["volume_ratio"])[:30]
    for i, item in enumerate(sorted_top30):
        item["rank"] = i + 1
    top30_per_day[date] = sorted_top30

# 組成 DataFrame
trend_data = {}
for date in latest_10_dates:
    for entry in top30_per_day[date]:
        stock = entry["stock_ID"]
        rank = entry["rank"]
        if stock not in trend_data:
            trend_data[stock] = {}
        trend_data[stock][date] = rank

df = pd.DataFrame(trend_data).T
df.columns = [pd.to_datetime(col).date() for col in df.columns]
latest_10_dates = [pd.to_datetime(date).date() for date in latest_10_dates]  # 確保型別一致
df = df[latest_10_dates]


# 基準日選擇
st.subheader("📆 選擇基準日")
# 先將日期從舊到新排列
sorted_dates = sorted(latest_10_dates)
# 將按鈕排成每列 5 個
rows = [sorted_dates[i:i + 5] for i in range(0, len(sorted_dates), 5)]
for row in rows:
    cols = st.columns(len(row))
    for idx, date in enumerate(row):
        date_str = date.strftime("%Y-%m-%d")
        if cols[idx].button(f"{date_str}", key=f"date_{date_str}"):
            st.session_state.selected_ref_date = date

st.write(f"✅ 已選擇基準日：**{st.session_state.selected_ref_date.strftime('%Y-%m-%d')}**")

# 股票選擇
filtered_top10 = [entry["stock_ID"] for entry in top30_per_day[st.session_state.selected_ref_date][:10]]
selected_stocks = st.multiselect(
    f"📍 從「{selected_labels}」區間中選擇要顯示的股票：",
    options=df.index.tolist(),
    default=filtered_top10
)

# 畫圖
fig = go.Figure()
x_dates = [d.strftime('%Y-%m-%d') for d in df.columns[::-1]]

for stock in selected_stocks:
    name = stockname(stock)
    capital = get_capital(stock)
    legend_name = f"{stock} {name} ({capital:.1f}萬張)" if capital else f"{stock} {name}"
    ranks = df.loc[stock][::-1]

    # 取得每一天的股價（你需要自己實作這個 function）
    prices = get_all_stock_prices(stock, df.columns[::-1])

        # 畫出活躍度排名趨勢 + 每日對應股價
    fig.add_trace(go.Scatter(
        x=x_dates,
        y=ranks.values,
        mode='lines+markers',
        name=legend_name,
        line=dict(width=2),
        marker=dict(size=6, symbol='circle'),
        hovertemplate=(
            f"📌 {legend_name}<br>"
            "📅 %{x}<br>"
            "🏅 排名：%{y}<br>"
            "💰 股價：%{customdata}元<extra></extra>"
        ),
        customdata=prices
    ))

# 更新佈局設置
fig.update_layout(
    title=dict(text="📈 成交活躍度排名趨勢圖", x=0.5),
    xaxis=dict(type="category", tickangle=-45, categoryarray=x_dates, title="日期"),
    yaxis=dict(autorange="reversed", range=[1, 30], title="排名"),
    plot_bgcolor='white',
    paper_bgcolor='white',
    legend=dict(orientation='h', y=-0.3, x=0.5, xanchor='center'),
    width=1400,
    height=600,
    margin=dict(l=40, r=40, t=80, b=120),
)

st.plotly_chart(fig, use_container_width=True)

# 將選取的股票清單轉成字串格式以便 SQL 查詢
placeholders = ','.join(['%s'] * len(selected_stocks))

# 查出對應的股票名稱
query = f"""
    SELECT stock_ID, stock_name
    FROM stock_id_list
    WHERE stock_ID IN ({placeholders})
"""
cursor = db.cursor()
cursor.execute(query, selected_stocks)

# 建立代號 ➜ 股票名稱的字典
stock_name_dict = {str(stock_id): name for stock_id, name in cursor.fetchall()}

# 產生連結（用名稱顯示，但連到代號的頁面）
links = "｜".join([
    f"[{stock_name_dict.get(stock, stock)}](https://tw.stock.yahoo.com/quote/{stock}.TW/technical-analysis)"
    for stock in selected_stocks
])

# 顯示在 Streamlit 畫面上
st.markdown(f"#### 🔗 股票連結：{links}", unsafe_allow_html=True)


# ===== 新增觀察名單相關 =====
st.subheader("🔍 加入觀察名單")

# 初始化觀察名單
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

# 加入／移除觀察名單邏輯
st.subheader("📌 選擇股票進行觀察")
for stock in selected_stocks:
    name = stockname(stock)
    capital = get_capital(stock)
    label = f"{stock} {name}（{capital:.1f}萬張）" if capital else f"{stock} {name}"

    cols = st.columns([3, 1])
    cols[0].markdown(f"🔎 **{label}**")
    
    if stock not in st.session_state.watchlist:
        if cols[1].button("➕ 加入", key=f"add_{stock}"):
            st.session_state.watchlist.append(stock)
    else:
        if cols[1].button("🗑 移除", key=f"remove_{stock}"):
            st.session_state.watchlist.remove(stock)

# --- Sidebar 顯示觀察名單 ---
with st.sidebar:
    st.markdown("## 👀 觀察名單")
    if not st.session_state.watchlist:
        st.info("尚未加入任何股票")
    else:
        for stock in st.session_state.watchlist:
            name = stockname(stock)
            capital = get_capital(stock)
            st.markdown(
                f"- [{stock} {name}（{capital:.1f}萬張）](https://tw.stock.yahoo.com/quote/{stock}.TW/technical-analysis)"
            )




# 關閉連線
cursor.close()
db.close()