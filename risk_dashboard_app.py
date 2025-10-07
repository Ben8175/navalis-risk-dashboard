# risk_dashboard_app.py
import pandas as pd
import streamlit as st
from datetime import datetime

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Navalis Capital Risk Dashboard", layout="wide")

st.title("⚓ Navalis Capital Risk Dashboard")
st.caption(f"As of {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# --- 2. PARAMETERS ---
TOTAL_CAPITAL = st.number_input("Total Capital (USD)", value=200000.00, step=1000.0)
MAX_DRAWDOWN_PER_TRADE_PCT = 0.02
TIME_STOP_DAYS = 45

# --- 3. USER INPUT DATA ---
st.subheader("📊 Current Open Trades")
st.write("Enter your trades below (you can copy/paste or type directly):")

default_data = [
    {'trade_id': 1, 'spread_name': 'CAPI/PANA Q4', 'entry_date': '2025-09-15', 'size': 8, 'entry_price': 5000, 'current_price': 6562.5, 'profit_target_price': 6800},
    {'trade_id': 2, 'spread_name': 'PANA/SUPRA Q1', 'entry_date': '2025-10-01', 'size': 4, 'entry_price': 3000, 'current_price': 2550, 'profit_target_price': 4000},
    {'trade_id': 3, 'spread_name': 'ROUTE 6 Q4', 'entry_date': '2025-10-05', 'size': 6, 'entry_price': 4000, 'current_price': 3466, 'profit_target_price': 5000},
]

df = st.data_editor(pd.DataFrame(default_data), num_rows="dynamic")

# --- 4. CALCULATIONS ---
df['entry_date'] = pd.to_datetime(df['entry_date'])
df['pnl_per_lot'] = df['current_price'] - df['entry_price']
df['pnl_usd'] = df['pnl_per_lot'] * df['size']
df['pnl_pct'] = (df['pnl_usd'] / (df['entry_price'] * df['size'])) * 100

df['stop_loss_price'] = df['entry_price'] - (df['profit_target_price'] - df['entry_price'])
df['prox_profit_target_pct'] = ((df['current_price'] - df['entry_price']) /
                                (df['profit_target_price'] - df['entry_price'])).clip(0, 1) * 100
df['prox_stop_loss_pct'] = ((df['entry_price'] - df['current_price']) /
                            (df['entry_price'] - df['stop_loss_price'])).clip(0, 1) * 100
df['days_open'] = (pd.Timestamp.now() - df['entry_date']).dt.days
df['prox_time_stop'] = df['days_open'].astype(str) + f" / {TIME_STOP_DAYS} days"

def get_status(prox):
    if prox >= 85:
        return "🔴 High Alert"
    elif prox >= 60:
        return "🟡 Watch"
    else:
        return "🟢 OK"

df['status'] = df['prox_stop_loss_pct'].apply(get_status)

# --- 5. PORTFOLIO METRICS ---
st.subheader("📈 Portfolio Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Total P&L (USD)", f"${df['pnl_usd'].sum():,.2f}")
col2.metric("% of Capital at Risk", f"{((df.loc[df['pnl_usd'] < 0, 'pnl_usd'].sum() / TOTAL_CAPITAL) * -100):.2f}%")
col3.metric("Number of Trades", f"{len(df)}")

# --- 6. TABLE OUTPUT ---
st.subheader("🧮 Position Detail")
styled = df[['spread_name', 'entry_date', 'size', 'pnl_usd', 'pnl_pct', 'status',
             'prox_profit_target_pct', 'prox_stop_loss_pct', 'prox_time_stop']].copy()
styled['entry_date'] = styled['entry_date'].dt.strftime('%Y-%m-%d')
styled['pnl_usd'] = styled['pnl_usd'].map('${:,.2f}'.format)
styled['pnl_pct'] = styled['pnl_pct'].map('{:.2f}%'.format)
styled['prox_profit_target_pct'] = styled['prox_profit_target_pct'].map('{:.0f}%'.format)
styled['prox_stop_loss_pct'] = styled['prox_stop_loss_pct'].map('{:.0f}%'.format)

st.dataframe(styled, use_container_width=True)

# --- 7. EXPORT ---
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📤 Download as CSV", csv, "risk_dashboard.csv", "text/csv")

st.markdown("---")
st.caption("Built with ❤️ by Navalis Capital | Streamlit Dashboard")