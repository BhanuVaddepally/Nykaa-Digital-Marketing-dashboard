import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import textwrap
import os
import json
import re
import urllib.request
import urllib.error
import hashlib
import html
import importlib.util
from io import StringIO, BytesIO
from string import Template
from plotly.subplots import make_subplots
import streamlit.components.v1 as components

st.set_page_config(page_title="Nykaa AI BI Dashboard", layout="wide")

# -------------------------
# THEME TOGGLE
# -------------------------

if "theme" not in st.session_state:
    st.session_state.theme = "dark"


def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"


top_left, top_right = st.columns([3.5, 1])
with top_left:
    st.markdown('<div class="top-line">Nykaa Digital Marketing Intelligence • Live Overview</div>', unsafe_allow_html=True)
with top_right:
    theme_icon = "☀" if st.session_state.theme == "dark" else "☾"
    st.button(theme_icon, key="theme_toggle", help="Toggle theme", on_click=toggle_theme)

theme = st.session_state.theme

if theme == "light":
    bg = "#F5F7FB"
    panel = "rgba(255, 255, 255, 0.82)"
    panel_strong = "rgba(255, 255, 255, 0.95)"
    panel_border = "rgba(108, 60, 240, 0.22)"
    text = "#0f172a"
    muted = "#5b6476"
    glow = "rgba(108, 60, 240, 0.2)"
    particle_1 = "rgba(108, 60, 240, 0.55)"
    particle_2 = "rgba(0, 194, 255, 0.5)"
    particle_3 = "rgba(255, 122, 89, 0.45)"
    particle_4 = "rgba(15, 23, 42, 0.25)"
    plotly_template = "plotly_white"
    hover_bg = "#F1F5F9"
else:
    bg = "#020617"
    panel = "rgba(10, 15, 35, 0.68)"
    panel_strong = "rgba(10, 15, 35, 0.82)"
    panel_border = "rgba(108, 60, 240, 0.28)"
    text = "#E6E7EA"
    muted = "#AAB3C6"
    glow = "rgba(0, 194, 255, 0.35)"
    particle_1 = "rgba(108, 60, 240, 0.6)"
    particle_2 = "rgba(0, 194, 255, 0.55)"
    particle_3 = "rgba(255, 122, 89, 0.5)"
    particle_4 = "rgba(230, 231, 234, 0.55)"
    plotly_template = "plotly_dark"
    hover_bg = "#0f172a"

plotly_colors = ["#6C3CF0", "#00C2FF", "#FF7A59", "#8B7BFF", "#2DD4BF"]

# -------------------------
# GLOBAL STYLES
# -------------------------

css = Template(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Manrope:wght@300;400;500;600;700&display=swap');

:root {
  --bg: $bg;
  --panel: $panel;
  --panel-strong: $panel_strong;
  --panel-border: $panel_border;
  --primary: #6C3CF0;
  --secondary: #00C2FF;
  --accent: #FF7A59;
  --text: $text;
  --muted: $muted;
  --glow: $glow;
  --particle-1: $particle_1;
  --particle-2: $particle_2;
  --particle-3: $particle_3;
  --particle-4: $particle_4;
  --control-height: 52px;
}

html, body {
  background: var(--bg);
  color: var(--text);
  font-family: 'Manrope', sans-serif;
}

html {
  scroll-behavior: smooth;
}

* {
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

/* Keep Plotly hover labels synced (avoid global transitions affecting SVG transforms). */
.js-plotly-plot .hoverlayer,
.js-plotly-plot .hoverlayer * {
  transition: none !important;
}

[data-testid="stAppViewContainer"] {
  background: transparent;
  position: relative;
  z-index: 1;
}

[data-testid="stAppViewContainer"]::before {
  content: "";
  position: fixed;
  inset: 0;
  background:
    radial-gradient(circle at 12% 20%, rgba(108, 60, 240, 0.16), transparent 35%),
    radial-gradient(circle at 86% 12%, rgba(0, 194, 255, 0.12), transparent 32%),
    radial-gradient(circle at 40% 85%, rgba(255, 122, 89, 0.12), transparent 38%),
    linear-gradient(120deg, rgba(255, 255, 255, 0.04) 0%, rgba(255, 255, 255, 0) 60%);
  pointer-events: none;
  z-index: 0;
  opacity: 0.7;
}

.stApp {
  background: transparent;
  position: relative;
  z-index: 1;
}

main .block-container {
  max-width: 1200px;
  padding-top: 2.2rem;
  padding-bottom: 0;
}

h1, h2, h3, h4 {
  font-family: 'Space Grotesk', sans-serif;
  color: var(--text);
  letter-spacing: 0.02em;
}

.top-line {
  font-size: 0.85rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 0.5rem;
}

.section-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.6rem 1.2rem;
  border-radius: 16px;
  background: var(--panel);
  border: 1px solid var(--panel-border);
  box-shadow: 0 16px 32px rgba(2, 6, 23, 0.5);
  margin-bottom: 1.4rem;
}

.section-nav-title {
  font-weight: 700;
  font-size: 0.95rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text);
}

.section-nav-links {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.section-link {
  font-size: 0.82rem;
  color: var(--muted);
  text-decoration: none;
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
  transition: color 0.2s ease, background 0.2s ease;
  border: 1px solid transparent;
}

.section-link,
.section-link:link,
.section-link:visited,
.section-link:hover,
.section-link:active,
.section-link:focus {
  text-decoration: none !important;
  border-bottom: none !important;
}

.section-link:hover {
  color: var(--text);
  background: rgba(0, 194, 255, 0.12);
  border-color: rgba(0, 194, 255, 0.3);
}

.nav-toast {
  position: fixed;
  top: 1.1rem;
  right: 1.4rem;
  z-index: 9999;
  background: linear-gradient(135deg, rgba(255, 122, 89, 0.92), rgba(108, 60, 240, 0.88));
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.35);
  border-radius: 12px;
  padding: 0.75rem 1.05rem;
  font-size: 0.82rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  box-shadow: 0 16px 34px rgba(2, 6, 23, 0.45), 0 0 24px rgba(255, 122, 89, 0.35);
  backdrop-filter: blur(6px);
  opacity: 0;
  transform: translateY(-8px);
  pointer-events: none;
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.nav-toast.show {
  opacity: 1;
  transform: translateY(0);
  animation: navToastPop 0.2s ease-out, navToastPulse 1.1s ease-in-out 0.35s 2;
}

.scroll-progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  width: 0%;
  z-index: 10000;
  background: linear-gradient(90deg, var(--secondary), var(--primary), var(--accent));
  box-shadow: 0 6px 14px rgba(0, 194, 255, 0.25);
  transition: width 0.12s ease;
  pointer-events: none;
}

@keyframes navToastPop {
  0% { transform: translateY(-12px) scale(0.98); }
  100% { transform: translateY(0) scale(1); }
}

@keyframes navToastPulse {
  0% { box-shadow: 0 16px 34px rgba(2, 6, 23, 0.45), 0 0 16px rgba(255, 122, 89, 0.35); }
  50% { box-shadow: 0 18px 38px rgba(2, 6, 23, 0.5), 0 0 28px rgba(255, 122, 89, 0.6); }
  100% { box-shadow: 0 16px 34px rgba(2, 6, 23, 0.45), 0 0 16px rgba(255, 122, 89, 0.35); }
}

label, .stCaption, .stTextInput label, .stSelectbox label, .stRadio label, .stCheckbox label, .stToggle label {
  color: var(--muted);
}

div[data-testid="stToggle"] {
  background: var(--panel);
  border: 1px solid var(--panel-border);
  border-radius: 999px;
  padding: 0.2rem 0.8rem;
  box-shadow: 0 10px 24px rgba(2, 6, 23, 0.25);
}

div[data-testid="stToggle"] label {
  color: var(--muted);
  font-size: 0.85rem;
}

.gradient-title {
  font-size: clamp(2.2rem, 3vw, 3.2rem);
  font-weight: 700;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  margin-bottom: 0.4rem;
}

.hero {
  padding: 1.6rem 1.8rem;
  border-radius: 22px;
  background: linear-gradient(135deg, rgba(108, 60, 240, 0.2), rgba(0, 194, 255, 0.08));
  border: 1px solid rgba(108, 60, 240, 0.3);
  border-left: 4px solid var(--secondary);
  box-shadow: 0 18px 40px rgba(2, 6, 23, 0.6);
  backdrop-filter: blur(10px);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.hero:hover {
  transform: translateY(-4px);
  box-shadow: 0 26px 60px rgba(2, 6, 23, 0.7), 0 0 30px rgba(108, 60, 240, 0.18);
}

.reveal-target {
  opacity: 0;
  transform: translateY(18px) scale(0.99);
  filter: blur(3px);
  transition: opacity 0.8s ease, transform 0.8s ease, filter 0.8s ease;
  will-change: opacity, transform, filter;
}

.reveal-visible {
  opacity: 1;
  transform: translateY(0) scale(1);
  filter: blur(0);
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.8rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--secondary);
  background: rgba(0, 194, 255, 0.15);
  border: 1px solid rgba(0, 194, 255, 0.35);
  margin-bottom: 0.8rem;
}

.hero-subtitle {
  font-size: 1.1rem;
  color: var(--muted);
  margin-bottom: 0.6rem;
}

.hero-meta {
  font-size: 0.95rem;
  color: var(--muted);
}

.section-title {
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: var(--muted);
  margin: 1.4rem 0 0.8rem 0;
  font-weight: 600;
}

.chart-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--secondary);
  border: 1px solid rgba(0, 194, 255, 0.4);
  background: rgba(0, 194, 255, 0.12);
  margin-bottom: 0.6rem;
}

.glass-card {
  background: var(--panel);
  border: 1px solid var(--panel-border);
  border-radius: 18px;
  box-shadow: 0 20px 40px rgba(2, 6, 23, 0.65);
  backdrop-filter: blur(14px);
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}

.glass-card:hover {
  transform: translateY(-6px) scale(1.01);
  border-color: rgba(0, 194, 255, 0.55);
  box-shadow: 0 30px 70px rgba(2, 6, 23, 0.8), 0 0 40px rgba(0, 194, 255, 0.15);
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.2rem;
}

.kpi-card {
  padding: 1.4rem 1.5rem;
  position: relative;
  overflow: hidden;
}

.kpi-card::after {
  content: "";
  position: absolute;
  inset: -40% 0 auto 0;
  height: 140%;
  background: radial-gradient(circle at top, rgba(108, 60, 240, 0.35), transparent 60%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.kpi-card:hover::after {
  opacity: 1;
}

.kpi-label {
  font-size: 0.85rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.14em;
  margin-bottom: 0.6rem;
}

.kpi-value {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 2rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 0.4rem;
}

.kpi-foot {
  font-size: 0.85rem;
  color: var(--muted);
}

.upload-card {
  padding: 1.4rem 1.4rem 0.8rem 1.4rem;
}

.upload-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.6rem;
}

div[data-testid="stFileUploader"] {
  background: transparent;
  border: 1px dashed rgba(108, 60, 240, 0.45);
  border-radius: 14px;
  padding: 0.8rem 0.8rem 0.4rem 0.8rem;
}

div[data-testid="stFileUploader"] section {
  color: var(--muted);
  font-size: 0.85rem;
}

div[data-testid="stFileUploader"] button {
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: #fff;
  border: none;
  border-radius: 10px;
}

div[data-testid="stTextInput"] input {
  background: var(--panel-strong);
  border: 1px solid rgba(108, 60, 240, 0.35);
  color: var(--text);
  border-radius: 12px;
  padding: 0.75rem 1rem;
  font-size: 0.95rem;
  box-shadow: inset 0 0 0 1px rgba(2, 6, 23, 0.3);
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
}

div[data-testid="stTextInput"] input:focus {
  border-color: var(--secondary);
  box-shadow: 0 0 0 3px rgba(0, 194, 255, 0.2);
}

div[data-testid="stTextInput"] input:hover {
  border-color: rgba(0, 194, 255, 0.4);
  box-shadow: 0 10px 24px rgba(2, 6, 23, 0.25);
}

div[data-testid="stTextInput"] input::placeholder {
  color: var(--muted);
}

div.stButton > button {
  width: 100%;
  background: linear-gradient(135deg, rgba(108, 60, 240, 0.8), rgba(0, 194, 255, 0.8));
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  padding: 0.7rem 1rem;
  font-weight: 600;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

div.stButton > button:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(108, 60, 240, 0.4);
}

.theme-toggle-fixed,
button[title="Toggle theme"], button[aria-label="Toggle theme"] {
  width: 52px !important;
  height: 52px !important;
  border-radius: 50% !important;
  padding: 0 !important;
  font-size: 1.3rem !important;
  font-weight: 700 !important;
  background: radial-gradient(circle at top, rgba(0, 194, 255, 0.7), rgba(108, 60, 240, 0.8)) !important;
  box-shadow: 0 12px 26px rgba(108, 60, 240, 0.45) !important;
  display: block !important;
  margin-left: auto !important;
  position: fixed !important;
  top: 68px !important;
  right: 26px !important;
  z-index: 5 !important;
}

.theme-toggle-fixed:hover,
button[title="Toggle theme"]:hover, button[aria-label="Toggle theme"]:hover {
  transform: translateY(-3px) scale(1.04);
  box-shadow: 0 16px 34px rgba(0, 194, 255, 0.5);
}

div[data-testid="stSelectbox"] > div {
  background: var(--panel-strong);
  border: 1px solid rgba(108, 60, 240, 0.35);
  border-radius: 12px;
  min-height: var(--control-height);
  height: var(--control-height);
}

div[data-testid="stSelectbox"] span {
  color: var(--text);
}

div[data-baseweb="select"] > div {
  background: var(--panel-strong) !important;
  border: 1px solid rgba(108, 60, 240, 0.35) !important;
  min-height: var(--control-height) !important;
  height: var(--control-height) !important;
  display: flex !important;
  align-items: center !important;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}

div[data-baseweb="select"] > div:hover {
  border-color: rgba(0, 194, 255, 0.45) !important;
  box-shadow: 0 10px 24px rgba(2, 6, 23, 0.25);
}

div[data-baseweb="select"] * {
  color: var(--text) !important;
}

div[data-testid="stDataFrame"] {
  background: var(--panel);
  border: 1px solid var(--panel-border);
  border-radius: 18px;
  padding: 0.6rem;
  box-shadow: 0 18px 32px rgba(2, 6, 23, 0.6);
}

div[data-testid="stDataFrame"] [role="gridcell"],
div[data-testid="stDataFrame"] [role="columnheader"],
div[data-testid="stDataFrame"] [role="rowheader"] {
  color: var(--text) !important;
}

div[data-testid="stTable"] th,
div[data-testid="stTable"] td {
  color: var(--text) !important;
}

div[data-testid="stExpander"] summary,
div[data-testid="stExpander"] summary * {
  color: var(--text) !important;
}

div[data-testid="stPlotlyChart"] {
  background: var(--panel);
  border: 1px solid var(--panel-border);
  border-radius: 18px;
  padding: 0.6rem;
  box-shadow: 0 18px 32px rgba(2, 6, 23, 0.6);
}

div[data-testid="stCodeBlock"] {
  background: var(--panel);
  border: 1px solid var(--panel-border);
  border-radius: 18px;
  box-shadow: 0 18px 32px rgba(2, 6, 23, 0.6);
}

div[data-testid="stDataFrame"]:hover,
div[data-testid="stPlotlyChart"]:hover,
div[data-testid="stCodeBlock"]:hover {
  transform: translateY(-4px);
  border-color: rgba(0, 194, 255, 0.45);
  box-shadow: 0 26px 60px rgba(2, 6, 23, 0.75), 0 0 34px rgba(0, 194, 255, 0.12);
}

div[data-testid="stCodeBlock"] pre {
  background: transparent;
}

div[data-testid="stSpinner"] {
  color: var(--secondary);
}

.insight-card {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  padding: 1.4rem 1.6rem;
}

.insight-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: #fff;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  letter-spacing: 0.12em;
  font-size: 0.8rem;
}

.insight-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.2rem;
}

.insight-text {
  color: var(--muted);
  font-size: 0.95rem;
}

.loader-card {
  padding: 1.4rem 1.6rem;
  position: relative;
  overflow: hidden;
}

.loader-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.35rem;
}

.loader-sub {
  color: var(--muted);
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.loader-bars {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.6rem;
}

.loader-bars span {
  height: 8px;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(108, 60, 240, 0.2), rgba(0, 194, 255, 0.5), rgba(108, 60, 240, 0.2));
  background-size: 200% 100%;
  animation: shimmer 1.4s ease-in-out infinite;
}

.loader-bars span:nth-child(2) {
  animation-delay: 0.2s;
}

.loader-bars span:nth-child(3) {
  animation-delay: 0.4s;
}

.chart-buffer {
  padding: 1rem 1.2rem;
  margin-top: 0.6rem;
}

.chart-buffer .loader-title {
  font-size: 0.95rem;
}

.chart-buffer .loader-sub {
  font-size: 0.85rem;
}

.chart-buffer .loader-bars span {
  height: 6px;
}

@keyframes shimmer {
  0% { background-position: 0% 50%; opacity: 0.5; }
  50% { background-position: 100% 50%; opacity: 1; }
  100% { background-position: 0% 50%; opacity: 0.5; }
}

.recommendations-card {
  padding: 1.4rem 1.6rem;
}

.recommendations-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.65rem 0;
  border-bottom: 1px solid rgba(108, 60, 240, 0.18);
}

.recommendation-item:last-child {
  border-bottom: none;
}

.recommendation-summary {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.recommendation-action {
  color: var(--muted);
  font-size: 0.9rem;
}

.impact-pill {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 600;
  border: 1px solid transparent;
  white-space: nowrap;
}

.impact-high {
  background: rgba(255, 122, 89, 0.18);
  color: #FF7A59;
  border-color: rgba(255, 122, 89, 0.4);
}

.impact-medium {
  background: rgba(0, 194, 255, 0.18);
  color: #00C2FF;
  border-color: rgba(0, 194, 255, 0.4);
}

.impact-low {
  background: rgba(108, 60, 240, 0.18);
  color: #6C3CF0;
  border-color: rgba(108, 60, 240, 0.4);
}

.explain-card {
  margin-top: 0.8rem;
  padding: 0.9rem 1.1rem;
  background: var(--panel-strong);
  border: 1px solid var(--panel-border);
  border-radius: 14px;
  color: var(--text);
}

.explain-card ul {
  margin: 0.4rem 0 0 1.2rem;
  color: var(--muted);
}

div[data-testid="stDownloadButton"] > button {
  width: 100%;
  background: linear-gradient(135deg, rgba(0, 194, 255, 0.8), rgba(108, 60, 240, 0.8));
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  padding: 0.6rem 0.9rem;
  font-weight: 600;
}

div[data-testid="stDownloadButton"] > button * {
  color: #fff !important;
}

div[data-testid="stDownloadButton"] > button:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(0, 194, 255, 0.35);
}

.footer {
  text-align: center;
  color: var(--muted);
  font-size: 0.85rem;
  margin-top: 2rem;
  margin-bottom: 0;
  padding-top: 1.5rem;
  padding-bottom: 0;
  border-top: 1px solid rgba(108, 60, 240, 0.2);
}

@media (max-width: 768px) {
  .hero {
    padding: 1.3rem;
  }
  .kpi-value {
    font-size: 1.6rem;
  }
}
</style>
"""
).substitute(
    bg=bg,
    panel=panel,
    panel_strong=panel_strong,
    panel_border=panel_border,
    text=text,
    muted=muted,
    glow=glow,
    particle_1=particle_1,
    particle_2=particle_2,
    particle_3=particle_3,
    particle_4=particle_4,
)

st.markdown(css, unsafe_allow_html=True)

# -------------------------
# CHATLING CHATBOT WIDGET
# -------------------------

components.html(
    """
<script>
(() => {
  const host = window.parent;
  const doc = host.document;

  function injectChatling() {
    if (!doc || !doc.body) return;
    host.chtlConfig = { chatbotId: "8986115621" };

    if (doc.getElementById("chtl-script")) return;
    const script = doc.createElement("script");
    script.async = true;
    script.dataset.id = "8986115621";
    script.id = "chtl-script";
    script.type = "text/javascript";
    script.src = "https://chatling.ai/js/embed.js";
    doc.body.appendChild(script);
  }

  if (doc && doc.readyState === "loading") {
    doc.addEventListener("DOMContentLoaded", injectChatling, { once: true });
  } else {
    injectChatling();
  }
})();
</script>
""",
    height=0,
    width=0,
)

# -------------------------
# ANIMATED PARTICLE BACKGROUND + KPI COUNT-UP
# -------------------------

components.html(
    """
<script>
(() => {
  try {
    const host = window.parent;
    const doc = host.document;

    const existingCanvas = doc.getElementById('particle-canvas');
    if (existingCanvas) {
      existingCanvas.remove();
    }

    const canvas = doc.createElement('canvas');
    canvas.id = 'particle-canvas';
    canvas.style.position = 'fixed';
    canvas.style.inset = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.zIndex = '0';
    canvas.style.pointerEvents = 'none';
    canvas.style.opacity = '0.55';
    doc.body.appendChild(canvas);

    const ctx = canvas.getContext('2d');

    const styles = host.getComputedStyle(doc.documentElement);
    const palette = [
      styles.getPropertyValue('--particle-1').trim() || 'rgba(108, 60, 240, 0.6)',
      styles.getPropertyValue('--particle-2').trim() || 'rgba(0, 194, 255, 0.55)',
      styles.getPropertyValue('--particle-3').trim() || 'rgba(255, 122, 89, 0.5)',
      styles.getPropertyValue('--particle-4').trim() || 'rgba(230, 231, 234, 0.55)',
    ];

    const state = {
      particles: [],
      density: 0.00085,
      attractRadius: 280,
      returnStrength: 0.003,
    };

    const mouse = {
      x: 0,
      y: 0,
      active: false,
    };

    function resize() {
      canvas.width = host.innerWidth;
      canvas.height = host.innerHeight;
      const targetCount = Math.min(1200, Math.max(420, Math.floor(canvas.width * canvas.height * state.density)));
      state.particles = Array.from({ length: targetCount }, () => {
        const baseVx = (Math.random() - 0.5) * 0.25;
        const baseVy = (Math.random() - 0.5) * 0.25;
        const isLarge = Math.random() < 0.08;
        const x = Math.random() * canvas.width;
        const y = Math.random() * canvas.height;
        return {
          x,
          y,
          homeX: x,
          homeY: y,
          vx: baseVx,
          vy: baseVy,
          baseVx,
          baseVy,
          r: isLarge ? Math.random() * 2.4 + 2.2 : Math.random() * 1.5 + 0.25,
          color: palette[Math.floor(Math.random() * palette.length)],
        };
      });
    }

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (let i = 0; i < state.particles.length; i++) {
        const p = state.particles[i];
        ctx.fillStyle = p.color;
        let attracted = false;
        if (mouse.active) {
          const dx = mouse.x - p.x;
          const dy = mouse.y - p.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < state.attractRadius && dist > 0.1) {
            const pull = (1 - dist / state.attractRadius) * 0.08;
            p.vx += (dx / dist) * pull;
            p.vy += (dy / dist) * pull;
            attracted = true;
          }
        }

        if (mouse.active && attracted) {
          p.vx += (p.baseVx - p.vx) * 0.01;
          p.vy += (p.baseVy - p.vy) * 0.01;
          p.vx += (Math.random() - 0.5) * 0.015;
          p.vy += (Math.random() - 0.5) * 0.015;
          p.vx *= 0.987;
          p.vy *= 0.987;
        } else {
          const dxHome = p.homeX - p.x;
          const dyHome = p.homeY - p.y;
          p.vx += dxHome * state.returnStrength;
          p.vy += dyHome * state.returnStrength;
          p.vx *= 0.9;
          p.vy *= 0.9;
        }

        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();
      }

      host.requestAnimationFrame(draw);
    }

    resize();
    host.addEventListener('resize', resize);
    doc.addEventListener('mousemove', (event) => {
      mouse.x = event.clientX;
      mouse.y = event.clientY;
      mouse.active = true;
    });
    doc.addEventListener('mouseleave', () => {
      mouse.active = false;
    });
    draw();

    function animateNode(node) {
      const target = parseFloat(node.dataset.target || '0');
      const decimals = parseInt(node.dataset.decimals || '0', 10);
      const prefix = node.dataset.prefix || '';
      const suffix = node.dataset.suffix || '';
      const duration = 1200;
      const start = host.performance.now();

      function format(value) {
        return prefix + value.toLocaleString(undefined, {
          minimumFractionDigits: decimals,
          maximumFractionDigits: decimals,
        }) + suffix;
      }

      function step(now) {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const value = target * eased;
        node.textContent = format(value);
        if (progress < 1) {
          host.requestAnimationFrame(step);
        }
      }

      host.requestAnimationFrame(step);
    }

    function pinThemeToggle() {
      const buttons = Array.from(doc.querySelectorAll('button'));
      const target = buttons.find((btn) => {
        const text = (btn.textContent || '').trim();
        const title = (btn.getAttribute('title') || '').trim();
        const label = (btn.getAttribute('aria-label') || '').trim();
        return text === '☀' || text === '☾' || title === 'Toggle theme' || label === 'Toggle theme';
      });
      if (target && !target.classList.contains('theme-toggle-fixed')) {
        target.classList.add('theme-toggle-fixed');
      }
    }

    function registerRevealTargets() {
      const selectors = [
        '.hero',
        '.glass-card',
        '.section-title',
        'div[data-testid=\"stDataFrame\"]',
        'div[data-testid=\"stPlotlyChart\"]',
        'div[data-testid=\"stCodeBlock\"]',
      ];
      doc.querySelectorAll(selectors.join(',')).forEach((el) => {
        if (!el.classList.contains('reveal-target')) {
          el.classList.add('reveal-target');
        }
      });
    }

    const revealObserver = new host.IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('reveal-visible');
            revealObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.18 }
    );

    function observeReveals() {
      const targets = doc.querySelectorAll('.reveal-target:not(.reveal-ready)');
      targets.forEach((el) => {
        el.classList.add('reveal-ready');
        revealObserver.observe(el);
      });
    }

    function animateKpis() {
      const nodes = doc.querySelectorAll('.kpi-value');
      nodes.forEach((node) => {
        const target = node.dataset.target || '0';
        if (node.dataset.animated === target) return;
        node.dataset.animated = target;
        animateNode(node);
      });
    }

    const observer = new host.MutationObserver(() => {
      animateKpis();
      pinThemeToggle();
      registerRevealTargets();
      observeReveals();
    });
    observer.observe(doc.body, { childList: true, subtree: true });
    animateKpis();
    pinThemeToggle();
    registerRevealTargets();
    observeReveals();
  } catch (err) {
    console.error('Particle background failed', err);
  }
})();
</script>
""",
    height=0,
    width=0,
)

# -------------------------
# SECTION NAV
# -------------------------

st.markdown(
    """
<div class="section-nav">
  <div class="section-nav-title">Navigate</div>
  <div class="section-nav-links">
    <a class="section-link" href="#data-preview">DATA PREVIEW</a>
    <a class="section-link" href="#ask">ASK Q</a>
    <a class="section-link" href="#sql-query">SQL QUERY</a>
    <a class="section-link" href="#dashboard">DASHBOARD</a>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

components.html(
    """
<script>
(() => {
  const host = window.parent;
  const doc = host.document;
  let toastTimer = null;

  function getQuestionValue() {
    const byPlaceholder = doc.querySelector('input[placeholder="Example: Show revenue by campaign type"]');
    if (byPlaceholder && typeof byPlaceholder.value === 'string') {
      return byPlaceholder.value.trim();
    }
    const byId = doc.querySelector('input[id*="question"]');
    if (byId && typeof byId.value === 'string') {
      return byId.value.trim();
    }
    return '';
  }

  function showNavToast(message) {
    let toast = doc.querySelector('.nav-toast');
    if (!toast) {
      toast = doc.createElement('div');
      toast.className = 'nav-toast';
      doc.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add('show');
    if (toastTimer) {
      host.clearTimeout(toastTimer);
    }
    toastTimer = host.setTimeout(() => {
      toast.classList.remove('show');
    }, 2200);
  }

  function bindSmoothLinks() {
    const links = Array.from(doc.querySelectorAll('.section-link'));
    links.forEach((link) => {
      if (link.dataset.smoothBound) return;
      link.dataset.smoothBound = 'true';
      link.addEventListener('click', (event) => {
        event.preventDefault();
        const targetId = link.getAttribute('href');
        if (!targetId || !targetId.startsWith('#')) return;
        const needsQuestion = targetId === '#sql-query' || targetId === '#dashboard';
        if (needsQuestion && !getQuestionValue()) {
          showNavToast('Please ask a question first.');
          return;
        }
        const target = doc.querySelector(targetId);
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  }

  bindSmoothLinks();
  const observer = new host.MutationObserver(bindSmoothLinks);
  observer.observe(doc.body, { childList: true, subtree: true });
})();
</script>
""",
    height=0,
    width=0,
)

# -------------------------
# HEADER + UPLOAD
# -------------------------

hero_col, upload_col = st.columns([2.2, 1])

with hero_col:
    st.markdown(
        """
<div class="hero">
  <div class="hero-badge">Digital Marketing Performance Suite</div>
  <div class="gradient-title">Nykaa Digital Marketing</div>
  <div class="hero-subtitle">Conversational analytics for digital marketing performance</div>
  <div class="hero-meta">Track channels, campaigns, and segments with fast, contextual BI insights.</div>
</div>
""",
        unsafe_allow_html=True,
    )

with upload_col:
    st.markdown(
        """
<div class="glass-card upload-card">
  <div class="upload-title">Upload Dataset</div>
  <div class="hero-meta">Upload a CSV file or use the bundled sample dataset.</div>
</div>
""",
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader("Upload CSV dataset (optional)", type=["csv"], label_visibility="collapsed")

# -------------------------
# LOAD DATA
# -------------------------

def extract_csv_from_bytes(raw_bytes):
    text = raw_bytes.decode("latin1", errors="ignore")
    start = text.find("Campaign_ID")
    if start == -1:
        lines = [line for line in text.splitlines() if line.count(",") >= 3]
        if not lines:
            raise ValueError("No CSV-like content found.")
        start = text.find(lines[0])
    csv_text = text[start:]
    lines = [line for line in csv_text.splitlines() if line.count(",") >= 3]
    csv_text = "\n".join(lines)
    return pd.read_csv(StringIO(csv_text))


def read_csv_bytes(raw_bytes):
    for encoding in ("utf-8", "latin1"):
        try:
            return pd.read_csv(BytesIO(raw_bytes), encoding=encoding, low_memory=False)
        except Exception:
            continue
    return extract_csv_from_bytes(raw_bytes)


def normalize_dataset(df):
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    df = df.loc[:, ~df.columns.str.contains("bplist", case=False, na=False)]

    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")

    return df


@st.cache_data(show_spinner=False)
def load_dataset_from_bytes(raw_bytes):
    try:
        df = read_csv_bytes(raw_bytes)
    except Exception:
        df = pd.read_csv(BytesIO(raw_bytes), encoding="latin1", low_memory=False)
    return normalize_dataset(df)


@st.cache_data(show_spinner=False)
def load_sample_dataset():
    sample = textwrap.dedent("""\
Campaign_ID,Campaign_Type,Channel_Used,Impressions,Clicks,Leads,Conversions,Revenue,ROI
A1,Social Media,YouTube,50000,6000,2000,1500,1800000,6.1
A2,Paid Ads,Instagram,90000,3000,1800,1200,1040000,3.2
A3,Email,Gmail,40000,4200,2000,1400,980000,4.1
A4,Influencer,Instagram,72000,5200,2400,1600,1520000,5.4
A5,Display Ads,Google,110000,4100,2100,1250,1180000,3.9
A6,Social Media,Facebook,64000,5600,2300,1500,1410000,4.7
A7,Affiliate,Blog,35000,1800,900,520,420000,2.1
A8,Email,Outlook,38000,2600,1300,780,620000,2.9
A9,Paid Ads,YouTube,95000,5200,2400,1650,1760000,4.2
A10,Influencer,YouTube,56000,3700,1900,1200,980000,3.6
A11,Display Ads,Instagram,88000,4500,2000,1350,1320000,3.7
A12,Social Media,WhatsApp,47000,3100,1500,920,780000,3.1
A13,Affiliate,Review Sites,42000,2100,1000,640,520000,2.4
A14,Email,Gmail,46000,2800,1400,880,690000,3.0
A15,Paid Ads,Google,105000,6100,2600,1750,1960000,4.5
A16,Influencer,Instagram,61000,3900,1750,1150,910000,3.4
A17,Social Media,Instagram,73000,5400,2200,1480,1500000,4.9
A18,Display Ads,YouTube,99000,4800,2100,1420,1380000,3.5
""")
    df = pd.read_csv(StringIO(sample))
    return normalize_dataset(df)


def load_dataset(uploaded_file):

    if uploaded_file:
        raw_bytes = uploaded_file.getvalue()
        data_sig = hashlib.md5(raw_bytes).hexdigest()
        df = load_dataset_from_bytes(raw_bytes)

    else:
        df = load_sample_dataset()
        data_sig = "sample-v1"

    return df, data_sig


data, data_sig = load_dataset(uploaded_file)

# -------------------------
# KPI SECTION
# -------------------------

def safe_sum(col):
    return data[col].sum() if col in data.columns else 0


def safe_mean(col):
    return data[col].mean() if col in data.columns else 0


st.markdown('<div id="kpis"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Key Performance Indicators</div>', unsafe_allow_html=True)

def build_kpis(df):
    items = []

    def add_item(label, value, decimals=0, prefix="", suffix="", foot=""):
        items.append(
            {
                "label": label,
                "value": value,
                "decimals": decimals,
                "prefix": prefix,
                "suffix": suffix,
                "foot": foot,
            }
        )

    if "Revenue" in df.columns:
        add_item("Total Revenue", safe_sum("Revenue"), 0, "INR ", "", "Aggregated across campaigns")
    if "Conversions" in df.columns:
        add_item("Total Conversions", safe_sum("Conversions"), 0, "", "", "Qualified customer actions")
    if "ROI" in df.columns:
        add_item("Average ROI", safe_mean("ROI"), 2, "", "", "Return on investment")

    if len(items) < 3:
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        used_cols = {item["label"].split(" ", 1)[-1] for item in items}
        for col in numeric_cols:
            if col in used_cols:
                continue
            col_lower = col.lower()
            if any(token in col_lower for token in ["roi", "rate", "ratio", "percent", "percentage", "avg", "mean"]):
                value = df[col].mean()
                label = f"Average {col}"
                decimals = 2
            else:
                value = df[col].sum()
                label = f"Total {col}"
                decimals = 0
            prefix = "INR " if any(token in col_lower for token in ["revenue", "sales", "cost", "spend", "budget"]) else ""
            add_item(label, value, decimals, prefix, "", "Auto-detected metric")
            if len(items) >= 3:
                break

    if len(items) < 3:
        add_item("Total Records", len(df), 0, "", "", "Rows in dataset")

    return items[:3]


kpis = build_kpis(data)
kpi_cards = "".join(
    [
        f"""
  <div class="glass-card kpi-card">
    <div class="kpi-label">{item['label']}</div>
    <div class="kpi-value" data-target="{item['value']}" data-prefix="{item['prefix']}" data-suffix="{item['suffix']}" data-decimals="{item['decimals']}">0</div>
    <div class="kpi-foot">{item['foot']}</div>
  </div>
        """
        for item in kpis
    ]
)

st.markdown(
    f"""
<div class="kpi-grid">
{kpi_cards}
</div>
""",
    unsafe_allow_html=True,
)

# -------------------------
# DATA PREVIEW
# -------------------------

st.markdown('<div id="data-preview"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Dataset Preview</div>', unsafe_allow_html=True)

st.dataframe(data.head(200), use_container_width=True)

# -------------------------
# DATABASE
# -------------------------

@st.cache_resource(show_spinner=False)
def get_sqlite_conn(db_path="data.db"):
    return sqlite3.connect(db_path, check_same_thread=False)


conn = get_sqlite_conn()
if st.session_state.get("data_sig") != data_sig:
    data.to_sql("campaigns", conn, if_exists="replace", index=False)
    st.session_state.data_sig = data_sig

# -------------------------
# GEMINI AI (OPTIONAL)
# -------------------------

def get_gemini_api_key():
    for key_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_AI_API_KEY"):
        value = os.getenv(key_name)
        if value:
            return value
    try:
        return st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
    except Exception:
        return None


def extract_sql(text):
    if not text:
        return None
    fence = re.search(r"```(?:sql)?\s*(.*?)```", text, re.S | re.I)
    if fence:
        text = fence.group(1)
    match = re.search(r"\b(SELECT|WITH)\b", text, re.I)
    if not match:
        return None
    sql = text[match.start() :]
    sql = sql.split(";")[0].strip()
    return sql


def is_safe_sql(sql):
    if not sql or not re.match(r"^(SELECT|WITH)\b", sql, re.I):
        return False
    if re.search(r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|PRAGMA|ATTACH|DETACH)\b", sql, re.I):
        return False
    if "campaigns" not in sql.lower():
        return False
    return True


def gemini_generate_sql(question_text, df, api_key, model_name):
    columns = [f"{col} ({dtype})" for col, dtype in df.dtypes.items()]
    date_samples = []
    if "Date" in df.columns:
        date_samples = df["Date"].dropna().astype(str).head(5).tolist()
    prompt = textwrap.dedent(
        f"""
        You are an expert data analyst. Convert the user's question into ONE SQLite SQL query.
        Use only the table `campaigns`.
        Return ONLY SQL (no markdown, no commentary).

        Table schema:
        {", ".join(columns)}

        Date samples (if present): {date_samples}

        User question: {question_text}
        """
    ).strip()

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError("Gemini API request failed.") from exc
    except Exception as exc:
        raise RuntimeError("Gemini API request failed.") from exc

    parts = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [])
    )
    text = "".join(part.get("text", "") for part in parts)
    sql = extract_sql(text)
    if is_safe_sql(sql):
        return sql
    return None


def gemini_generate_text(prompt, api_key, model_name):
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise RuntimeError("Gemini API request failed.") from exc

    parts = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [])
    )
    text = "".join(part.get("text", "") for part in parts).strip()
    return text


def extract_json_block(text):
    if not text:
        return None
    match = re.search(r"(\{.*\}|\[.*\])", text, re.S)
    if match:
        return match.group(1)
    return None


def format_kpi_value(item):
    value = item.get("value", 0)
    decimals = int(item.get("decimals", 0) or 0)
    prefix = item.get("prefix", "")
    suffix = item.get("suffix", "")
    if pd.isna(value):
        return "N/A"
    try:
        if decimals <= 0:
            formatted = f"{float(value):,.0f}"
        else:
            formatted = f"{float(value):,.{decimals}f}"
    except Exception:
        formatted = str(value)
    return f"{prefix}{formatted}{suffix}"


def brief_text(text, max_words=16):
    if not text:
        return ""
    words = str(text).strip().split()
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words]) + "..."


def build_fallback_explanation(result_df, chart_type, time_col=None):
    numeric_cols = result_df.select_dtypes(include="number").columns.tolist()
    non_numeric_cols = [c for c in result_df.columns if c not in numeric_cols]
    value_col = numeric_cols[0] if numeric_cols else None
    category_col = non_numeric_cols[0] if non_numeric_cols else None

    what = "Summarizes your question and the query output values."
    trend = "Shows the main pattern without strong outliers."
    insight = "Focus on leaders and improve lagging segments."

    if value_col and time_col:
        sorted_df = result_df.sort_values(time_col)
        first_val = sorted_df[value_col].iloc[0]
        last_val = sorted_df[value_col].iloc[-1]
        change = "upward" if last_val >= first_val else "downward"
        what = f"{value_col} over time from query results."
        trend = f"Overall movement is {change}."
        insight = "Align actions to the dominant time trend."
    elif value_col and category_col:
        what = f"Compares {value_col} across {category_col} from the query."
        sorted_df = result_df.sort_values(value_col, ascending=False)
        top = sorted_df.iloc[0]
        bottom = sorted_df.iloc[-1]
        trend = f"{top[category_col]} leads, {bottom[category_col]} trails."
        insight = f"Prioritize {top[category_col]} and lift {bottom[category_col]}."

    return {
        "what": str(what),
        "trend": str(trend),
        "insight": str(insight),
    }


def build_chart_explanation(question_text, result_df, chart_type, time_col=None, api_key=None, model_name=None):
    if api_key:
        sample = result_df.head(10).to_csv(index=False)
        prompt = textwrap.dedent(
            f"""
            You are a senior BI analyst. Provide an executive-friendly explanation for the chart.
            Keep it very brief (max 12 words per bullet) and use this exact format with three bullet lines:
            - What the chart shows: ...
            - Key trends or anomalies: ...
            - Important business insights: ...
            Make sure the first bullet references the user's question and what data the chart represents.

            Question: {question_text}
            Chart type: {chart_type}
            Data sample:
            {sample}
            """
        ).strip()
        try:
            response = gemini_generate_text(prompt, api_key, model_name)
            lines = [line.strip("•- ").strip() for line in response.splitlines() if line.strip()]
            mapped = {"what": "", "trend": "", "insight": ""}
            for line in lines:
                lower = line.lower()
                if lower.startswith("what"):
                    mapped["what"] = line.split(":", 1)[-1].strip()
                elif lower.startswith("key"):
                    mapped["trend"] = line.split(":", 1)[-1].strip()
                elif lower.startswith("important"):
                    mapped["insight"] = line.split(":", 1)[-1].strip()
            if all(mapped.values()):
                return mapped
        except RuntimeError:
            pass

    return build_fallback_explanation(result_df, chart_type, time_col=time_col)


def build_fallback_recommendations(result_df, question_text):
    numeric_cols = result_df.select_dtypes(include="number").columns.tolist()
    non_numeric_cols = [c for c in result_df.columns if c not in numeric_cols]
    value_col = numeric_cols[0] if numeric_cols else None
    category_col = non_numeric_cols[0] if non_numeric_cols else None
    recommendations = []

    if value_col and category_col and len(result_df) > 1:
        sorted_df = result_df.sort_values(value_col, ascending=False)
        top = sorted_df.iloc[0]
        bottom = sorted_df.iloc[-1]
        avg = sorted_df[value_col].mean()
        top_impact = "High" if top[value_col] >= avg * 1.15 else "Medium"
        bottom_impact = "Medium" if bottom[value_col] < avg * 0.9 else "Low"

        recommendations.append(
            {
                "summary": f"Scale {top[category_col]} investment",
                "action": f"Shift budget toward {top[category_col]} where {value_col} is strongest.",
                "impact": top_impact,
            }
        )
        recommendations.append(
            {
                "summary": f"Optimize {bottom[category_col]}",
                "action": f"Refresh creative or targeting to lift {bottom[category_col]} performance.",
                "impact": bottom_impact,
            }
        )

    recommendations.append(
        {
            "summary": "Run controlled experiments",
            "action": "Test a 5-10% reallocation to validate lift before scaling.",
            "impact": "Low",
        }
    )

    return recommendations[:3]


def build_smart_recommendations(question_text, result_df, api_key=None, model_name=None):
    if api_key:
        sample = result_df.head(10).to_csv(index=False)
        prompt = textwrap.dedent(
            f"""
            You are an executive BI strategist. Based on the dataset sample, return JSON with 3 recommendations.
            Each item must include: summary, action, impact (High/Medium/Low).
            Keep summaries under 8 words.

            Question: {question_text}
            Data sample:
            {sample}
            """
        ).strip()
        try:
            response = gemini_generate_text(prompt, api_key, model_name)
            json_block = extract_json_block(response)
            if json_block:
                parsed = json.loads(json_block)
                if isinstance(parsed, dict):
                    parsed = parsed.get("recommendations", [])
                cleaned = []
                for item in parsed:
                    summary = str(item.get("summary", "")).strip()
                    action = str(item.get("action", "")).strip()
                    impact = str(item.get("impact", "Medium")).strip().title()
                    if summary and action:
                        cleaned.append(
                            {
                                "summary": summary,
                                "action": action,
                                "impact": impact if impact in ("High", "Medium", "Low") else "Medium",
                            }
                        )
                if cleaned:
                    return cleaned[:3]
        except (RuntimeError, json.JSONDecodeError):
            pass

    return build_fallback_recommendations(result_df, question_text)




def sql_quote(identifier):
    safe = str(identifier).replace('"', '""')
    return f'"{safe}"'


def build_fallback_sql(df):
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    non_numeric_cols = [c for c in df.columns if c not in numeric_cols]

    preferred_categories = ["Channel_Used", "Campaign_Type", "Campaign_ID"]
    preferred_values = ["Revenue", "Conversions", "Clicks", "Impressions", "ROI"]

    category_col = next((c for c in preferred_categories if c in df.columns), None)
    value_col = next((c for c in preferred_values if c in df.columns), None)

    if not category_col and non_numeric_cols:
        category_col = non_numeric_cols[0]
    if not value_col and numeric_cols:
        value_col = numeric_cols[0]

    if category_col and value_col:
        agg = "AVG" if value_col.lower() in {"roi", "rate", "ratio", "percentage", "percent"} else "SUM"
        return (
            f"SELECT {sql_quote(category_col)} AS Category, "
            f"{agg}({sql_quote(value_col)}) AS Value "
            f"FROM campaigns GROUP BY {sql_quote(category_col)} ORDER BY Value DESC"
        )

    if value_col:
        return f"SELECT {sql_quote(value_col)} AS Value FROM campaigns"

    return "SELECT * FROM campaigns LIMIT 200"


@st.cache_data(show_spinner=False)
def run_sql_query(sql_query, data_sig):
    with sqlite3.connect("data.db") as conn:
        return pd.read_sql(sql_query, conn)


def build_export_figure(fig, kpis, dashboard_title, template, colorway, text_color, chart_type):
    kpi_items = kpis[:3] if kpis else []
    cols = max(1, len(kpi_items))
    plot_type = "domain" if chart_type == "Pie" else "xy"
    specs = [[{"type": "indicator"}] * cols, [{"type": plot_type, "colspan": cols}] + [None] * (cols - 1)]
    export_fig = make_subplots(
        rows=2,
        cols=cols,
        specs=specs,
        row_heights=[0.28, 0.72],
        vertical_spacing=0.08,
    )

    if kpi_items:
        for idx, item in enumerate(kpi_items):
            export_fig.add_trace(
                go.Indicator(
                    mode="number",
                    value=item.get("value", 0),
                    number={
                        "prefix": item.get("prefix", ""),
                        "suffix": item.get("suffix", ""),
                        "valueformat": f".{int(item.get('decimals', 0))}f",
                    },
                    title={"text": item.get("label", "KPI"), "font": {"size": 14}},
                ),
                row=1,
                col=idx + 1,
            )

    for trace in fig.data:
        export_fig.add_trace(trace, row=2, col=1)

    export_fig.update_layout(
        template=template,
        colorway=colorway,
        height=900,
        title_text=dashboard_title,
        title_x=0.02,
        font_color=text_color,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=80, b=40),
    )

    try:
        xaxis_title = fig.layout.xaxis.title.text if fig.layout.xaxis.title else None
        yaxis_title = fig.layout.yaxis.title.text if fig.layout.yaxis.title else None
        if xaxis_title:
            export_fig.update_xaxes(title_text=xaxis_title, row=2, col=1)
        if yaxis_title:
            export_fig.update_yaxes(title_text=yaxis_title, row=2, col=1)
    except Exception:
        pass

    return export_fig


def get_export_assets(fig, kpis, dashboard_title, template, colorway, text_color, chart_type, signature=None):
    if importlib.util.find_spec("kaleido") is None:
        return None, None, "Export requires the Kaleido engine. Run: python -m pip install kaleido"
    if signature is None:
        signature_source = fig.to_json() + json.dumps(kpis, sort_keys=True, default=str) + dashboard_title + chart_type
        signature = hashlib.md5(signature_source.encode("utf-8")).hexdigest()
    cached = st.session_state.get("export_cache", {})
    if cached.get("sig") == signature:
        return cached.get("png"), cached.get("pdf"), cached.get("error")

    export_fig = build_export_figure(fig, kpis, dashboard_title, template, colorway, text_color, chart_type)
    png_bytes = None
    pdf_bytes = None
    errors = []

    try:
        png_bytes = pio.to_image(export_fig, format="png", scale=2)
    except Exception:
        errors.append("PNG export requires the Kaleido engine.")

    try:
        pdf_bytes = pio.to_image(export_fig, format="pdf")
    except Exception:
        errors.append("PDF export requires the Kaleido engine.")

    error = " ".join(errors) if errors else None

    st.session_state.export_cache = {
        "sig": signature,
        "png": png_bytes,
        "pdf": pdf_bytes,
        "error": error,
    }
    return png_bytes, pdf_bytes, error



# -------------------------
# QUERY INPUT
# -------------------------

st.markdown('<div id="ask"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Ask a Business Question</div>', unsafe_allow_html=True)

if "question" not in st.session_state:
    st.session_state.question = ""

if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = get_gemini_api_key() or ""
if "gemini_model" not in st.session_state:
    st.session_state.gemini_model = "gemini-2.5-flash"
if "use_gemini" not in st.session_state:
    st.session_state.use_gemini = bool(st.session_state.gemini_api_key)


def set_question(value):
    st.session_state.question = value


st.text_input(
    "",
    key="question",
    placeholder="Example: Show revenue by campaign type",
    label_visibility="collapsed",
)

c1, c2, c3 = st.columns(3)

if c1.button("Revenue by campaign", on_click=set_question, args=("Show revenue by campaign type",)):
    pass

if c2.button("Highest ROI channel", on_click=set_question, args=("Which channel has the highest ROI",)):
    pass

if c3.button("Clicks vs impressions", on_click=set_question, args=("Compare clicks and impressions",)):
    pass

question = st.session_state.question

if "chart_explanations" not in st.session_state:
    st.session_state.chart_explanations = {}
if "recommendation_cache" not in st.session_state:
    st.session_state.recommendation_cache = {}
if "chart_cache" not in st.session_state:
    st.session_state.chart_cache = {}
if "export_cache" not in st.session_state:
    st.session_state.export_cache = {}
if "last_chart_signature" not in st.session_state:
    st.session_state.last_chart_signature = ""
if "last_chart_pref" not in st.session_state:
    st.session_state.last_chart_pref = ""

# -------------------------
# QUERY ENGINE
# -------------------------

if question:

    loader = st.empty()
    loader.markdown(
        """
<div class="glass-card loader-card">
  <div class="loader-title">Generating your dashboard</div>
  <div class="loader-sub">Analyzing data and assembling insights...</div>
  <div class="loader-bars">
    <span></span>
    <span></span>
    <span></span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.spinner("Generating dashboard..."):

        q = question.lower()
        sql_query = None
        engine_used = "Rule-based"
        preferred_chart = None

        if (
            ("roi" in q)
            and ("channel" in q or "channel_used" in q)
            and any(token in q for token in ["highest", "top", "best", "max"])
        ):
            sql_query = """
            SELECT Channel_Used AS Category,
            AVG(ROI) AS Value
            FROM campaigns
            GROUP BY Channel_Used
            ORDER BY Value DESC
            """
            preferred_chart = "Pie"

        use_gemini = st.session_state.get("use_gemini", False)
        if use_gemini and st.session_state.get("gemini_api_key"):
            try:
                if not sql_query:
                    sql_query = gemini_generate_sql(
                        question,
                        data,
                        st.session_state.gemini_api_key,
                        st.session_state.gemini_model,
                    )
                    if sql_query:
                        engine_used = "Gemini"
            except RuntimeError:
                st.warning("Gemini request failed; using rule-based queries.")

        if not sql_query and "revenue" in q and "campaign" in q:

            sql_query = """
            SELECT Campaign_Type AS Category,
            SUM(Revenue) AS Value
            FROM campaigns
            GROUP BY Campaign_Type
            ORDER BY Value DESC
            """

        elif not sql_query and "roi" in q:

            sql_query = """
            SELECT Channel_Used AS Category,
            AVG(ROI) AS Value
            FROM campaigns
            GROUP BY Channel_Used
            ORDER BY Value DESC
            """
            preferred_chart = "Pie"

        elif not sql_query and "clicks" in q and "impressions" in q:

            sql_query = """
            SELECT Channel_Used,
            SUM(Impressions) AS Impressions,
            SUM(Clicks) AS Clicks
            FROM campaigns
            GROUP BY Channel_Used
            """

        if not sql_query:
            sql_query = build_fallback_sql(data)
            engine_used = "Auto-summary"

        loader.empty()
        st.markdown('<div id="sql-query"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Generated SQL Query</div>', unsafe_allow_html=True)
        st.caption(f"Query engine: {engine_used}")
        st.code(sql_query, language="sql")

        try:
            result = run_sql_query(sql_query, data_sig)
        except Exception:
            fallback_query = build_fallback_sql(data)
            if fallback_query != sql_query:
                sql_query = fallback_query
                engine_used = "Auto-summary"
                st.caption("Adjusted to a compatible query for this dataset.")
                result = run_sql_query(sql_query, data_sig)
            else:
                st.error("Unable to generate a dashboard for the current dataset.")
                st.stop()

        st.markdown('<div class="section-title">Query Result</div>', unsafe_allow_html=True)
        st.dataframe(result, use_container_width=True)

        # -------------------------
        # VISUALIZATION
        # -------------------------

        dashboard_header = st.container()
        toolbar_left, toolbar_right = st.columns([2.3, 1.7])

        working = result.copy()
        numeric_cols = working.select_dtypes(include="number").columns.tolist()
        non_numeric_cols = [c for c in working.columns if c not in numeric_cols]
        time_col = None

        for col in non_numeric_cols:
            col_lower = col.lower()
            if any(token in col_lower for token in ["date", "month", "week", "day"]):
                parsed = pd.to_datetime(working[col], errors="coerce")
                if parsed.notna().mean() > 0.6:
                    working[col] = parsed
                    time_col = col
                    break

        if not time_col:
            for col in non_numeric_cols:
                parsed = pd.to_datetime(working[col], errors="coerce")
                if parsed.notna().mean() > 0.6:
                    working[col] = parsed
                    time_col = col
                    break

        def build_chart_options():
            options = ["Auto"]
            if len(numeric_cols) >= 1:
                options.append("Bar")
            if len(non_numeric_cols) >= 1 and len(numeric_cols) >= 2:
                options.append("Grouped Bar")
            if (time_col and numeric_cols) or (len(non_numeric_cols) >= 1 and len(numeric_cols) >= 1):
                options.append("Line")
                options.append("Area")
            if len(non_numeric_cols) >= 1 and len(numeric_cols) >= 1:
                options.append("Pie")
            if ("Impressions" in working.columns and "Clicks" in working.columns) or len(numeric_cols) >= 2:
                options.append("Scatter")
            if len(numeric_cols) >= 2:
                options.append("Heatmap")
            return options

        chart_options = build_chart_options()
        initial_pref_warning = None
        current_pref = st.session_state.get("chart_pref", "Auto")
        if current_pref not in chart_options:
            initial_pref_warning = f"{current_pref} chart isn't available for this result. Using Auto."
            st.session_state.chart_pref = "Auto"

        with toolbar_left:
            chart_label_slot = st.empty()
            chart_warning_slot = st.empty()
            chart_pref = st.selectbox(
                "Chart type",
                chart_options,
                index=chart_options.index(st.session_state.get("chart_pref", "Auto")),
                help="Override the auto-selected chart type",
                key="chart_pref",
            )

        try:
            def df_fingerprint(df):
                sample = df.head(800)
                hashed = pd.util.hash_pandas_object(sample, index=True)
                digest = hashlib.md5()
                digest.update(str(df.shape).encode("utf-8"))
                digest.update("|".join(map(str, df.columns)).encode("utf-8"))
                digest.update(hashed.values.tobytes())
                return digest.hexdigest()

            chart_placeholder = st.empty()
            loader_html = """
<div class="glass-card loader-card chart-buffer">
  <div class="loader-title">Creating chart</div>
  <div class="loader-sub">Rendering the new visualization...</div>
  <div class="loader-bars">
    <span></span>
    <span></span>
    <span></span>
  </div>
</div>
"""
            chart_type = "Bar"

            result_sig = df_fingerprint(result)
            chart_signature = hashlib.md5(
                f"{question}|{chart_pref}|{result_sig}|{plotly_template}".encode("utf-8")
            ).hexdigest()
            chart_changed = (
                chart_signature != st.session_state.last_chart_signature
                or chart_pref != st.session_state.last_chart_pref
            )
            if chart_changed:
                chart_placeholder.markdown(loader_html, unsafe_allow_html=True)

            def build_auto_chart():
                if (
                    preferred_chart == "Pie"
                    and len(non_numeric_cols) == 1
                    and len(numeric_cols) == 1
                    and len(working) <= 10
                ):
                    return (
                        px.pie(
                            working,
                            names=non_numeric_cols[0],
                            values=numeric_cols[0],
                            hole=0.45,
                        ),
                        "Pie",
                    )
                if "Impressions" in working.columns and "Clicks" in working.columns:
                    label_col = "Channel_Used" if "Channel_Used" in working.columns else None
                    return (
                        px.scatter(
                            working,
                            x="Impressions",
                            y="Clicks",
                            size="Clicks",
                            color=label_col,
                            hover_name=label_col,
                            custom_data=[label_col] if label_col else None,
                            render_mode="webgl",
                        ),
                        "Scatter",
                    )

                if time_col and numeric_cols:
                    sorted_working = working.sort_values(time_col)
                    return (
                        px.line(
                            sorted_working,
                            x=time_col,
                            y=numeric_cols[0],
                            markers=True,
                        ),
                        "Line",
                    )

                if len(non_numeric_cols) >= 1 and len(numeric_cols) >= 2:
                    value_cols = numeric_cols[:2]
                    return (
                        px.bar(
                            working,
                            x=non_numeric_cols[0],
                            y=value_cols,
                            barmode="group",
                        ),
                        "Grouped Bar",
                    )

                if len(non_numeric_cols) == 1 and len(numeric_cols) == 1:
                    if any(key in q for key in ["share", "distribution", "breakdown", "composition", "split"]) or len(working) <= 8:
                        return (
                            px.pie(
                                working,
                                names=non_numeric_cols[0],
                                values=numeric_cols[0],
                                hole=0.45,
                            ),
                            "Pie",
                        )
                    return (
                        px.bar(
                            working,
                            x=non_numeric_cols[0],
                            y=numeric_cols[0],
                        ),
                        "Bar",
                    )

                if len(numeric_cols) >= 1:
                    return px.bar(working, x=working.index, y=numeric_cols[0]), "Bar"

                return px.bar(working), "Bar"

            cached_chart = st.session_state.chart_cache.get(chart_signature)
            if cached_chart:
                fig = cached_chart["fig"]
                chart_type = cached_chart["chart_type"]
                override_failed = cached_chart["override_failed"]
            else:
                fig, chart_type = build_auto_chart()
                override_failed = False

                if chart_pref != "Auto":
                    fig_override = None
                    override_type = chart_pref

                    if chart_pref == "Scatter":
                        if "Impressions" in working.columns and "Clicks" in working.columns:
                            label_col = "Channel_Used" if "Channel_Used" in working.columns else None
                            fig_override = px.scatter(
                                working,
                                x="Impressions",
                                y="Clicks",
                                size="Clicks",
                                color=label_col,
                                hover_name=label_col,
                                custom_data=[label_col] if label_col else None,
                                render_mode="webgl",
                            )
                        elif len(numeric_cols) >= 2:
                            label_col = non_numeric_cols[0] if non_numeric_cols else None
                            fig_override = px.scatter(
                                working,
                                x=numeric_cols[0],
                                y=numeric_cols[1],
                                color=label_col,
                                hover_name=label_col,
                                custom_data=[label_col] if label_col else None,
                                render_mode="webgl",
                            )

                    elif chart_pref == "Line":
                        if time_col and numeric_cols:
                            sorted_working = working.sort_values(time_col)
                            fig_override = px.line(
                                sorted_working,
                                x=time_col,
                                y=numeric_cols[0],
                                markers=True,
                            )
                        elif len(non_numeric_cols) >= 1 and len(numeric_cols) >= 1:
                            fig_override = px.line(
                                working,
                                x=non_numeric_cols[0],
                                y=numeric_cols[0],
                                markers=True,
                            )

                    elif chart_pref == "Area":
                        if time_col and numeric_cols:
                            sorted_working = working.sort_values(time_col)
                            fig_override = px.area(
                                sorted_working,
                                x=time_col,
                                y=numeric_cols[0],
                            )
                        elif len(non_numeric_cols) >= 1 and len(numeric_cols) >= 1:
                            fig_override = px.area(
                                working,
                                x=non_numeric_cols[0],
                                y=numeric_cols[0],
                            )

                    elif chart_pref == "Pie":
                        if len(non_numeric_cols) >= 1 and len(numeric_cols) >= 1:
                            fig_override = px.pie(
                                working,
                                names=non_numeric_cols[0],
                                values=numeric_cols[0],
                                hole=0.45,
                            )

                    elif chart_pref == "Grouped Bar":
                        if len(non_numeric_cols) >= 1 and len(numeric_cols) >= 2:
                            fig_override = px.bar(
                                working,
                                x=non_numeric_cols[0],
                                y=numeric_cols[:2],
                                barmode="group",
                            )

                    elif chart_pref == "Bar":
                        if len(non_numeric_cols) >= 1 and len(numeric_cols) >= 1:
                            fig_override = px.bar(
                                working,
                                x=non_numeric_cols[0],
                                y=numeric_cols[0],
                            )
                        elif len(numeric_cols) >= 1:
                            fig_override = px.bar(working, x=working.index, y=numeric_cols[0])

                    elif chart_pref == "Heatmap":
                        if len(numeric_cols) >= 2:
                            corr = working[numeric_cols].corr(numeric_only=True)
                            fig_override = px.imshow(
                                corr,
                                text_auto=".2f",
                                color_continuous_scale="Blues",
                            )

                    if fig_override is not None:
                        fig = fig_override
                        chart_type = override_type
                    else:
                        override_failed = True

                base_height = 520
                transition_duration = 0
                fig.update_layout(
                    template=plotly_template,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color=text,
                    margin=dict(l=10, r=10, t=30, b=10),
                    hoverlabel=dict(bgcolor=hover_bg, font_size=12, font=dict(color=text), align="left"),
                    colorway=plotly_colors,
                    legend_title_text="",
                    height=base_height,
                    transition=dict(duration=transition_duration, easing="cubic-in-out"),
                )

                if chart_type == "Pie":
                    fig.update_traces(
                        textinfo="percent+label",
                        textposition="inside",
                        insidetextorientation="radial",
                        sort=False,
                        hovertemplate="%{label}<br>%{value:,.0f} (%{percent})<extra></extra>",
                    )
                    fig.update_layout(
                        legend=dict(
                            orientation="v",
                            yanchor="middle",
                            y=0.5,
                            xanchor="left",
                            x=0.9,
                            font=dict(size=14),
                            itemwidth=40,
                        ),
                        margin=dict(l=10, r=90, t=30, b=10),
                        height=560,
                        hovermode="closest",
                    )
                    fig.update_traces(
                        domain=dict(x=[0.06, 0.86], y=[0.08, 0.92]),
                        textfont=dict(size=14),
                    )
                elif chart_type in ("Line", "Area"):
                    fig.update_traces(line=dict(width=3))
                    fig.update_layout(hovermode="x unified")
                elif chart_type == "Heatmap":
                    fig.update_layout(hovermode="closest")
                else:
                    fig.update_traces(marker=dict(line=dict(width=0)))
                    fig.update_layout(hovermode="closest")

                if chart_type == "Scatter":
                    x_title = fig.layout.xaxis.title.text or "X"
                    y_title = fig.layout.yaxis.title.text or "Y"
                    label_name = None
                    if "Channel_Used" in working.columns:
                        label_name = "Channel"
                    elif non_numeric_cols:
                        label_name = non_numeric_cols[0]
                    name_prefix = f"{label_name}: %{{customdata[0]}}<br>" if label_name else ""
                    fig.update_traces(
                        hovertemplate=f"{name_prefix}{x_title}: %{{x:,.0f}}<br>{y_title}: %{{y:,.0f}}<extra></extra>"
                    )

                st.session_state.chart_cache[chart_signature] = {
                    "fig": fig,
                    "chart_type": chart_type,
                    "override_failed": override_failed,
                }

            label = "Auto-selected" if chart_pref == "Auto" or override_failed else "Selected"

            dashboard_title = f"Nykaa AI BI Dashboard • {question}"
            export_png = None
            export_pdf = None
            export_error = None
            try:
                export_png, export_pdf, export_error = get_export_assets(
                    fig,
                    kpis,
                    dashboard_title,
                    plotly_template,
                    plotly_colors,
                    text,
                    chart_type,
                    signature=chart_signature,
                )
            except Exception:
                export_png, export_pdf, export_error = None, None, "Export temporarily unavailable."

            with dashboard_header:
                st.markdown('<div id="dashboard"></div>', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Dashboard</div>', unsafe_allow_html=True)

            with toolbar_left:
                chart_label_slot.markdown(
                    f'<div class="chart-chip">{label}: {chart_type} chart</div>',
                    unsafe_allow_html=True,
                )
                if override_failed:
                    chart_warning_slot.warning(
                        "Selected chart type isn't suitable for this result. Using auto selection."
                    )
                elif initial_pref_warning:
                    chart_warning_slot.info(initial_pref_warning)
                else:
                    chart_warning_slot.empty()

            with toolbar_right:
                export_cols = st.columns(2)
                export_cols[0].download_button(
                    "Export as PDF",
                    data=export_pdf or b"",
                    file_name="nykaa_dashboard.pdf",
                    mime="application/pdf",
                    disabled=export_pdf is None,
                    use_container_width=True,
                )
                export_cols[1].download_button(
                    "Export as PNG",
                    data=export_png or b"",
                    file_name="nykaa_dashboard.png",
                    mime="image/png",
                    disabled=export_png is None,
                    use_container_width=True,
                )
                if export_error:
                    st.caption(export_error)

            chart_placeholder.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.session_state.last_chart_signature = chart_signature
            st.session_state.last_chart_pref = chart_pref

            explain_clicked = st.button(
                "Explain this Chart",
                key=f"explain_{chart_signature}",
                use_container_width=True,
            )

            if explain_clicked:
                with st.spinner("Explaining chart..."):
                    explanation = build_chart_explanation(
                        question,
                        working,
                        chart_type,
                        time_col=time_col,
                        api_key=st.session_state.get("gemini_api_key") if st.session_state.get("use_gemini") else None,
                        model_name=st.session_state.get("gemini_model"),
                    )
                    st.session_state.chart_explanations[chart_signature] = explanation

            explanation = st.session_state.chart_explanations.get(chart_signature)
            with st.expander("Chart Explanation", expanded=bool(explanation)):
                if explanation:
                    sentence = (
                        f"This chart shows {brief_text(explanation.get('what', '')).rstrip('.')}."
                        f" It highlights {brief_text(explanation.get('trend', '')).rstrip('.')}."
                        f" It suggests {brief_text(explanation.get('insight', '')).rstrip('.')}."
                    )
                    st.markdown(
                        f"""
<div class="explain-card">
  {html.escape(sentence)}
</div>
""",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        '<div class="explain-card">Click <strong>Explain this Chart</strong> to generate a CXO-ready summary.</div>',
                        unsafe_allow_html=True,
                    )

        except:
            st.warning("Could not create chart")

        # -------------------------
        # INSIGHT
        # -------------------------

        st.markdown('<div class="section-title">Insight Summary</div>', unsafe_allow_html=True)

        if len(result) > 0:

            if result.shape[1] >= 2:
                top = result.iloc[0, 0]
                val = result.iloc[0, 1]
                insight_title = "Top Performer Highlight"
                insight_text = f"{top} is the top performer with value {val}."
            else:
                col_name = result.columns[0]
                val = result.iloc[0, 0]
                insight_title = "Result Highlight"
                insight_text = f"{col_name} value is {val}."

            val_num = pd.to_numeric(val, errors="coerce")
            if pd.notna(val_num):
                val_text = f"{val_num:,.2f}"
            else:
                val_text = str(val)

            insight_text = insight_text.replace(str(val), val_text)

            st.markdown(
                f"""
<div class="glass-card insight-card">
  <div class="insight-icon">NX</div>
  <div>
    <div class="insight-title">{insight_title}</div>
    <div class="insight-text">{insight_text}</div>
  </div>
</div>
""",
                unsafe_allow_html=True,
            )

        # -------------------------
        # SMART RECOMMENDATIONS
        # -------------------------

        st.markdown('<div class="section-title">Smart Recommendations</div>', unsafe_allow_html=True)
        recommendations = []
        if len(result) > 0:
            rec_signature = hashlib.md5(
                (question + result.head(15).to_csv(index=False)).encode("utf-8")
            ).hexdigest()
            recommendations = st.session_state.recommendation_cache.get(rec_signature)
            if not recommendations:
                use_gemini = st.session_state.get("use_gemini", False)
                if use_gemini and st.session_state.get("gemini_api_key"):
                    with st.spinner("Generating recommendations..."):
                        recommendations = build_smart_recommendations(
                            question,
                            result,
                            api_key=st.session_state.get("gemini_api_key"),
                            model_name=st.session_state.get("gemini_model"),
                        )
                else:
                    recommendations = build_smart_recommendations(question, result)
                st.session_state.recommendation_cache[rec_signature] = recommendations

        if recommendations:
            rec_items = []
            for rec in recommendations:
                impact = str(rec.get("impact", "Medium")).title()
                impact_class = {
                    "High": "impact-high",
                    "Medium": "impact-medium",
                    "Low": "impact-low",
                }.get(impact, "impact-medium")
                rec_items.append(
                    f"""
  <div class="recommendation-item">
    <div>
      <div class="recommendation-summary">{html.escape(rec.get("summary", ""))}</div>
      <div class="recommendation-action">{html.escape(rec.get("action", ""))}</div>
    </div>
    <div class="impact-pill {impact_class}">{impact} Impact</div>
  </div>
                    """
                )
            st.markdown(
                f"""
<div class="glass-card recommendations-card">
  <div class="recommendations-title">AI Business Recommendations</div>
  {''.join(rec_items)}
</div>
""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
<div class="glass-card recommendations-card">
  <div class="recommendations-title">AI Business Recommendations</div>
  <div class="recommendation-action">Run a query with data to receive tailored recommendations.</div>
</div>
""",
                unsafe_allow_html=True,
            )


# -------------------------
# FOOTER
# -------------------------

st.markdown(
    """
<div class="footer">
  Nykaa Digital Marketing • Conversational BI Prototype
</div>
""",
    unsafe_allow_html=True,
)
