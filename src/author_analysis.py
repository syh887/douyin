"""
创作者分析模块
分析维度：作品量排行、活跃度、完播/点赞表现、地域分布
"""
import pandas as pd
import numpy as np
from pyecharts.charts import Bar, Pie, Scatter, Line
from pyecharts import options as opts
from src.colors import (
    MORANDI_COLORS, MORANDI_PRIMARY, MORANDI_ROSE,
    MORANDI_SAGE, MORANDI_TAUPE, MORANDI_CLAY
)


def _base_opts(title: str) -> opts.InitOpts:
    return opts.InitOpts(width='100%', height='450px', bg_color='transparent')


def _title_opts(text: str) -> opts.TitleOpts:
    return opts.TitleOpts(
        title=text,
        title_textstyle_opts=opts.TextStyleOpts(
            color='#5D6B7A', font_size=14, font_weight='bold'
        ),
    )


def author_production_ranking(df: pd.DataFrame, top_n: int = 30) -> Bar:
    """创作者作品数排行 Top N"""
    author_counts = df.groupby('author_id').agg(
        作品数=('item_id', 'nunique'),
        总播放=('item_id', 'count'),
    ).reset_index()
    author_counts.columns = ['author_id', '作品数', '总播放']
    author_counts = author_counts.sort_values('作品数', ascending=False).head(top_n)

    bar = (
        Bar(init_opts=_base_opts('创作者排行'))
        .add_xaxis(author_counts['author_id'].astype(str).tolist())
        .add_yaxis('作品数', author_counts['作品数'].tolist(), color=MORANDI_PRIMARY)
        .add_yaxis('总播放量(万)', (author_counts['总播放'] / 10000).round(2).tolist(),
                   color=MORANDI_ROSE)
        .set_global_opts(
            title_opts=_title_opts(f'高产创作者 Top {top_n}'),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=90, interval=2, color=MORANDI_TAUPE),
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=MORANDI_CLAY)),
            ),
            yaxis_opts=opts.AxisOpts(
                splitline_opts=opts.SplitLineOpts(linestyle_opts=opts.LineStyleOpts(color='#EDE7E0')),
            ),
            legend_opts=opts.LegendOpts(pos_bottom='0%',
                                        textstyle_opts=opts.TextStyleOpts(color=MORANDI_TAUPE)),
            toolbox_opts=opts.ToolboxOpts(),
        )
    )
    return bar


def author_performance_scatter(df: pd.DataFrame) -> Scatter:
    """创作者完播率 vs 点赞率 散点图"""
    author_stats = df.groupby('author_id').agg(
        作品数=('item_id', 'nunique'),
        完播率=('finish', 'mean'),
        点赞率=('like', 'mean'),
        总播放=('item_id', 'count'),
    ).reset_index()
    author_stats = author_stats[author_stats['作品数'] >= 5]
    author_stats['完播率'] = (author_stats['完播率'] * 100).round(1)
    author_stats['点赞率'] = (author_stats['点赞率'] * 100).round(2)

    scatter = (
        Scatter(init_opts=_base_opts('创作者表现'))
        .add_xaxis(author_stats['完播率'].tolist())
        .add_yaxis('创作者', author_stats['点赞率'].tolist(),
                   symbol_size=8, color=MORANDI_SAGE)
        .set_global_opts(
            title_opts=_title_opts('创作者完播率 vs 点赞率 (作品>=5)'),
            xaxis_opts=opts.AxisOpts(
                name='完播率(%)', min_=0, max_=100,
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


def author_duration_analysis(df: pd.DataFrame) -> Bar:
    """创作者平均作品时长分布"""
    duration_stats = df.groupby('author_id')['duration_time'].mean().reset_index()
    duration_stats.columns = ['author_id', '平均时长']

    bins = [0, 5, 10, 15, 20, 30, 60, 999]
    labels = ['0-5s', '5-10s', '10-15s', '15-20s', '20-30s', '30-60s', '60s+']
    duration_stats['时长段'] = pd.cut(duration_stats['平均时长'], bins=bins, labels=labels, right=False)
    dist = duration_stats['时长段'].value_counts().reindex(labels).fillna(0)

    bar = (
        Bar(init_opts=_base_opts('创作者时长分布'))
        .add_xaxis(dist.index.tolist())
        .add_yaxis('创作者数量', dist.values.astype(int).tolist(), color=MORANDI_PRIMARY)
        .set_global_opts(
            title_opts=_title_opts('创作者平均作品时长分布'),
            xaxis_opts=opts.AxisOpts(
                name='平均时长段',
                axislabel_opts=opts.LabelOpts(color=MORANDI_TAUPE),
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=MORANDI_CLAY)),
            ),
            yaxis_opts=opts.AxisOpts(
                name='创作者数',
                splitline_opts=opts.SplitLineOpts(linestyle_opts=opts.LineStyleOpts(color='#EDE7E0')),
            ),
            toolbox_opts=opts.ToolboxOpts(),
        )
    )
    return bar


def author_top_by_completion(df: pd.DataFrame, top_n: int = 20) -> Bar:
    """完播率最高的创作者 Top N"""
    author_stats = df.groupby('author_id').agg(
        完播率=('finish', 'mean'),
        点赞率=('like', 'mean'),
        作品数=('item_id', 'nunique'),
    ).reset_index()
    author_stats = author_stats[author_stats['作品数'] >= 5]
    author_stats['完播率'] = (author_stats['完播率'] * 100).round(1)
    author_stats['点赞率'] = (author_stats['点赞率'] * 100).round(2)
    top = author_stats.sort_values('完播率', ascending=False).head(top_n)

    bar = (
        Bar(init_opts=_base_opts('完播率排行'))
        .add_xaxis(top['author_id'].astype(str).tolist())
        .add_yaxis('完播率(%)', top['完播率'].tolist(), color=MORANDI_SAGE)
        .add_yaxis('点赞率(%)', top['点赞率'].tolist(), color=MORANDI_ROSE)
        .set_global_opts(
            title_opts=_title_opts(f'完播率最高创作者 Top {top_n} (作品>=5)'),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=90, interval=2, color=MORANDI_TAUPE),
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=MORANDI_CLAY)),
            ),
            yaxis_opts=opts.AxisOpts(
                splitline_opts=opts.SplitLineOpts(linestyle_opts=opts.LineStyleOpts(color='#EDE7E0')),
            ),
            legend_opts=opts.LegendOpts(pos_bottom='0%',
                                        textstyle_opts=opts.TextStyleOpts(color=MORANDI_TAUPE)),
            toolbox_opts=opts.ToolboxOpts(),
        )
    )
    return bar


def author_channel_distribution(df: pd.DataFrame) -> Pie:
    """创作者使用的分发渠道分析"""
    channel_names = {0: '推荐页', 2: '同城/附近', 3: '搜索', 4: '个人主页'}
    channel_stats = df.groupby('channel').agg(
        作者数=('author_id', 'nunique'),
    ).reset_index()
    channel_stats['channel_name'] = channel_stats['channel'].map(channel_names)
    data_pair = [list(z) for z in zip(channel_stats['channel_name'].tolist(),
                                        channel_stats['作者数'].tolist())]

    pie = (
        Pie(init_opts=_base_opts('渠道分布'))
        .add('渠道', data_pair, radius=['30%', '60%'])
        .set_global_opts(
            title_opts=_title_opts('创作者分发渠道分布'),
            legend_opts=opts.LegendOpts(orient='vertical', pos_left='5%', pos_top='15%',
                                       textstyle_opts=opts.TextStyleOpts(color=MORANDI_TAUPE)),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter='{b}: {d}%', color=MORANDI_TAUPE))
        .set_colors(MORANDI_COLORS)
    )
    return pie
