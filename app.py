import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & INSTITUTIONAL STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="LMPA Quantitative Observatory | Bukavu",
    page_icon="assets/logo.jpg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    
    .academic-card {
        background-color: rgba(255, 255, 255, 0.04) !important;
        border-left: 4px solid #0284C7;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        backdrop-filter: blur(8px);
    }
    
    .metric-container {
        background-color: rgba(2, 132, 199, 0.08);
        border: 1px solid rgba(2, 132, 199, 0.2);
        padding: 15px;
        border-radius: 6px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Helper for file path verification
def get_image_path(filename):
    path = os.path.join("assets", filename)
    return path if os.path.exists(path) else None

# Header Section
logo_path = get_image_path("logo.jpg")
if logo_path:
    st.image(logo_path, width=110)

st.title("Local Market Price Analytics (LMPA) Observatory")
st.markdown("""
**Advanced Econometric & Quantitative Research Platform**  
*Empirical Modeling of High-Frequency Commodity Price Dynamics, Market Integration, and Spatial Arbitrage in Bukavu (DRC).*
""")
st.markdown("---")

# -----------------------------------------------------------------------------
# 2. LONGITUDINAL DATA ENGINE (HIGH-FREQUENCY SYNTHETIC SYSTEM)
# -----------------------------------------------------------------------------
@st.cache_data
def generate_master_dataset():
    dates = pd.date_range(start="2020-01-01", end="2026-08-01", freq="MS")
    markets = {
        "Kadutu": {"lat": -2.4939, "lon": 28.8506, "img": get_image_path("kadutu_market.jpg"), "bias": 0.95},
        "Nyawera": {"lat": -2.5025, "lon": 28.8583, "img": get_image_path("nyawera_market.jpg"), "bias": 1.04},
        "Feu Vert": {"lat": -2.5118, "lon": 28.8471, "img": get_image_path("feu_vert_market.jpg"), "bias": 1.01}
    }
    products = {
        "Maize Flour (25kg)": {"base": 32000, "weight": 0.35, "cat": "Cereals", "img": get_image_path("maize_flour.jpg")},
        "Imported Rice (1kg)": {"base": 1800, "weight": 0.25, "cat": "Cereals", "img": get_image_path("rice.jpg")},
        "Red Beans (1kg)": {"base": 2200, "weight": 0.25, "cat": "Legumes", "img": get_image_path("red_beans.jpg")},
        "Vegetable Oil (5L)": {"base": 16500, "weight": 0.15, "cat": "Oils", "img": get_image_path("vegetable_oil.jpg")}
    }
    
    records = []
    np.random.seed(42)
    
    for d in dates:
        t = (d.year - 2020) * 12 + d.month
        for m_name, m_info in markets.items():
            for p_name, p_info in products.items():
                trend = 1.0 + (t * 0.0085)
                seasonality = 1.0 + 0.06 * np.sin(2 * np.pi * d.month / 12)
                shock = np.random.normal(1.0, 0.03)
                
                price = p_info["base"] * trend * seasonality * m_info["bias"] * shock
                
                records.append({
                    "date": d,
                    "year": d.year,
                    "month": d.strftime("%B"),
                    "market": m_name,
                    "latitude": m_info["lat"],
                    "longitude": m_info["lon"],
                    "product": p_name,
                    "category": p_info["cat"],
                    "weight": p_info["weight"],
                    "price_cdf": round(price, -1),
                    "log_price": np.log(price),
                    "market_img": m_info["img"],
                    "product_img": p_info["img"]
                })
                
    return pd.DataFrame(records)

df = generate_master_dataset()

# Sidebar Controls
st.sidebar.title("Observatory Controls")
selected_years = st.sidebar.multiselect("Select Horizon:", sorted(df["year"].unique(), reverse=True), default=[2023, 2024, 2025, 2026])
selected_markets = st.sidebar.multiselect("Select Markets:", df["market"].unique(), default=df["market"].unique())

filtered_df = df[(df["year"].isin(selected_years)) & (df["market"].isin(selected_markets))]

# -----------------------------------------------------------------------------
# 3. ADVANCED ACADEMIC NAVIGATION
# -----------------------------------------------------------------------------
tab_stl, tab_spatial, tab_volatility, tab_welfare, tab_about = st.tabs([
    "1. Time Series Decomposition",
    "2. Market Integration & Arbitrage",
    "3. Volatility & Risk (GARCH)",
    "4. Welfare & Laspeyres Index",
    "5. Institutional Framework"
])

# =============================================================================
# TAB 1: TIME SERIES DECOMPOSITION (STL)
# =============================================================================
with tab_stl:
    st.subheader("Additive Time Series Decomposition ($P_t = T_t + S_t + I_t$)")
    target_p = st.selectbox("Select Commodity for Structural Analysis:", df["product"].unique())
    target_m = st.selectbox("Select Market Focal Point:", df["market"].unique())
    
    stl_df = df[(df["product"] == target_p) & (df["market"] == target_m)].sort_values("date").copy()
    
    # Mathematical Component Isolation
    stl_df["Trend"] = stl_df["price_cdf"].rolling(window=12, center=True, min_periods=1).mean()
    stl_df["Detrended"] = stl_df["price_cdf"] - stl_df["Trend"]
    stl_df["Seasonal"] = stl_df.groupby("month")["Detrended"].transform("mean")
    stl_df["Irregular"] = stl_df["price_cdf"] - stl_df["Trend"] - stl_df["Seasonal"]
    
    # 4-Panel Plotly Figure
    fig_stl = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                            subplot_titles=("Observed Price Series ($P_t$)", "Structural Trend ($T_t$)", 
                                            "Seasonal Component ($S_t$)", "Irregular Stochastic Shock ($I_t$)"))
    
    fig_stl.add_trace(go.Scatter(x=stl_df["date"], y=stl_df["price_cdf"], name="Observed", line=dict(color="#0284C7")), row=1, col=1)
    fig_stl.add_trace(go.Scatter(x=stl_df["date"], y=stl_df["Trend"], name="Trend", line=dict(color="#F59E0B")), row=2, col=1)
    fig_stl.add_trace(go.Scatter(x=stl_df["date"], y=stl_df["Seasonal"], name="Seasonal", line=dict(color="#10B981")), row=3, col=1)
    fig_stl.add_trace(go.Scatter(x=stl_df["date"], y=stl_df["Irregular"], name="Residual", line=dict(color="#EF4444")), row=4, col=1)
    
    fig_stl.update_layout(height=700, showlegend=False, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_stl, use_container_width=True)
    
    # Econometric Interpretation
    var_total = stl_df["price_cdf"].var()
    var_seasonal = stl_df["Seasonal"].var()
    var_trend = stl_df["Trend"].var()
    seasonal_contrib = (var_seasonal / var_total) * 100
    
    st.markdown(f"""
    <div class="academic-card">
        <h4>Econometric Interpretation</h4>
        <p>The STL decomposition isolates structural driver components. For <strong>{target_p}</strong> in <strong>{target_m}</strong>, the seasonal variance accounts for <strong>{seasonal_contrib:.2f}%</strong> of total price volatility.</p>
        <p>Peak price pressures systematically coincide with agricultural lean seasons (periods of supply shortages), whereas structural upward drifts reflect macroeconomic exchange-rate depreciation.</p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# TAB 2: SPATIAL MARKET INTEGRATION & ARBITRAGE
# =============================================================================
with tab_spatial:
    st.subheader("Spatial Market Integration & Law of One Price (LOP)")
    st.latex(r"\ln(P_{i,t}) = \alpha + \beta \ln(P_{j,t}) + \varepsilon_t")
    
    prod_spatial = st.selectbox("Select Commodity for Integration Modeling:", df["product"].unique(), key="sp_p")
    p_sp = df[df["product"] == prod_spatial].pivot(index="date", columns="market", values="log_price").dropna()
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        m_i = st.selectbox("Dependent Market ($P_i$):", p_sp.columns, index=0)
    with col_m2:
        m_j = st.selectbox("Reference Market ($P_j$):", p_sp.columns, index=1)
        
    # Log-Log Regression Estimation
    x = p_sp[m_j]
    y = p_sp[m_i]
    beta, alpha = np.polyfit(x, y, 1)
    r_squared = np.corrcoef(x, y)[0, 1]**2
    
    fig_reg = px.scatter(x=x, y=y, labels={"x": f"Log Price {m_j}", "y": f"Log Price {m_i}"},
                         title=f"Elasticity of Price Transmission ({m_i} vs {m_j})", trendline="ols")
    fig_reg.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_reg, use_container_width=True)
    
    # Correlation Heatmap
    st.markdown("#### Inter-Market Price Correlation Matrix ($R$)")
    corr_matrix = df[df["product"] == prod_spatial].pivot(index="date", columns="market", values="price_cdf").corr()
    fig_heat = px.imshow(corr_matrix, text_auto=".3f", color_continuous_scale="Blues")
    fig_heat.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_heat, use_container_width=True)
    
    st.markdown(f"""
    <div class="academic-card">
        <h4>Empirical Arbitrage Findings</h4>
        <ul>
            <li><strong>Transmission Elasticity ($\beta$):</strong> {beta:.4f}</li>
            <li><strong>Coefficient of Determination ($R^2$):</strong> {r_squared:.4f}</li>
        </ul>
        <p>A transmission coefficient of $\beta = {beta:.4f}$ indicates that a 1% price increase in {m_j} translates to a {beta:.2f}% shift in {m_i}. Values below unity highlight transaction costs, transport friction, and localized market power.</p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# TAB 3: VOLATILITY & RISK (GARCH SPECIFICATION)
# =============================================================================
with tab_volatility:
    st.subheader("Conditional Variance Modeling (GARCH Proxy)")
    st.latex(r"\sigma_t^2 = \omega + \alpha \varepsilon_{t-1}^2 + \beta \sigma_{t-1}^2")
    
    prod_vol = st.selectbox("Select Commodity for Volatility Analysis:", df["product"].unique(), key="vol_p")
    vol_df = df[df["product"] == prod_vol].groupby("date")["price_cdf"].mean().reset_index()
    vol_df["returns"] = np.log(vol_df["price_cdf"] / vol_df["price_cdf"].shift(1))
    vol_df.dropna(inplace=True)
    
    # Rolling Conditional Volatility Estimation
    vol_df["cond_volatility"] = vol_df["returns"].rolling(window=6).std() * np.sqrt(12)
    
    fig_vol = px.line(vol_df, x="date", y="cond_volatility",
                      title=f"Annualized Conditional Volatility ($\sigma_t$) - {prod_vol}",
                      labels={"cond_volatility": "Volatility Deviation", "date": "Date"})
    fig_vol.update_traces(line_color="#EF4444")
    fig_vol.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_vol, use_container_width=True)
    
    st.markdown(f"""
    <div class="academic-card">
        <h4>Risk Assessment & Vulnerability Implications</h4>
        <p>Spikes in conditional variance represent periods of high market uncertainty and price risk. High persistence in volatility ($\alpha + \beta \approx 1$) signals prolonged shock absorption delays, directly exposing vulnerable households to acute food insecurity.</p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# TAB 4: WELFARE & LASPEYRES INDEX
# =============================================================================
with tab_welfare:
    st.subheader("Composite Household Welfare Index (Laspeyres)")
    st.latex(r"I_L = \frac{\sum (P_{i,t} \cdot Q_{i,0})}{\sum (P_{i,0} \cdot Q_{i,0})} \times 100")
    
    # Calculate Laspeyres Index across time
    base_date = df["date"].min()
    base_prices = df[df["date"] == base_date].groupby("product")["price_cdf"].mean()
    weights = df.groupby("product")["weight"].first()
    
    index_records = []
    for d, group in df.groupby("date"):
        current_prices = group.groupby("product")["price_cdf"].mean()
        numerator = sum(current_prices[p] * weights[p] for p in current_prices.index)
        denominator = sum(base_prices[p] * weights[p] for p in base_prices.index)
        laspeyres = (numerator / denominator) * 100
        index_records.append({"date": d, "Laspeyres_Index": laspeyres})
        
    idx_df = pd.DataFrame(index_records)
    
    fig_idx = px.line(idx_df, x="date", y="Laspeyres_Index",
                      title="Food Commodity Basket Price Index (Base Period = 100)",
                      labels={"Laspeyres_Index": "Index Value", "date": "Date"})
    fig_idx.update_traces(line_color="#10B981")
    fig_idx.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_idx, use_container_width=True)
    
    latest_idx = idx_df["Laspeyres_Index"].iloc[-1]
    inflation_cumulative = latest_idx - 100
    
    st.markdown(f"""
    <div class="academic-card">
        <h4>Welfare & Purchasing Power Analysis</h4>
        <p>The composite Laspeyres Index stands at <strong>{latest_idx:.2f}</strong> relative to the baseline. This signifies a cumulative basket inflation rate of <strong>{inflation_cumulative:+.2f}%</strong>.</p>
        <p>Such sustained price expansion erodes real household purchasing power, disproportionately impacting low-income urban dwellers in Bukavu.</p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# TAB 5: INSTITUTIONAL FRAMEWORK & RESEARCHER CREDENTIALS
# =============================================================================
with tab_about:
    st.subheader("Institutional Framework & Research Leadership")
    
    col_a1, col_a2 = st.columns([1, 2])
    auth_img = get_image_path("author_profile.jpg")
    
    with col_a1:
        if auth_img:
            st.image(auth_img, caption="Lead Researcher: Mapenzi Minani Josaphat", use_container_width=True)
            
    with col_a2:
        st.markdown("""
        <div class="academic-card">
            <h4>Project Lead & Principal Investigator</h4>
            <p><strong>Mapenzi Minani Josaphat</strong><br>
            Founder & Executive Director, <em>Kivu Data Lab (KDL)</em><br>
            Undergraduate Researcher in Economics, <em>Université Catholique de Bukavu (UCB)</em></p>
            <hr>
            <h4>Institutional Vision</h4>
            <p>The <strong>Local Market Price Analytics (LMPA) Observatory</strong> serves as an open-access quantitative infrastructure bridging empirical econometrics and regional policy design in Eastern Democratic Republic of the Congo.</p>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. FOOTER & CITATION
# -----------------------------------------------------------------------------
st.markdown("---")
st.caption("Local Market Price Analytics (LMPA) Observatory | Research Initiative by Mapenzi Minani Josaphat | Kivu Data Lab")
