"""
抖音短视频数据智能分析平台
Python课程大作业 - 任务2：Python数据分析
"""
import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import streamlit as st
import pandas as pd
import numpy as np
import warnings

# 屏蔽 st.components.v1.html 的弃用警告（2026-06-01后弃用，但 data-uri iframe 会禁用 JS）
warnings.filterwarnings("ignore", message="Please replace.*components.*")
import streamlit.components.v1 as components

# PyEcharts
from pyecharts.charts import Bar, Scatter
from pyecharts import options as opts

from src.data_loader import load_data_v3 as load_data, engineer_features, get_data_summary
from src.user_analysis import (
    user_city_distribution, user_interaction_analysis,
    user_active_hours, user_finish_vs_like,
    user_top_active, user_weekday_activity,
)
from src.author_analysis import (
    author_production_ranking, author_performance_scatter,
    author_duration_analysis, author_top_by_completion,
    author_channel_distribution,
)
from src.content_analysis import (
    duration_vs_completion, duration_distribution,
    music_top_usage, item_city_distribution,
    like_vs_finish_heatmap, recommend_best_duration,
)
from src.insights import (
    best_publish_time, best_duration_analysis,
    channel_performance, correlation_analysis,
    user_portrait_summary,
)
from src import data_loader

# =========================================================
# 莫兰迪色调色板
# =========================================================
MORANDI_COLORS = [
    "#7D8B9A",  # 灰蓝
    "#C4A4A4",  # dusty rose
    "#8FAE9B",  # 鼠尾草绿
    "#B8A99A",  # 灰褐
    "#D4C5A9",  # 陶土色
    "#A8B8C8",  # 淡灰蓝
    "#C8B8B8",  # 淡粉灰
    "#B0C4B0",  # 淡灰绿
]

MORANDI = {
    "bg": "#F5F0EB",           # 暖白米色背景
    "card_bg": "#EDE7E0",      # 浅米色卡片
    "card_bg2": "#E8E3DD",     # 稍深米色
    "primary": "#7D8B9A",      # 灰蓝（主色）
    "primary_dark": "#5D6B7A", # 深灰蓝
    "rose": "#C4A4A4",         #  dusty rose
    "sage": "#8FAE9B",         # 鼠尾草绿
    "taupe": "#B8A99A",        # 灰褐
    "clay": "#D4C5A9",         # 陶土色
    "text": "#4A4A4A",         # 柔和黑
    "text_light": "#7A7A7A",   # 浅灰
    "border": "#D6CFC6",       # 边框色
    "highlight_bg": "#F0EBE3", # 高亮背景
    "success_bg": "#E6EDE5",   # 成功背景（偏绿）
    "white": "#FFFFFF",
}

# ========== 页面配置 ==========
st.set_page_config(
    page_title="抖音短视频数据智能分析平台 | Python课程大作业",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ========== 莫兰迪 CSS 样式 ==========
st.markdown(f"""
<style>
    /* 全局 */
    .stApp {{
        background-color: {MORANDI["bg"]};
    }}
    .main-header {{
        font-size: 2.2rem;
        font-weight: 700;
        color: {MORANDI["primary_dark"]};
        padding: 1rem 0 0.5rem 0;
        margin-bottom: 1.2rem;
        letter-spacing: 0.5px;
    }}
    .main-header small {{
        font-weight: 400;
        font-size: 1rem;
        color: {MORANDI["text_light"]};
    }}
    /* 要求大标题 */
    .req-header {{
        font-size: 1.5rem;
        font-weight: 600;
        color: {MORANDI["white"]};
        background: linear-gradient(135deg, {MORANDI["primary"]}, {MORANDI["primary_dark"]});
        padding: 0.8rem 1.2rem;
        border-radius: 10px;
        margin: 1rem 0 0.8rem 0;
        letter-spacing: 0.3px;
    }}
    .req-header small {{
        font-weight: 400;
        font-size: 0.85rem;
        opacity: 0.85;
    }}
    .req-sub {{
        font-size: 1.1rem;
        font-weight: 600;
        color: {MORANDI["primary_dark"]};
        padding: 0.4rem 0 0.4rem 0.8rem;
        border-left: 4px solid {MORANDI["rose"]};
        margin: 1.2rem 0 0.8rem 0;
    }}
    .sub-header {{
        font-size: 1.3rem;
        font-weight: 600;
        color: {MORANDI["primary_dark"]};
        padding: 0.4rem 0;
        margin: 0.5rem 0;
    }}
    /* 指标卡片 */
    .metric-card {{
        background: linear-gradient(135deg, {MORANDI["primary"]}, {MORANDI["primary_dark"]});
        border-radius: 12px;
        padding: 1.2rem 0.8rem;
        color: white;
        text-align: center;
        box-shadow: 0 3px 8px rgba(0,0,0,0.06);
    }}
    .metric-card .metric-value {{
        font-size: 1.8rem;
        font-weight: 700;
        line-height: 1.2;
    }}
    .metric-card .metric-label {{
        font-size: 0.85rem;
        opacity: 0.85;
        margin-top: 0.2rem;
    }}
    .metric-card-rose {{
        background: linear-gradient(135deg, {MORANDI["rose"]}, #D4B8B8) !important;
    }}
    .metric-card-sage {{
        background: linear-gradient(135deg, {MORANDI["sage"]}, #A8C4B4) !important;
    }}
    .metric-card-taupe {{
        background: linear-gradient(135deg, {MORANDI["taupe"]}, #C8BCB0) !important;
    }}
    .metric-card-clay {{
        background: linear-gradient(135deg, {MORANDI["clay"]}, #DECCB8) !important;
    }}
    /* 高亮框 */
    .highlight-box {{
        background: {MORANDI["highlight_bg"]};
        border-left: 4px solid {MORANDI["rose"]};
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
        color: {MORANDI["text"]};
    }}
    .insight-box {{
        background: {MORANDI["card_bg"]};
        border-left: 4px solid {MORANDI["primary"]};
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: {MORANDI["text"]};
    }}
    .success-box {{
        background: {MORANDI["success_bg"]};
        border-left: 4px solid {MORANDI["sage"]};
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: {MORANDI["text"]};
    }}
    /* 侧边栏 */
    .css-1d391kg, .css-163ttbj, section[data-testid="stSidebar"] > div {{
        background-color: {MORANDI["card_bg"]} !important;
    }}
    .sidebar .sidebar-content {{
        background-color: {MORANDI["card_bg"]};
    }}
    /* 数据表格 */
    .stDataFrame {{
        border: 1px solid {MORANDI["border"]};
        border-radius: 8px;
    }}
    /* tab 样式 */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0;
        background-color: {MORANDI["card_bg"]};
        border-radius: 8px 8px 0 0;
        padding: 0.2rem 0.2rem 0 0.2rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 6px 6px 0 0;
        padding: 0.4rem 1rem;
        font-size: 0.9rem;
        color: {MORANDI["text_light"]};
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {MORANDI["white"]} !important;
        color: {MORANDI["primary_dark"]} !important;
        font-weight: 600;
    }}
    /* expender */
    .streamlit-expanderHeader {{
        background-color: {MORANDI["card_bg"]};
        border-radius: 8px;
    }}
    /* metric */
    .stMetric label {{
        color: {MORANDI["text_light"]} !important;
    }}
    .stMetric .value {{
        color: {MORANDI["primary_dark"]} !important;
    }}
    footer {{
        display: none;
    }}
    /* selectbox, slider */
    .stSelectbox label, .stSlider label {{
        color: {MORANDI["text"]} !important;
        font-weight: 500;
    }}
    div.stSlider > div[data-baseweb="slider"] > div > div {{
        background-color: {MORANDI["primary"]} !important;
    }}
</style>
""", unsafe_allow_html=True)


# ========== 数据加载 ==========
@st.cache_data(show_spinner="正在加载数据... 173万行，请稍候 ⏳")
def load_and_process_v3():
    df = load_data()
    df = engineer_features(df)
    return df

try:
    df = load_and_process_v3()
    summary = get_data_summary(df)
except Exception as e:
    st.error(f"数据加载失败: {e}")
    st.info("请确认数据文件路径正确")
    st.stop()


# ========== 侧边栏 ==========
st.sidebar.markdown(
    f"<h3 style='color:{MORANDI['primary_dark']}; margin-bottom:0.2rem;'>📊 导航面板</h3>",
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    f"<p style='color:{MORANDI['text_light']}; font-size:0.85rem; margin-top:0;'>"
    f"抖音短视频数据智能分析平台</p>",
    unsafe_allow_html=True,
)

nav_options = [
    "🏠 数据总览",
    "📋 要求1-用户分析",
    "📋 要求2-作者分析",
    "📋 要求3-作品分析",
    "💡 智能洞察(拓展)",
]
selected_page = st.sidebar.radio("选择分析模块", nav_options, label_visibility="collapsed")

st.sidebar.markdown(f"<hr style='border-color:{MORANDI['border']};'>", unsafe_allow_html=True)
st.sidebar.markdown("### ⚙️ 数据筛选")

all_channels = sorted(df['channel'].unique().tolist())
channel_map = {0: '推荐页', 1: '关注页', 2: '搜索页', 3: '个人主页'}
channel_labels = [f"{c} - {channel_map.get(c, '未知')}" for c in all_channels]
selected_channels = st.sidebar.multiselect("分发渠道", options=channel_labels, default=channel_labels)
selected_channel_nums = [int(c.split(" - ")[0]) for c in selected_channels]

date_min = df['date'].min().date()
date_max = df['date'].max().date()
date_range = st.sidebar.date_input(
    "日期范围", value=(date_min, date_max), min_value=date_min, max_value=date_max)

dur_min = int(df['duration_time'].min())
dur_max = int(df['duration_time'].max())
dur_range = st.sidebar.slider("视频时长范围(秒)", min_value=dur_min, max_value=dur_max, value=(dur_min, dur_max))

df_filtered = df[
    (df['channel'].isin(selected_channel_nums)) &
    (df['date'] >= pd.Timestamp(date_range[0])) &
    (df['date'] <= pd.Timestamp(date_range[1])) &
    (df['duration_time'] >= dur_range[0]) &
    (df['duration_time'] <= dur_range[1])
]

st.sidebar.markdown(f"**当前筛选**: {len(df_filtered):,} 条 / {len(df_filtered)/len(df)*100:.1f}%")
st.sidebar.markdown(f"<hr style='border-color:{MORANDI['border']};'>", unsafe_allow_html=True)
st.sidebar.markdown(
    f"<p style='color:{MORANDI['text_light']}; font-size:0.75rem; text-align:center;'>"
    f"抖音短视频数据智能分析平台 v2.0</p>",
    unsafe_allow_html=True,
)


# ========== 图表渲染 ==========
def render_chart(chart, height: str = "500px"):
    """渲染 PyEcharts 图表到 Streamlit
    使用 components.html（data-uri iframe 会禁用 JS，导致图表空白）
    """
    # 统一修复：将所有多系列图表的图例移到底部，避免与标题重叠
    if hasattr(chart, 'options'):
        series = chart.options.get('series', [])
        if isinstance(series, list) and len(series) > 1:
            names = [s.get('name') for s in series if s.get('name')]
            if names:
                old_legend = chart.options.get('legend', {})
                if isinstance(old_legend, list) and len(old_legend) > 0:
                    old_legend = old_legend[0] if isinstance(old_legend[0], dict) else {}
                elif not isinstance(old_legend, dict):
                    old_legend = {}
                chart.options['legend'] = {'bottom': 5, 'data': names,
                                           'textStyle': old_legend.get('textStyle')}
                chart.options['grid'] = [{'containLabel': True, 'bottom': '8%'}]
    chart_html = chart.render_embed()
    # 多系列图表底部有图例，需要额外高度
    series_count = len(chart.options.get('series', [])) if hasattr(chart, 'options') else 0
    extra = 80 if series_count > 1 else 20
    components.html(chart_html, height=int(height.replace('px', '')) + extra)


# =========================================================
# 页面 0: 数据总览
# =========================================================
if selected_page == "🏠 数据总览":
    st.markdown('<div class="main-header">🎯 数据总览 <small>抖音短视频数据智能分析平台</small></div>', unsafe_allow_html=True)

    # 核心指标行
    st.markdown('<div class="req-sub">📊 核心数据指标</div>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{summary["总记录数"]}</div><div class="metric-label">总记录数</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{summary["用户数"]}</div><div class="metric-label">活跃用户</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card metric-card-rose"><div class="metric-value">{summary["作者数"]}</div><div class="metric-label">内容创作者</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card metric-card-sage"><div class="metric-value">{summary["作品数"]}</div><div class="metric-label">短视频作品</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{summary["平均完播率"]}</div><div class="metric-label">平均完播率</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:0.8rem'></div>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card metric-card-rose"><div class="metric-value">{summary["平均点赞率"]}</div><div class="metric-label">平均点赞率</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card metric-card-sage"><div class="metric-value">{summary["平均时长"]}</div><div class="metric-label">平均视频时长</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card metric-card-taupe"><div class="metric-value">{summary["覆盖城市(用户)"]}</div><div class="metric-label">用户覆盖城市</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card metric-card-clay"><div class="metric-value">{summary["日期范围"]}</div><div class="metric-label">数据时间跨度</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="req-sub">📈 数据概览</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        chart = user_active_hours(df_filtered)
        render_chart(chart, "450px")
    with col2:
        chart = duration_distribution(df_filtered)
        render_chart(chart, "450px")

    col1, col2 = st.columns(2)
    with col1:
        chart = like_vs_finish_heatmap(df_filtered)
        render_chart(chart, "400px")
    with col2:
        chart = user_weekday_activity(df_filtered)
        render_chart(chart, "400px")

    with st.expander("📋 数据说明与字段解释"):
        st.markdown("""
        - **数据来源**: 抖音短视频平台脱敏数据
        - **时间范围**: 2019年9月21日 - 10月30日
        - **数据量**: 约170万条用户观看行为记录
        - **字段说明**:
            - `uid`: 用户ID（脱敏） | `user_city`: 用户所在城市（编码）
            - `item_id`: 作品ID（脱敏） | `author_id`: 作者ID（脱敏）
            - `item_city`: 作品发布城市（编码） | `channel`: 分发渠道
            - `finish`: 是否观看完成（0/1） | `like`: 是否点赞（0/1）
            - `music_id`: 背景音乐ID | `duration_time`: 视频时长（秒）
        """)


# =========================================================
# 页面 1: 用户数据可视化分析（要求1）
# =========================================================
elif selected_page == "📋 要求1-用户分析":
    st.markdown("""
    <div class="req-header">
    📋 要求1 — 用户数据可视化分析 <small>用户浏览量 / 点赞量 / 观看完整数 / 观看作品城市数</small>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "👁 用户浏览量分析",
        "❤️ 点赞量分析",
        "✅ 观看完整数分析",
        "🌍 观看作品城市数分析",
    ])

    # ---- Tab1: 用户浏览量 ----
    with tab1:
        st.markdown("""
        <div class="highlight-box">
        <strong>📌 要求1-用户指标①：用户浏览量</strong><br>
        分析用户的浏览/观看行为，包括整体浏览量分布、时段规律、高频用户排行。
        </div>
        """, unsafe_allow_html=True)

        total_views = len(df_filtered)
        avg_views_per_user = total_views / max(df_filtered['uid'].nunique(), 1)
        peak_hour = int(df_filtered.groupby('H')['item_id'].count().idxmax())
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总浏览量", f"{total_views:,}")
        with col2:
            st.metric("人均浏览量", f"{avg_views_per_user:.1f} 次")
        with col3:
            st.metric("浏览高峰时段", f"{peak_hour}:00-{peak_hour+1}:00")

        st.markdown('<div class="req-sub">👁 用户浏览时段分布</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            chart = user_active_hours(df_filtered)
            render_chart(chart, "450px")
        with col2:
            chart = user_weekday_activity(df_filtered)
            render_chart(chart, "400px")

        st.markdown('<div class="req-sub">🏆 浏览最多的活跃用户 Top30</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 2])
        with col1:
            chart = user_top_active(df_filtered)
            render_chart(chart, "450px")
        with col2:
            st.markdown('<div class="insight-box"><strong>💡 分析结论</strong><br>', unsafe_allow_html=True)
            top_user_views = df_filtered['uid'].value_counts()
            st.markdown(f"Top1用户浏览了 **{top_user_views.iloc[0]:,}** 次")
            st.markdown(f"Top5平均浏览 **{top_user_views.head(5).mean():.0f}** 次/人")
            top10_ratio = top_user_views.head(10).sum() / total_views * 100
            st.markdown(f"Top10用户贡献了 **{top10_ratio:.1f}%** 的总浏览量")
            st.markdown("</div>", unsafe_allow_html=True)

    # ---- Tab2: 点赞量 ----
    with tab2:
        st.markdown("""
        <div class="highlight-box">
        <strong>📌 要求1-用户指标②：点赞量</strong><br>
        分析用户的点赞行为，包括整体点赞率、不同维度下的点赞分布。
        </div>
        """, unsafe_allow_html=True)

        total_likes = int(df_filtered['like'].sum())
        like_rate = df_filtered['like'].mean() * 100
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总点赞量", f"{total_likes:,}")
        with col2:
            st.metric("平均点赞率", f"{like_rate:.2f}%")
        with col3:
            avg_likes_per_user = total_likes / max(df_filtered['uid'].nunique(), 1)
            st.metric("人均点赞数", f"{avg_likes_per_user:.2f}")

        st.markdown('<div class="req-sub">❤️ 点赞率在不同维度的对比</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            like_by_duration = df_filtered.groupby('duration_group', observed=False)['like'].mean() * 100
            bar = Bar(init_opts=opts.InitOpts(width='100%', height='400px'))
            bar.add_xaxis(like_by_duration.index.astype(str).tolist())
            bar.add_yaxis('点赞率(%)', like_by_duration.values.round(2).tolist())
            bar.set_global_opts(
                title_opts=opts.TitleOpts(title='不同视频时长的点赞率',
                    title_textstyle_opts=opts.TextStyleOpts(color=MORANDI['primary_dark'], font_size=14)),
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
                yaxis_opts=opts.AxisOpts(name='点赞率(%)'),
                toolbox_opts=opts.ToolboxOpts(),
            )
            # 应用莫兰迪色
            bar.set_colors([MORANDI['rose'], MORANDI['sage'], MORANDI['taupe']])
            render_chart(bar, "400px")

        with col2:
            like_by_period = df_filtered.groupby('time_period')['like'].mean() * 100
            periods_order = ['凌晨(0-6点)', '早晨(6-9点)', '上午(9-12点)', '中午(12-14点)',
                           '下午(14-18点)', '傍晚(18-21点)', '夜间(21-24点)']
            like_by_period = like_by_period.reindex([p for p in periods_order if p in like_by_period.index]).fillna(0)
            bar2 = Bar(init_opts=opts.InitOpts(width='100%', height='400px'))
            bar2.add_xaxis(like_by_period.index.tolist())
            bar2.add_yaxis('点赞率(%)', like_by_period.values.round(2).tolist())
            bar2.set_global_opts(
                title_opts=opts.TitleOpts(title='不同时段的点赞率',
                    title_textstyle_opts=opts.TextStyleOpts(color=MORANDI['primary_dark'], font_size=14)),
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=30)),
                yaxis_opts=opts.AxisOpts(name='点赞率(%)'),
                toolbox_opts=opts.ToolboxOpts(),
            )
            bar2.set_colors([MORANDI['sage']])
            render_chart(bar2, "400px")

        st.markdown('<div class="req-sub">完播与点赞的交叉分析</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            chart = like_vs_finish_heatmap(df_filtered)
            render_chart(chart, "400px")
        with col2:
            st.markdown('<div class="insight-box"><strong>💡 分析结论</strong><br>', unsafe_allow_html=True)
            st.markdown(f"- 总体点赞率: **{like_rate:.2f}%**")
            finish_like_rate = df_filtered[df_filtered['finish'] == 1]['like'].mean() * 100
            not_finish_like_rate = df_filtered[df_filtered['finish'] == 0]['like'].mean() * 100
            st.markdown(f"- 看完用户点赞率: **{finish_like_rate:.2f}%**")
            st.markdown(f"- 未看完用户点赞率: **{not_finish_like_rate:.2f}%**")
            st.markdown(f"- 看完点赞率是未看完的 **{finish_like_rate/not_finish_like_rate:.1f}倍**")
            st.markdown("</div>", unsafe_allow_html=True)

    # ---- Tab3: 观看完整数 ----
    with tab3:
        st.markdown("""
        <div class="highlight-box">
        <strong>📌 要求1-用户指标③：观看完整数 (完播率)</strong><br>
        分析用户是否完整观看视频的行为，完播率是衡量内容吸引力的核心指标。
        </div>
        """, unsafe_allow_html=True)

        total_finish = int(df_filtered['finish'].sum())
        finish_rate = df_filtered['finish'].mean() * 100
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("完整观看总数", f"{total_finish:,}")
        with col2:
            st.metric("平均完播率", f"{finish_rate:.2f}%")
        with col3:
            not_finish = len(df_filtered) - total_finish
            st.metric("未看完数", f"{not_finish:,}")

        st.markdown('<div class="req-sub">⏱ 不同视频时长的完播率</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 2])
        with col1:
            chart = duration_vs_completion(df_filtered)
            render_chart(chart, "450px")
        with col2:
            st.markdown('<div class="insight-box"><strong>💡 分析结论</strong><br>', unsafe_allow_html=True)
            dur_stats = df_filtered.groupby('duration_group', observed=False)['finish'].mean() * 100
            best_dur = dur_stats.idxmax()
            worst_dur = dur_stats.idxmin()
            st.markdown(f"- **完播率最高**: **{best_dur}** ({dur_stats.max():.1f}%)")
            st.markdown(f"- **完播率最低**: **{worst_dur}** ({dur_stats.min():.1f}%)")
            st.markdown("- 短视频（15秒以内）完播率显著高于长视频")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="req-sub">📊 完播率的影响因素</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            channel_map_inv = {0: '推荐页', 1: '关注页', 2: '搜索页', 3: '个人主页'}
            finish_by_channel = df_filtered.groupby('channel')['finish'].mean() * 100
            bar = Bar(init_opts=opts.InitOpts(width='100%', height='400px'))
            bar.add_xaxis([channel_map_inv.get(c, str(c)) for c in finish_by_channel.index])
            bar.add_yaxis('完播率(%)', finish_by_channel.values.round(1).tolist())
            bar.set_global_opts(
                title_opts=opts.TitleOpts(title='各分发渠道的完播率',
                    title_textstyle_opts=opts.TextStyleOpts(color=MORANDI['primary_dark'], font_size=14)),
                yaxis_opts=opts.AxisOpts(name='完播率(%)'),
                toolbox_opts=opts.ToolboxOpts(),
            )
            bar.set_colors([MORANDI['primary']])
            render_chart(bar, "400px")
        with col2:
            st.markdown(f'''
            <div class="success-box">
            <strong>✅ 完播率优化建议</strong>
            <ol style="margin:0.5rem 0;padding-left:1.2rem;">
                <li>视频控制在 <strong>10-15秒</strong> 以内完播率最高</li>
                <li><strong>前3秒</strong> 抓住用户注意力是关键</li>
                <li><strong>关注页和搜索页</strong> 的用户完播率更高（目的性强）</li>
                <li><strong>傍晚和夜间</strong> 用户更可能看完完整视频</li>
            </ol>
            </div>
            ''', unsafe_allow_html=True)

    # ---- Tab4: 观看作品城市数 ----
    with tab4:
        st.markdown("""
        <div class="highlight-box">
        <strong>📌 要求1-用户指标④：观看作品城市数</strong><br>
        分析用户所在城市分布，了解不同城市用户的观看行为差异。
        </div>
        """, unsafe_allow_html=True)

        n_cities = df_filtered[df_filtered['user_city'] > 0]['user_city'].nunique()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("用户覆盖城市数", f"{n_cities} 个")
        with col2:
            top_city = df_filtered[df_filtered['user_city_name'] != "其他城市"]['user_city_name'].value_counts().index[0]
            st.metric("最多用户的城市", top_city)

        st.markdown('<div class="req-sub">🌍 用户城市分布 Top20</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 2])
        with col1:
            chart = user_city_distribution(df_filtered)
            render_chart(chart, "480px")
        with col2:
            st.markdown('<div class="insight-box"><strong>💡 分析结论</strong><br>', unsafe_allow_html=True)
            city_stats = df_filtered.groupby('user_city_name').agg(
                用户数=('uid', 'nunique'),观看次数=('item_id', 'count'),
            ).sort_values('用户数', ascending=False)
            top3 = city_stats.head(3)
            st.markdown("**用户最多的城市**")
            for idx, row in top3.iterrows():
                st.markdown(f"- **{idx}**: {int(row['用户数']):,} 用户, {int(row['观看次数']):,} 次观看")
            st.markdown(f"Top3用户数占总 **{(top3['用户数'].sum()/city_stats['用户数'].sum()*100):.1f}%**")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="req-sub">📊 用户城市详情表</div>', unsafe_allow_html=True)
        city_detail = df_filtered.groupby('user_city_name').agg(
            用户数=('uid', 'nunique'),观看次数=('item_id', 'count'),
            完播率=('finish', 'mean'),点赞率=('like', 'mean'),
        ).reset_index()
        city_detail['完播率'] = (city_detail['完播率'] * 100).round(1)
        city_detail['点赞率'] = (city_detail['点赞率'] * 100).round(2)
        city_detail.columns = ['城市', '用户数', '观看次数', '完播率(%)', '点赞率(%)']
        st.dataframe(city_detail.sort_values('观看次数', ascending=False), use_container_width=True, hide_index=True)


# =========================================================
# 页面 2: 作者数据可视化分析（要求2）
# =========================================================
elif selected_page == "📋 要求2-作者分析":
    st.markdown("""
    <div class="req-header">
    📋 要求2 — 作者数据可视化分析 <small>作品平均时长 / 发布作品数 / 创作活跃度 / 去过城市数</small>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "⏱ 作品平均时长", "📦 发布作品数", "🔥 创作活跃度", "🏙 去过城市数",
    ])

    with tab1:
        st.markdown("""
        <div class="highlight-box">
        <strong>📌 要求2-作者指标①：作品平均时长</strong><br>
        分析每位创作者的平均视频时长，了解不同作者的创作风格。
        </div>
        """, unsafe_allow_html=True)

        author_dur = df_filtered.groupby('author_id')['duration_time'].mean()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("创作者总数", f"{author_dur.shape[0]:,}")
        with col2:
            st.metric("全平台平均时长", f"{df_filtered['duration_time'].mean():.1f}s")
        with col3:
            st.metric("创作者平均时长", f"{author_dur.mean():.1f}s")

        st.markdown('<div class="req-sub">⏱ 创作者平均作品时长分布</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 2])
        with col1:
            chart = author_duration_analysis(df_filtered)
            render_chart(chart, "450px")
        with col2:
            st.markdown('<div class="insight-box"><strong>💡 分析结论</strong><br>', unsafe_allow_html=True)
            dur_bins = pd.cut(author_dur, bins=[0, 5, 10, 15, 20, 30, 60, 999],
                             labels=['0-5s', '5-10s', '10-15s', '15-20s', '20-30s', '30-60s', '60s+'])
            most_common = dur_bins.value_counts().idxmax()
            short_pct = dur_bins.value_counts().loc[["0-5s","5-10s","10-15s"]].sum() / len(dur_bins) * 100
            st.markdown(f"- 大多数创作者的平均时长集中在 **{most_common}**")
            st.markdown(f"- 短视频创作者（<=15s）占比 **{short_pct:.1f}%**")
            st.markdown("</div>", unsafe_allow_html=True)


    with tab2:
        st.markdown("""
        <div class="highlight-box">
        <strong>📌 要求2-作者指标②：发布作品数</strong><br>
        分析创作者的内容产出量，了解平台创作者的活跃程度和产出分布。
        </div>
        """, unsafe_allow_html=True)

        author_prod = df_filtered.groupby('author_id')['item_id'].nunique()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("创作者总数", f"{author_prod.shape[0]:,}")
        with col2:
            st.metric("人均作品数", f"{author_prod.mean():.1f}")
        with col3:
            st.metric("最高产创作者作品数", f"{author_prod.max()}")

        st.markdown('<div class="req-sub">🏆 创作者发布作品数排行 Top30</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 2])
        with col1:
            chart = author_production_ranking(df_filtered)
            render_chart(chart, "450px")
        with col2:
            st.markdown('<div class="insight-box"><strong>💡 分析结论</strong><br>', unsafe_allow_html=True)
            top10_sum = author_prod.sort_values(ascending=False).head(10).sum()
            total_works = int(author_prod.sum())
            st.markdown(f"- Top10创作者发布了 **{top10_sum:,}** 个作品")
            st.markdown(f"- 占全部作品的 **{top10_sum/total_works*100:.1f}%**")
            st.markdown("- 二八效应明显：少数创作者产出多数内容")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="req-sub">完播率最高的创作者 Top20（作品>=5个）</div>', unsafe_allow_html=True)
        chart = author_top_by_completion(df_filtered)
        render_chart(chart, "450px")

    with tab3:
        st.markdown("""
        <div class="highlight-box">
        <strong>📌 要求2-作者指标③：创作活跃度</strong><br>
        分析创作者的活跃天数、发布频率，评估持续创作能力。
        </div>
        """, unsafe_allow_html=True)

        author_active = df_filtered.groupby('author_id').agg(
            活跃天数=('date', 'nunique'),作品数=('item_id', 'nunique'),总播放=('item_id', 'count'),
        ).reset_index()
        author_active['日均作品数'] = (author_active['作品数'] / author_active['活跃天数'].replace(0, 1)).round(2)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("创作者总数", f"{author_active.shape[0]:,}")
        with col2:
            st.metric("平均活跃天数", f"{author_active['活跃天数'].mean():.1f} 天")
        with col3:
            most_active = author_active.loc[author_active['活跃天数'].idxmax()]
            st.metric("最活跃创作者天数", f"{int(most_active['活跃天数'])} 天")

        st.markdown('<div class="req-sub">🔥 创作者活跃天数分布</div>', unsafe_allow_html=True)
        bins = [1, 2, 5, 10, 20, 30, 999]
        labels = ['1天', '2-5天', '5-10天', '10-20天', '20-30天', '30天+']
        active_bins = pd.cut(author_active['活跃天数'], bins=bins, labels=labels, right=False)
        dist = active_bins.value_counts().reindex(labels).fillna(0).astype(int)

        bar = Bar(init_opts=opts.InitOpts(width='100%', height='400px'))
        bar.add_xaxis(dist.index.tolist())
        bar.add_yaxis('创作者数', dist.values.tolist())
        bar.set_global_opts(
            title_opts=opts.TitleOpts(title='创作者活跃天数分布',
                title_textstyle_opts=opts.TextStyleOpts(color=MORANDI['primary_dark'], font_size=14)),
            xaxis_opts=opts.AxisOpts(name='活跃天数'),
            yaxis_opts=opts.AxisOpts(name='创作者数'),
            toolbox_opts=opts.ToolboxOpts(),
        )
        bar.set_colors([MORANDI['sage']])
        render_chart(bar, "400px")

        st.markdown('<div class="req-sub">📊 活跃度 vs 作品数散点图</div>', unsafe_allow_html=True)
        scatter = Scatter(init_opts=opts.InitOpts(width='100%', height='400px'))
        # 固定种子采样，避免每次刷新随机选择不同数据点
        rng = np.random.default_rng(42)
        n_sample = min(2000, len(author_active))
        sample = author_active.iloc[rng.choice(len(author_active), n_sample, replace=False)]
        scatter.add_xaxis(sample['活跃天数'].tolist())
        scatter.add_yaxis('创作者', sample['作品数'].tolist(),
                          symbol_size=5, color='rgba(125, 139, 154, 0.35)')
        scatter.set_global_opts(
            title_opts=opts.TitleOpts(title='创作者活跃天数 vs 作品数',
                title_textstyle_opts=opts.TextStyleOpts(color=MORANDI['primary_dark'], font_size=14)),
            xaxis_opts=opts.AxisOpts(name='活跃天数'),
            yaxis_opts=opts.AxisOpts(name='作品数'),
            toolbox_opts=opts.ToolboxOpts(),
        )
        render_chart(scatter, "400px")

        st.markdown(f"""
        <div class="insight-box"><strong>💡 分析结论</strong><br>
        - 大部分创作者活跃天数较少，属于"尝试型"创作者<br>
        - 少数创作者持续活跃（20天以上），是平台的核心创作者<br>
        - 活跃天数与作品数呈正相关，持续创作是增加作品量的关键
        </div>
        """, unsafe_allow_html=True)

    with tab4:
        st.markdown("""
        <div class="highlight-box">
        <strong>📌 要求2-作者指标④：去过城市数（发布城市覆盖）</strong><br>
        分析创作者的作品发布城市覆盖范围，了解创作者的地域分布特征。
        </div>
        """, unsafe_allow_html=True)

        author_cities = df_filtered[df_filtered['item_city'] > 0].groupby('author_id')['item_city'].nunique()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("创作者总数", f"{author_cities.shape[0]:,}")
        with col2:
            st.metric("平均去过城市数", f"{author_cities.mean():.1f}")
        with col3:
            st.metric("覆盖最多城市的创作者", f"{author_cities.max()} 个城市")

        st.markdown('<div class="req-sub">🏙 创作者去过的城市数分布</div>', unsafe_allow_html=True)
        bins = [1, 2, 3, 5, 10, 20, 999]
        labels = ['1个城市', '2个城市', '3-5个', '5-10个', '10-20个', '20个+']
        city_bins = pd.cut(author_cities, bins=bins, labels=labels, right=False)
        dist = city_bins.value_counts().reindex(labels).fillna(0).astype(int)

        bar = Bar(init_opts=opts.InitOpts(width='100%', height='400px'))
        bar.add_xaxis(dist.index.tolist())
        bar.add_yaxis('创作者数', dist.values.tolist())
        bar.set_global_opts(
            title_opts=opts.TitleOpts(title='创作者发布城市覆盖数分布',
                title_textstyle_opts=opts.TextStyleOpts(color=MORANDI['primary_dark'], font_size=14)),
            xaxis_opts=opts.AxisOpts(name='覆盖城市数'),
            yaxis_opts=opts.AxisOpts(name='创作者数'),
            toolbox_opts=opts.ToolboxOpts(),
        )
        bar.set_colors([MORANDI['taupe']])
        render_chart(bar, "400px")

        st.markdown('<div class="req-sub">📊 作品发布城市排行 Top20</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 2])
        with col1:
            chart = item_city_distribution(df_filtered)
            render_chart(chart, "450px")
        with col2:
            st.markdown('<div class="insight-box"><strong>💡 分析结论</strong><br>', unsafe_allow_html=True)
            city_stats = df_filtered.groupby('item_city_name').agg(
                作品数=('item_id', 'nunique'),作者数=('author_id', 'nunique'),
            ).sort_values('作品数', ascending=False)
            top3 = city_stats.head(3)
            st.markdown("**作品发布最多的城市**")
            for idx, row in top3.iterrows():
                st.markdown(f"- **{idx}**: {int(row['作品数']):,} 作品, {int(row['作者数']):,} 创作者")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="req-sub">创作者分发渠道偏好</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            chart = author_channel_distribution(df_filtered)
            render_chart(chart, "400px")
        with col2:
            st.markdown('<div class="insight-box"><strong>💡 流量渠道分析</strong><br>', unsafe_allow_html=True)
            from src.insights import channel_performance
            ch_data = channel_performance(df_filtered)
            for item in ch_data:
                st.markdown(f"- **{item['渠道']}**: {item['占比']}流量, 完播{item['完播率']}, 点赞{item['点赞率']}")
            st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 页面 3: 作品数据可视化分析（要求3）
# =========================================================
elif selected_page == "📋 要求3-作品分析":
    st.markdown("""
    <div class="req-header">
    📋 要求3 — 作品数据可视化分析 <small>点赞量 / 浏览量 / 背景音乐 / 发布城市</small>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "❤️ 点赞量分析", "👁 浏览量分析", "🎵 背景音乐分析", "🏙 发布城市分析",
    ])

    with tab1:
        st.markdown("""
        <div class="highlight-box">
        <strong>📌 要求3-作品指标①：点赞量</strong><br>
        分析作品获得的点赞情况，点赞量反映内容的受欢迎程度。
        </div>
        """, unsafe_allow_html=True)

        total_likes = int(df_filtered['like'].sum())
        like_rate = df_filtered['like'].mean() * 100
        n_items = df_filtered['item_id'].nunique()
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("作品总点赞量", f"{total_likes:,}")
        with col2: st.metric("作品平均点赞率", f"{like_rate:.2f}%")
        with col3: st.metric("作品总数", f"{n_items:,}")

        st.markdown('<div class="req-sub">❤️ 不同维度对点赞率的影响</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            chart = duration_vs_completion(df_filtered)
            chart.set_global_opts(title_opts=opts.TitleOpts(title='不同时长对点赞率/完播率的影响',
                title_textstyle_opts=opts.TextStyleOpts(color=MORANDI['primary_dark'], font_size=14)))
            chart.set_colors([MORANDI['primary'], MORANDI['rose']])
            render_chart(chart, "400px")
        with col2:
            ch_map = {0: '推荐页', 1: '关注页', 2: '搜索页', 3: '个人主页'}
            like_by_ch = df_filtered.groupby('channel')['like'].mean() * 100
            bar = Bar(init_opts=opts.InitOpts(width='100%', height='400px'))
            bar.add_xaxis([ch_map.get(c, str(c)) for c in like_by_ch.index])
            bar.add_yaxis('点赞率(%)', like_by_ch.values.round(2).tolist())
            bar.set_global_opts(
                title_opts=opts.TitleOpts(title='不同渠道的点赞率',
                    title_textstyle_opts=opts.TextStyleOpts(color=MORANDI['primary_dark'], font_size=14)),
                toolbox_opts=opts.ToolboxOpts(),
            )
            bar.set_colors([MORANDI['sage']])
            render_chart(bar, "400px")

        chart = like_vs_finish_heatmap(df_filtered)
        render_chart(chart, "400px")

    with tab2:
        st.markdown("""
        <div class="highlight-box">
        <strong>📌 要求3-作品指标②：浏览量</strong><br>
        分析作品的浏览/播放情况，浏览量是衡量作品曝光和吸引力的基础指标。
        </div>
        """, unsafe_allow_html=True)

        total_views = len(df_filtered)
        views_per_item = total_views / max(n_items, 1)
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("总浏览量", f"{total_views:,}")
        with col2: st.metric("平均单作品浏览量", f"{views_per_item:.1f} 次")
        with col3: st.metric("作品总数", f"{n_items:,}")

        st.markdown('<div class="req-sub">👁 浏览量时段分布</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            chart = user_active_hours(df_filtered)
            render_chart(chart, "450px")
        with col2:
            chart = user_weekday_activity(df_filtered)
            render_chart(chart, "400px")

        st.markdown('<div class="req-sub">📈 各分发渠道的浏览量占比</div>', unsafe_allow_html=True)
        ch_map = {0: '推荐页', 1: '关注页', 2: '搜索页', 3: '个人主页'}
        views_by_ch = df_filtered.groupby('channel')['item_id'].count()
        bar = Bar(init_opts=opts.InitOpts(width='100%', height='400px'))
        bar.add_xaxis([ch_map.get(c, str(c)) for c in views_by_ch.index])
        bar.add_yaxis('浏览量', views_by_ch.values.tolist())
        bar.set_global_opts(
            title_opts=opts.TitleOpts(title='各渠道浏览量分布',
                title_textstyle_opts=opts.TextStyleOpts(color=MORANDI['primary_dark'], font_size=14)),
            yaxis_opts=opts.AxisOpts(name='浏览量'),
            toolbox_opts=opts.ToolboxOpts(),
        )
        bar.set_colors([MORANDI['primary']])
        render_chart(bar, "400px")

        st.markdown(f"""
        <div class="insight-box"><strong>💡 分析结论</strong><br>
        - 推荐页贡献了绝大部分浏览量，是作品曝光的主要渠道<br>
        - 晚间和周末是浏览高峰期，适合发布新内容获取更多曝光<br>
        - 浏览量集中在短时长视频（≤15s），用户更倾向于浏览短视频
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        st.markdown("""
        <div class="highlight-box">
        <strong>📌 要求3-作品指标③：背景音乐</strong><br>
        分析作品使用的背景音乐情况，音乐是短视频内容的重要组成部分。
        </div>
        """, unsafe_allow_html=True)

        n_music = int(df_filtered['music_id'].nunique())
        top_music_id = int(df_filtered['music_id'].value_counts().index[0])
        top_music_usage = int(df_filtered['music_id'].value_counts().iloc[0])
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("背景音乐总数", f"{n_music:,}")
        with col2: st.metric("最热门音乐ID", f"{top_music_id}")
        with col3: st.metric("最热音乐使用次数", f"{top_music_usage:,}")

        st.markdown('<div class="req-sub">🎵 热门背景音乐排行 Top20</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 2])
        with col1:
            chart = music_top_usage(df_filtered)
            render_chart(chart, "450px")
        with col2:
            st.markdown('<div class="insight-box"><strong>💡 分析结论</strong><br>', unsafe_allow_html=True)
            music_stats = data_loader.get_music_stats(df_filtered)
            st.markdown(f"- 最热门音乐被使用了 **{int(music_stats['总播放量'].iloc[0]):,}** 次")
            st.markdown(f"- Top5音乐平均完播率 **{music_stats.head(5)['完播率'].mean():.1f}%**")
            st.markdown(f"- Top5音乐平均点赞率 **{music_stats.head(5)['点赞率'].mean():.2f}%**")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="req-sub">📊 背景音乐详细数据表</div>', unsafe_allow_html=True)
        music_stats = data_loader.get_music_stats(df_filtered)
        st.dataframe(music_stats.head(20), use_container_width=True)

    with tab4:
        st.markdown("""
        <div class="highlight-box">
        <strong>📌 要求3-作品指标④：发布城市</strong><br>
        分析作品的发布城市分布，了解不同城市的内容创作生态。
        </div>
        """, unsafe_allow_html=True)

        n_item_cities = int(df_filtered[df_filtered['item_city'] > 0]['item_city'].nunique())
        top_item_city = df_filtered[df_filtered['item_city_name'] != "其他城市"]['item_city_name'].value_counts().index[0]
        col1, col2 = st.columns(2)
        with col1: st.metric("作品覆盖发布城市数", f"{n_item_cities} 个")
        with col2: st.metric("最多作品发布城市", top_item_city)

        st.markdown('<div class="req-sub">🏙 作品发布城市分布 Top20</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 2])
        with col1:
            chart = item_city_distribution(df_filtered)
            render_chart(chart, "450px")
        with col2:
            st.markdown('<div class="insight-box"><strong>💡 分析结论</strong><br>', unsafe_allow_html=True)
            city_stats = df_filtered.groupby('item_city_name').agg(
                作品数=('item_id', 'nunique'),作者数=('author_id', 'nunique'),
            ).sort_values('作品数', ascending=False)
            for idx, row in city_stats.head(3).iterrows():
                st.markdown(f"- **{idx}**: {int(row['作品数']):,} 作品, {int(row['作者数']):,} 创作者")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="req-sub">📊 发布城市 vs 完播率（作品>=10）</div>', unsafe_allow_html=True)
        city_finish = df_filtered.groupby('item_city_name').agg(
            作品数=('item_id', 'nunique'),完播率=('finish', 'mean'),
        ).reset_index()
        city_finish = city_finish[city_finish['作品数'] >= 10].sort_values('完播率', ascending=False).head(20)
        city_finish['完播率'] = (city_finish['完播率'] * 100).round(1)

        bar = Bar(init_opts=opts.InitOpts(width='100%', height='400px'))
        bar.add_xaxis(city_finish['item_city_name'].tolist())
        bar.add_yaxis('完播率(%)', city_finish['完播率'].tolist())
        bar.set_global_opts(
            title_opts=opts.TitleOpts(title='各城市作品完播率排行',
                title_textstyle_opts=opts.TextStyleOpts(color=MORANDI['primary_dark'], font_size=14)),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
            toolbox_opts=opts.ToolboxOpts(),
        )
        bar.set_colors([MORANDI['rose']])
        render_chart(bar, "400px")


# =========================================================
# 页面 4: 智能洞察（拓展）
# =========================================================
elif selected_page == "💡 智能洞察(拓展)":
    st.markdown(
        f'<div class="main-header">💡 智能洞察 & 创作建议</div>',
        unsafe_allow_html=True,
    )

    try:
        bp = best_publish_time(df_filtered)
        st.markdown(f'''
        <div class="success-box">
        <strong>⏰ 最佳发布时间推荐</strong><br>
        <span style="font-size:1.1rem;">{bp["最佳时段"]}</span> 发布的视频综合表现最佳<br>
        完播率 <strong>{bp["完播率"]}</strong> · 点赞率 <strong>{bp["点赞率"]}</strong> · {bp["数据量"]}
        </div>
        ''', unsafe_allow_html=True)

        bd = best_duration_analysis(df_filtered)
        st.markdown(f'''
        <div class="success-box">
        <strong>⏱ 最佳视频时长推荐</strong><br>
        <span style="font-size:1.1rem;">{bd["最佳时长(秒)"]}秒</span> 是所有视频中综合表现最好的时长<br>
        完播率 {bd["完播率"]} · 点赞率 {bd["点赞率"]}<br>
        Top5推荐时长: {", ".join([f"{s}秒" for s in bd["Top5推荐时长"]])}
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('<div class="sub-header">👥 用户画像总结</div>', unsafe_allow_html=True)
        ups = user_portrait_summary(df_filtered)
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("总用户数", ups['总用户数'])
        with col2: st.metric("完播型用户", ups['完播型用户'])
        with col3: st.metric("点赞型用户", ups['点赞型用户'])
        with col4: st.metric("高频用户", ups['高频用户'])

        st.markdown('<div class="sub-header">📡 分发渠道效果对比</div>', unsafe_allow_html=True)
        ch_data = channel_performance(df_filtered)
        cols = st.columns(3)
        for i, item in enumerate(ch_data):
            with cols[i % 3]:
                st.markdown(f"**{item['渠道']}**")
                st.markdown(f"- 流量占比: {item['占比']}")
                st.markdown(f"- 完播率: {item['完播率']}")
                st.markdown(f"- 点赞率: {item['点赞率']}")

        st.markdown('<div class="sub-header">📊 关键因素相关性分析</div>', unsafe_allow_html=True)
        corr_data = correlation_analysis(df_filtered)
        for item in corr_data['解读']:
            st.markdown(f'''
            <div class="insight-box">
            <strong>{item["因素"]}</strong><br>
            {item["解读"]}<br>
            <small>完播率: {item["与完播率关系"]} · 点赞率: {item["与点赞率关系"]}</small>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown(f'''
        <div class="success-box">
        <strong>🎯 综合创作建议（数据驱动）</strong>
        <ol style="margin:0.5rem 0 0 0;padding-left:1.2rem;">
            <li><strong>控制时长在10-15秒</strong> — 完播率和点赞率的黄金区间</li>
            <li><strong>选择傍晚或夜间发布</strong> — 用户更活跃，互动率更高</li>
            <li><strong>使用热门背景音乐</strong> — 能显著提升曝光量和互动率</li>
            <li><strong>内容前3秒抓住注意力</strong> — 完播率的关键在开头</li>
            <li><strong>周末加大内容投放</strong> — 用户活跃度比工作日更高</li>
        </ol>
        </div>
        ''', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"分析过程出错: {e}")
        st.info("部分分析可能需要更多数据，请检查筛选条件。")


# ========== 页脚 ==========
st.markdown(f"<hr style='border-color:{MORANDI['border']};margin-top:2rem;'>", unsafe_allow_html=True)
st.markdown(
    f"<div style='text-align: center; color: {MORANDI['text_light']}; font-size: 0.8rem;'>"
    f"📊 抖音短视频数据智能分析平台 · Python程序设计课程大作业 · 任务2：Python数据分析 · "
    f"<span style='color:{MORANDI['sage']};'>Morandi</span> Design"
    f"</div>",
    unsafe_allow_html=True,
)
