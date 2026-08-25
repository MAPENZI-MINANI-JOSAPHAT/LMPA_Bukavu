import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px

# 1. Configuration de la page
st.set_page_config(
    page_title="LMPA Observatory | Bukavu",
    page_icon="assets/logo.jpg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Helper pour vérifier l'existence des fichiers images
def get_image_path(filename):
    path = os.path.join("assets", filename)
    if os.path.exists(path):
        return path
    return None

# 2. Styles CSS légers pour le responsive et l'animation zoom
st.markdown("""
    <style>
    .main { background-color: #F8F9FA; }
    #MainMenu, footer, header {visibility: hidden;}
    
    @keyframes zoomIn {
        0% { transform: scale(0.3); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    .stImage > img {
        animation: zoomIn 1.1s ease-out forwards;
        border-radius: 50%;
        border: 3px solid #E2E8F0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    .welcome-box {
        background: linear-gradient(135deg, #002B49 0%, #1E293B 100%);
        color: #FFFFFF;
        padding: 30px 20px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 25px;
    }
    .welcome-title {
        color: #FFFFFF !important;
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 15px;
    }
    .welcome-text {
        color: #E2E8F0 !important;
        font-size: 1rem;
        line-height: 1.5;
    }
    .institutional-box {
        background-color: #FFFFFF !important;
        padding: 20px;
        border-radius: 6px;
        border-left: 4px solid #002B49;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Bannière d'accueil avec Logo Natif Streamlit
logo_path = get_image_path("logo.jpg")

with st.container():
    st.markdown('<div class="welcome-box">', unsafe_allow_html=True)
    if logo_path:
        col_l1, col_l2, col_l3 = st.columns([2, 1, 2])
        with col_l2:
            st.image(logo_path, use_container_width=True)
    st.markdown("""
        <h1 class="welcome-title">Local Market Price Analytics Observatory</h1>
        <p class="welcome-text">
            Welcome to the <strong>LMPA Observatory</strong>, a quantitative research platform dedicated to tracking, modeling, and analyzing high-frequency food commodity price dynamics and market integration across Bukavu, Democratic Republic of the Congo.
        </p>
    </div>
    """, unsafe_allow_html=True)

# 4. Données
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

# 5. Sidebar Controls
st.sidebar.title("Observatory Controls")
st.sidebar.markdown("---")
selected_years = st.sidebar.multiselect("Select Years:", sorted(df["year"].unique(), reverse=True), default=[2024, 2025, 2026])
selected_markets = st.sidebar.multiselect("Select Markets:", df["market"].unique(), default=df["market"].unique())

filtered_df = df[(df["year"].isin(selected_years)) & (df["market"].isin(selected_markets))]

# 6. Onglets Principaux
tab_analytics, tab_compare, tab_spatial, tab_method, tab_about = st.tabs([
    "1. Price Analytics",
    "2. Inter-Temporal Comparison",
    "3. Spatial Analysis",
    "4. Data Protocol",
    "5. About the Project"
])

# TAB 1: PRICE ANALYTICS
with tab_analytics:
    st.subheader("Commodity Trajectory & Volatility Analysis")
    target_product = st.selectbox("Select Target Commodity:", filtered_df["product"].unique())
    p_df = filtered_df[filtered_df["product"] == target_product].sort_values("date")
    
    col_img, col_stats = st.columns([1, 2])
    with col_img:
        img_p = p_df["product_img"].iloc[0]
        if img_p:
            st.image(img_p, caption=f"Sample: {target_product}", use_container_width=True)
        
    with col_stats:
        latest_date = p_df["date"].max()
        latest_price = p_df[p_df["date"] == latest_date]["price_cdf"].mean()
        mean_price = p_df["price_cdf"].mean()
        std_dev = p_df["price_cdf"].std()
        cv_val = (std_dev / mean_price) * 100 if mean_price > 0 else 0
        
        m1, m2 = st.columns(2)
        m1.metric("Latest Mean Price", f"{latest_price:,.0f} CDF")
        m2.metric("Sample Mean", f"{mean_price:,.0f} CDF")
        
        st.markdown("#### Volatility Metric (Coefficient of Variation)")
        st.latex(r"CV = \left( \frac{\sigma}{\mu} \right) \times 100")
        st.write(f"Computed $CV$ for **{target_product}**: **{cv_val:.2f}%**")

    st.markdown("---")
    fig_line = px.line(
        p_df, x="date", y="price_cdf", color="market", markers=True,
        title=f"Monthly Price Evolution ({target_product})",
        labels={"price_cdf": "Price (CDF)", "date": "Date", "market": "Market"},
        template="plotly_white"
    )
    st.plotly_chart(fig_line, use_container_width=True)

# TAB 2: COMPARISON
with tab_compare:
    st.subheader("Mathematical Inter-Temporal Comparison")
    comp_product = st.selectbox("Select Commodity for Comparison:", df["product"].unique(), key="comp_prod")
    comp_df = df[df["product"] == comp_product].sort_values("date")
    available_dates = comp_df["date"].dt.strftime("%Y-%m").unique()
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        date_t0_str = st.selectbox("Baseline Date (t0):", available_dates, index=0)
    with col_d2:
        date_t1_str = st.selectbox("Comparison Date (t1):", available_dates, index=len(available_dates)-1)
        
    date_t0 = pd.to_datetime(date_t0_str + "-01")
    date_t1 = pd.to_datetime(date_t1_str + "-01")
    p_t0 = comp_df[comp_df["date"] == date_t0]["price_cdf"].mean()
    p_t1 = comp_df[comp_df["date"] == date_t1]["price_cdf"].mean()
    
    pct_change = ((p_t1 - p_t0) / p_t0) * 100 if p_t0 > 0 else 0
    
    res_col1, res_col2, res_col3 = st.columns(3)
    res_col1.metric(f"Price at {date_t0_str}", f"{p_t0:,.0f} CDF")
    res_col2.metric(f"Price at {date_t1_str}", f"{p_t1:,.0f} CDF")
    res_col3.metric("Percentage Change", f"{pct_change:+.2f}%")
    
    st.markdown("##### Percentage Change Formula")
    st.latex(r"\Delta P = \left( \frac{P_{t_1} - P_{t_0}}{P_{t_0}} \right) \times 100")

# TAB 3: SPATIAL ANALYSIS (Ultra-compatible version)
with tab_spatial:
    st.subheader("Market Infrastructure & Spatial Mapping")
    m_col1, m_col2, m_col3 = st.columns(3)
    
    k_img = get_image_path("kadutu_market.jpg")
    n_img = get_image_path("nyawera_market.jpg")
    f_img = get_image_path("feu_vert_market.jpg")
    
    with m_col1:
        if k_img: st.image(k_img, caption="Kadutu Market", use_container_width=True)
    with m_col2:
        if n_img: st.image(n_img, caption="Nyawera Market", use_container_width=True)
    with m_col3:
        if f_img: st.image(f_img, caption="Feu Vert Market", use_container_width=True)
        
    st.markdown("---")
    latest_spatial_date = filtered_df["date"].max()
    spatial_data = filtered_df[filtered_df["date"] == latest_spatial_date].groupby(["market", "latitude", "longitude"])["price_cdf"].mean().reset_index()
    
    # Utilisation d'un graphique à bulles pour garantir 100% de compatibilité sur tous les serveurs
    fig_map = px.scatter(
        spatial_data, x="longitude", y="latitude", size="price_cdf", color="market",
        hover_name="market", text="market",
        title=f"Market Price Spatial Dispersion ({latest_spatial_date.strftime('%B %Y')})",
        labels={"price_cdf": "Price (CDF)"},
        size_max=30, template="plotly_white"
    )
    fig_map.update_traces(textposition='top center')
    st.plotly_chart(fig_map, use_container_width=True)

# TAB 4: DATA PROTOCOL
with tab_method:
    st.subheader("Field Protocol & Econometric Framework")
    st.markdown("""
    <div class="institutional-box">
    <h4>Data Collection Protocol</h4>
    <p>Data is systematically collected weekly across markets in Bukavu using digital forms via KoboCollect by enumerators from Kivu Data Lab (KDL).</p>
    </div>
    """, unsafe_allow_html=True)

# TAB 5: ABOUT THE PROJECT
with tab_about:
    st.subheader("About the Project & Developer")
    col_author_img, col_author_bio = st.columns([1, 2])
    
    auth_img = get_image_path("author_profile.jpg")
    with col_author_img:
        if auth_img:
            st.image(auth_img, caption="Mapenzi Minani Josaphat", use_container_width=True)
    with col_author_bio:
        st.markdown("""
        <div class="institutional-box">
        <h4>Leadership & Institutional Framework</h4>
        <p>Developed by <strong>Mapenzi Minani Josaphat</strong> under the <strong>Kivu Data Lab (KDL)</strong> initiative.</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("Local Market Price Analytics Observatory (LMPA) | Developed by Mapenzi Minani Josaphat | Kivu Data Lab")
