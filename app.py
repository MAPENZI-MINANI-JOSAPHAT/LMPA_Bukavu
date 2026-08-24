import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px

# 1. Configuration de la page
st.set_page_config(
    page_title="LMPA Bukavu",
    page_icon="assets/logo.jpg",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 2. Styles CSS personnalisés et masquage des éléments Streamlit
st.markdown("""
    <style>
    /* Masquer le menu hamburger, le pied de page et l'en-tête Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Style global */
    .main { background-color: #F8F9FA; }
    
    /* Cartes de métriques */
    .stMetric {
        background-color: #FFFFFF !important;
        padding: 16px;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border-top: 3px solid #002B49;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Contenu principal de l'application
st.title("LMPA Bukavu")
st.write("Bienvenue sur l'application de suivi des prix du marché à Bukavu.")
 
 
