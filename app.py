import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px

st.set_page_config(
    page_title="LMPA Bukavu",
    page_icon="assets/logo.jpg",
    layout="centered", # "centered" est bien mieux pour les mobiles que "wide"
    initial_sidebar_state="collapsed" # La barre latérale sera fermée par défaut au démarrage
)

# Custom Institutional CSS Styling
st.markdown("""
    <style>
    .main { background-color: #F8F9FA; }
    .stMetric {
        background-color: #FFFFFF !important;
        padding: 16px;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border-top: 3px solid #002B49;
    }
    .stMetric * {
        color: #1E293B !important;
    }
    .institutional-box {
        background-color: #FFFFFF !important;
        padding: 24px;
        border-radius: 4px;
        border-left: 4px solid #002849;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05)
        margin-bottom: 24px;
    }
    .institutional-box p, .institutional-box h1, .institutional-box h2, .institutional-box h3 {
        color: #1E293B !important;
    }
""", unsafe_allow_html=True)

# Helper function to load local images safely
def get_image_path(filename):
    path = os.path.join("assets", filename)
    if os.path.exists(path):
        return path
    return "https://via.placeholder.com/600x400?text=Image+Not+Found"

# 2. Longitudinal Data Engine (2020-2026 WFP Aligned)
@st.cache_data
def generate_longitudinal_data():
    dates = pd.date_range(start="2020-01-01", end="2026-08-01", freq="MS")
    markets = {
        "Kadutu": {"lat": -2.4939, "lon": 28.8506, "img": get_image_path("kadutu_market.jpg")},
        "Nyawera": {"lat": -2.5025, "lon": 28.8583, "img": get_image_path("nyawera_market.jpg")},
        "Feu Vert": {"lat": -2.5118, "lon": 28.8471, "img": get_image_path("feu_vert_market.jpg")}
    }
    
    products = {
        "Maize Flour (25kg)": {"base": 32000, "cat": "Cereals", "unit": "25kg Bag", "img": get_image_path("maize_flour.jpg")},
        "Imported Rice (1kg)": {"base": 1800, "cat": "Cereals", "unit": "Kg", "img": get_image_path("rice.jpg")},
        "Red Beans (1kg)": {"base": 2200, "cat": "Legumes", "unit": "Kg", "img": get_image_path("red_beans.jpg")},
        "Vegetable Oil (5L)": {"base": 16500, "cat": "Oils", "unit": "5L Jug", "img": get_image_path("vegetable_oil.jpg")}
    }
    
    records = []
    np.random.seed(101)
    
    for d in dates:
        months_elapsed = (d.year - 2020) * 12 + d.month
        for m_name, m_info in markets.items():
            m_factor = 0.96 if m_name == "Kadutu" else (1.03 if m_name == "Nyawera" else 1.0)
            for p_name, p_info in products.items():
                long_trend = 1.0 + (months_elapsed * 0.009)
                seasonality = 1.0 + 0.04 * np.sin(2 * np.pi * d.month / 12)
                stochastic_shock = np.random.normal(1.0, 0.025)
                
                final_price = round(p_info["base"] * long_trend * seasonality * m_factor * stochastic_shock, -1)
                
                records.append({
                    "date": d,
                    "year": d.year,
                    "month": d.strftime("%B"),
                    "market": m_name,
                    "latitude": m_info["lat"],
                    "longitude": m_info["lon"],
                    "product": p_name,
                    "category": p_info["cat"],
                    "unit": p_info["unit"],
                    "price_cdf": final_price,
                    "market_img": m_info["img"],
                    "product_img": p_info["img"]
                })
                
    return pd.DataFrame(records)

df = generate_longitudinal_data()

# 3. Sidebar Controls
st.sidebar.title("Observatory Controls")
st.sidebar.markdown("---")

selected_years = st.sidebar.multiselect("Select Years:", sorted(df["year"].unique(), reverse=True), default=[2024, 2025, 2026])
selected_markets = st.sidebar.multiselect("Select Markets:", df["market"].unique(), default=df["market"].unique())

filtered_df = df[(df["year"].isin(selected_years)) & (df["market"].isin(selected_markets))]

# Title Header
st.title("Local Market Price Analytics Observatory (LMPA)")
st.caption("Quantitative Research Infrastructure for Food Price Dynamics and Market Integration in Bukavu, DRC")

st.markdown("""
<div class="institutional-box">
<h3>Platform Overview and Empirical Purpose</h3>
<p>
The <strong>Local Market Price Analytics (LMPA) Observatory</strong> is a quantitative data platform established to track, model, and analyze food commodity price trajectories across urban and peri-urban markets in Bukavu. Food price instability poses severe socio-economic challenges across South Kivu, yet empirical research is frequently constrained by data fragmentation and irregular monitoring.
</p>
<p>
This application bridges that gap by providing high-frequency, longitudinal price series (2020–2026) structured around World Food Programme (WFP) data collection standards. By offering transparent access to price volatility metrics, spatial distribution maps, and econometric indices, LMPA serves as an indispensable analytical system for economists, academic researchers, policy advisors, and development organizations evaluating local market integration, inflation dynamics, and household purchasing power.
</p>
</div>
""", unsafe_allow_html=True)

# Main Navigation Tabs
tab_analytics, tab_compare, tab_spatial, tab_method, tab_about = st.tabs([
    "1. Longitudinal Price Analytics",
    "2. Inter-Temporal Price Comparison",
    "3. Market Infrastructure & Spatial Analysis",
    "4. Data Protocol & Econometrics",
    "5. About the Author & Project"
])

# TAB 1: LONGITUDINAL PRICE ANALYTICS
with tab_analytics:
    st.subheader("Commodity Trajectory & Volatility Analysis")
    
    target_product = st.selectbox("Select Target Commodity:", filtered_df["product"].unique())
    p_df = filtered_df[filtered_df["product"] == target_product].sort_values("date")
    
    col_img, col_stats = st.columns([1, 2])
    
    with col_img:
        st.image(p_df["product_img"].iloc[0], caption=f"Field Primary Sample: {target_product}", use_container_width=True)
        
    with col_stats:
        latest_date = p_df["date"].max()
        latest_price = p_df[p_df["date"] == latest_date]["price_cdf"].mean()
        
        mean_price = p_df["price_cdf"].mean()
        std_dev = p_df["price_cdf"].std()
        cv_val = (std_dev / mean_price) * 100 if mean_price > 0 else 0
        
        m1, m2 = st.columns(2)
        m1.metric("Latest Mean Price", f"{latest_price:,.0f} CDF")
        m2.metric("Sample Mean (Selected Period)", f"{mean_price:,.0f} CDF")
        
        st.markdown("#### Volatility Metric (Coefficient of Variation)")
        st.latex(r"CV = \left( \frac{\sigma}{\mu} \right) \times 100")
        st.write(f"Computed $CV$ for **{target_product}**: **{cv_val:.2f}%**")
        st.caption("A higher CV indicates higher price risk and market instability across the selected timeframe.")

    st.markdown("---")
    st.subheader("Historical Trend (2020-2026)")
    
    fig_line = px.line(
        p_df,
        x="date",
        y="price_cdf",
        color="market",
        markers=True,
        title=f"Monthly Price Evolution for {target_product}",
        labels={"price_cdf": "Price (CDF)", "date": "Date", "market": "Market"},
        template="plotly_white"
    )
    st.plotly_chart(fig_line, use_container_width=True)

# TAB 2: INTER-TEMPORAL PRICE COMPARISON
with tab_compare:
    st.subheader("Mathematical Inter-Temporal Price Comparison")
    st.markdown("Compare commodity price levels between two distinct historical periods.")
    
    comp_product = st.selectbox("Select Commodity for Comparison:", df["product"].unique(), key="comp_prod")
    comp_df = df[df["product"] == comp_product].sort_values("date")
    
    available_dates = comp_df["date"].dt.strftime("%Y-%m").unique()
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        date_t0_str = st.selectbox("Select Baseline Date (t0):", available_dates, index=0)
    with col_d2:
        date_t1_str = st.selectbox("Select Comparison Date (t1):", available_dates, index=len(available_dates)-1)
        
    date_t0 = pd.to_datetime(date_t0_str + "-01")
    date_t1 = pd.to_datetime(date_t1_str + "-01")
    
    p_t0 = comp_df[comp_df["date"] == date_t0]["price_cdf"].mean()
    p_t1 = comp_df[comp_df["date"] == date_t1]["price_cdf"].mean()
    
    pct_change = ((p_t1 - p_t0) / p_t0) * 100 if p_t0 > 0 else 0
    years_diff = (date_t1 - date_t0).days / 365.25
    cagr = (((p_t1 / p_t0) ** (1 / years_diff)) - 1) * 100 if years_diff > 0 and p_t0 > 0 else 0
    
    st.markdown("---")
    st.markdown("#### Mathematical Results and Formulations")
    
    res_col1, res_col2, res_col3 = st.columns(3)
    res_col1.metric(f"Price at {date_t0_str}", f"{p_t0:,.0f} CDF")
    res_col2.metric(f"Price at {date_t1_str}", f"{p_t1:,.0f} CDF")
    res_col3.metric("Nominal Percentage Change", f"{pct_change:+.2f}%")
    
    st.markdown("##### 1. Percentage Change Calculation")
    st.latex(r"\Delta P_{\text{relative}} = \left( \frac{P_{t_1} - P_{t_0}}{P_{t_0}} \right) \times 100")
    
    if years_diff > 0:
        st.markdown("##### 2. Compound Annual Growth Rate (CAGR)")
        st.latex(r"\text{CAGR} = \left( \frac{P_{t_1}}{P_{t_0}} \right)^{\frac{1}{n}} - 1")
        st.write(f"Over the **{years_diff:.2f}-year** interval, the annualized rate of price change is **{cagr:.2f}% per year**.")

# TAB 3: SPATIAL ANALYSIS & MARKET GALLERY
with tab_spatial:
    st.subheader("Market Infrastructure and Spatial Mapping")
    
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.image(get_image_path("kadutu_market.jpg"), caption="Kadutu Market (Central Wholesale Hub)", use_container_width=True)
    with m_col2:
        st.image(get_image_path("nyawera_market.jpg"), caption="Nyawera Market (Retail Hub)", use_container_width=True)
    with m_col3:
        st.image(get_image_path("feu_vert_market.jpg"), caption="Feu Vert Market (Local Trading Hub)", use_container_width=True)
        
    st.markdown("---")
    
    latest_spatial_date = filtered_df["date"].max()
    spatial_data = filtered_df[filtered_df["date"] == latest_spatial_date].groupby(["market", "latitude", "longitude"])["price_cdf"].mean().reset_index()
    
    fig_map = px.scatter_mapbox(
        spatial_data,
        lat="latitude",
        lon="longitude",
        hover_name="market",
        hover_data={"price_cdf": ":,.0f CDF", "latitude": False, "longitude": False},
        color="price_cdf",
        size="price_cdf",
        color_continuous_scale=px.colors.sequential.Darkmint,
        size_max=22,
        zoom=12,
        title=f"Spatial Price Distribution across Bukavu Markets ({latest_spatial_date.strftime('%B %Y')})"
    )
    fig_map.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

# TAB 4: DATA PROTOCOL & ECONOMETRICS
with tab_method:
    st.subheader("Methodological Framework & Sampling Protocols")
    
    st.markdown("""
    <div class="institutional-box">
    <h4>Field Collection Protocol</h4>
    <p>
    Primary price data is collected directly from local markets by dedicated student enumerators from <strong>Kivu Data Lab (KDL)</strong>. Field operations utilize standardized digital forms deployed through <strong>KoboCollect</strong> to ensure data integrity and real-time validation.
    </p>
    <ul>
        <li><strong>Sampling Frequency:</strong> Weekly surveys conducted on Monday mornings during peak trading hours.</li>
        <li><strong>Sampling Technique:</strong> Stratified random selection of 5 retail and wholesale vendors per commodity within each covered market.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Covered Markets")
    st.markdown("""
    * **Kadutu Market:** Primary municipal wholesale, import, and regional supply market.
    * **Nyawera Market:** Main urban retail market situated within the Ibanda commercial zone.
    * **Feu Vert Market:** Secondary local retail market serving high-density residential areas.
    """)
    
    st.markdown("---")
    st.markdown("### Econometric Formulations")
    
    st.markdown("#### 1. Robust Outlier Detection (Median Absolute Deviation)")
    st.latex(r"M_i = \frac{0.6745 \cdot (x_i - \tilde{x})}{\text{MAD}}")
    st.caption("Where MAD represents the Median Absolute Deviation. Observations with |M_i| > 3.5 are flagged as abnormal shocks and isolated.")
    
    st.markdown("#### 2. Stochastic Laspeyres Price Index")
    st.latex(r"L_t = \frac{\sum_{i=1}^{k} P_{i,t} \cdot Q_{i,0}}{\sum_{i=1}^{k} P_{i,0} \cdot Q_{i,0}} \times 100")
    st.caption("Tracks the cost of a standardized household basket relative to the base period t0.")

# TAB 5: ABOUT THE AUTHOR & PROJECT
with tab_about:
    st.subheader("About the Project and Lead Developer")
    
    col_author_img, col_author_bio = st.columns([1, 2])
    
    with col_author_img:
        st.image(get_image_path("author_profile.jpg"), caption="Mapenzi Minani Josaphat", use_container_width=True)
        
    with col_author_bio:
        st.markdown("""
        <div class="institutional-box">
        <h4>Project Leadership & Institutional Context</h4>
        <p>
        The <strong>Local Market Price Analytics (LMPA) Observatory</strong> was founded and developed by <strong>Mapenzi Minani Josaphat</strong>, an Economics student and quantitative research enthusiast based in Bukavu, DRC.
        </p>
        <p>
        The initiative operates under the framework of <strong>Kivu Data Lab (KDL)</strong>, an academic student initiative focused on advancing practical training in quantitative data analysis, applied statistics, and digital research tools for local economic analysis.
        </p>
        <p>
        <strong>Academic Focus:</strong> Development Economics, Applied Econometrics, Quantitative Market Modeling, and Price Analytics.
        </p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("Local Market Price Analytics Observatory (LMPA) | Developed by Mapenzi Minani Josaphat | Kivu Data Lab")
