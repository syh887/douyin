"""
用户分析模块
分析维度：用户地域分布、互动行为、活跃时段、用户画像
"""
import pandas as pd
import numpy as np
from pyecharts.charts import Bar, Pie, Line, Scatter, Map, HeatMap
from pyecharts import options as opts
from src.colors import (
    MORANDI_COLORS, MORANDI_PRIMARY, MORANDI_ROSE,
    MORANDI_SAGE, MORANDI_TAUPE, MORANDI_CLAY
)


def _base_opts(title: str, subtitle: str = "") -> opts.InitOpts:
    """统一初始化配置"""
    return opts.InitOpts(width='100%', height='450px',
                         bg_color='transparent')


def _title_opts(text: str) -> opts.TitleOpts:
    return opts.TitleOpts(
        title=text,
        title_textstyle_opts=opts.TextStyleOpts(
            color='#5D6B7A', font_size=14, font_weight='bold'
        ),
    )


def user_city_distribution(df: pd.DataFrame, top_n: int = 20) -> Bar:
    """用户地域分布 Top N"""
    city_stats = df.groupby('user_city_name').agg(
        用户数=('uid', 'nunique'),
        观看次数=('item_id', 'count'),
        完播率=('finish', 'mean'),
    ).reset_index()
    city_stats['完播率'] = (city_stats['完播率'] * 100).round(1)
    city_stats = city_stats.sort_values('用户数', ascending=False).head(top_n)

    bar = (
        Bar(init_opts=_base_opts('用户地域分布'))
        .add_xaxis(city_stats['user_city_name'].tolist())
        .add_yaxis('用户数', city_stats['用户数'].tolist(), color=MORANDI_PRIMARY)
        .set_global_opts(
            title_opts=_title_opts('用户地域分布 Top 20'),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=45, color=MORANDI_TAUPE),
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=MORANDI_CLAY)),
            ),
            yaxis_opts=opts.AxisOpts(
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=MORANDI_CLAY)),
                splitline_opts=opts.SplitLineOpts(linestyle_opts=opts.LineStyleOpts(color='#EDE7E0')),
            ),
            toolbox_opts=opts.ToolboxOpts(),
        )
    )
    return bar


def user_interaction_analysis(df: pd.DataFrame) -> Pie:
    """用户互动行为分布"""
    interaction_counts = df['interaction_type'].value_counts()
    data_pair = [list(z) for z in zip(interaction_counts.index.tolist(),
                                        interaction_counts.values.tolist())]

    pie = (
        Pie(init_opts=_base_opts('用户互动分布'))
        .add('互动类型', data_pair,
             radius=['30%', '60%'],
             center=['50%', '55%'],
             label_opts=opts.LabelOpts(formatter='{b}: {d}%',
                                       color=MORANDI_TAUPE))
        .set_global_opts(
            title_opts=_title_opts('用户互动行为分布'),
            legend_opts=opts.LegendOpts(orient='vertical', pos_left='5%', pos_top='14%',
                                       textstyle_opts=opts.TextStyleOpts(color=MORANDI_TAUPE)),
        )
        .set_colors(MORANDI_COLORS)
    )
    return pie


def user_active_hours(df: pd.DataFrame) -> Bar:
    """用户活跃时段分布"""
    hour_stats = df.groupby('H').agg(
        观看次数=('item_id', 'count'),
        点赞率=('like', 'mean'),
        完播率=('finish', 'mean'),
    ).reset_index()
    hour_stats['点赞率'] = (hour_stats['点赞率'] * 100).round(2)
    hour_stats['完播率'] = (hour_stats['完播率'] * 100).round(1)

    bar = (
        Bar(init_opts=_base_opts('用户活跃时段'))
        .add_xaxis(hour_stats['H'].astype(str).tolist())
        .add_yaxis('观看次数(万)',
                   (hour_stats['观看次数'] / 10000).round(2).tolist(),
                   color=MORANDI_PRIMARY)
        .set_global_opts(
            title_opts=_title_opts('用户活跃时段分布'),
            xaxis_opts=opts.AxisOpts(
                name='小时',
                axislabel_opts=opts.LabelOpts(rotate=45, color=MORANDI_TAUPE),
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=MORANDI_CLAY)),
            ),
            yaxis_opts=opts.AxisOpts(
                name='观看次数(万)',
                splitline_opts=opts.SplitLineOpts(linestyle_opts=opts.LineStyleOpts(color='#EDE7E0')),
            ),
            toolbox_opts=opts.ToolboxOpts(),
        )
    )
    return bar


def user_finish_vs_like(df: pd.DataFrame) -> Scatter:
    """完播率 vs 点赞率 散点图"""
    hour_stats = df.groupby('H').agg(
        完播率=('finish', 'mean'),
        点赞率=('like', 'mean'),
        观看次数=('item_id', 'count'),
    ).reset_index()
    hour_stats['完播率'] = (hour_stats['完播率'] * 100).round(1)
    hour_stats['点赞率'] = (hour_stats['点赞率'] * 100).round(2)

    scatter = (
        Scatter(init_opts=_base_opts('完播率vs点赞率'))
        .add_xaxis(hour_stats['完播率'].tolist())
        .add_yaxis('点赞率', hour_stats['点赞率'].tolist(),
                   symbol_size=lambda x: max(hour_stats['观看次数'].tolist()[x] / 3000, 5),
                   color=MORANDI_ROSE)
        .set_global_opts(
            title_opts=_title_opts('完播率 vs 点赞率 (气泡大小=观看次数)'),
            xaxis_opts=opts.AxisOpts(
                name='完播率(%)', min_=30, max_=50,
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=MORANDI_CLAY)),
            ),
            yaxis_opts=opts.AxisOpts(
                name='点赞率(%)',
                splitline_opts=opts.SplitLineOpts(linestyle_opts=opts.LineStyleOpts(color='#EDE7E0')),
            ),
            toolbox_opts=opts.ToolboxOpts(),
        )
    )
    return scatter


def user_top_active(df: pd.DataFrame, top_n: int = 30) -> Bar:
    """最活跃用户 Top N"""
    top_users = df['uid'].value_counts().head(top_n).reset_index()
    top_users.columns = ['uid', '观看次数']

    bar = (
        Bar(init_opts=_base_opts('活跃用户排行'))
        .add_xaxis(top_users['uid'].astype(str).tolist())
        .add_yaxis('观看次数', top_users['观看次数'].tolist(), color=MORANDI_SAGE)
        .set_global_opts(
            title_opts=_title_opts(f'最活跃用户 Top {top_n}'),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=90, interval=2, color=MORANDI_TAUPE),
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=MORANDI_CLAY)),
            ),
            yaxis_opts=opts.AxisOpts(
                splitline_opts=opts.SplitLineOpts(linestyle_opts=opts.LineStyleOpts(color='#EDE7E0')),
            ),
            toolbox_opts=opts.ToolboxOpts(),
        )
    )
    return bar


def user_weekday_activity(df: pd.DataFrame) -> Bar:
    """一周活跃度分析"""
    df['weekday'] = df['date'].dt.dayofweek
    weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    wd_stats = df.groupby('weekday').agg(
        观看次数=('item_id', 'count'),
        完播率=('finish', 'mean'),
        点赞率=('like', 'mean'),
    ).reset_index()
    wd_stats['完播率'] = (wd_stats['完播率'] * 100).round(1)
    wd_stats['点赞率'] = (wd_stats['点赞率'] * 100).round(2)
    wd_stats['weekday_name'] = wd_stats['weekday'].map(lambda x: weekday_names[int(x)])

    bar = (
        Bar(init_opts=_base_opts('一周活跃度'))
        .add_xaxis(wd_stats['weekday_name'].tolist())
        .add_yaxis('观看次数(万)', (wd_stats['观看次数'] / 10000).round(2).tolist(),
                   color=MORANDI_PRIMARY)
        .add_yaxis('完播率(%)', wd_stats['完播率'].tolist(), color=MORANDI_ROSE)
        .add_yaxis('点赞率(%)', wd_stats['点赞率'].tolist(), color=MORANDI_SAGE)
        .set_global_opts(
            title_opts=_title_opts('一周活跃度分析'),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=0, color=MORANDI_TAUPE),
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=MORANDI_CLAY)),
            ),
            yaxis_opts=opts.AxisOpts(
                name='数值',
                splitline_opts=opts.SplitLineOpts(linestyle_opts=opts.LineStyleOpts(color='#EDE7E0')),
            ),
            legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color=MORANDI_TAUPE)),
            toolbox_opts=opts.ToolboxOpts(),
        )
    )
    return bar
