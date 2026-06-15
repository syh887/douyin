"""
作品内容分析模块
分析维度：视频时长、音乐热度、发布城市、互动表现
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


def duration_vs_completion(df: pd.DataFrame) -> Bar:
    """时长分段 vs 完播率/点赞率"""
    duration_stats = df.groupby('duration_group', observed=False).agg(
        作品数=('item_id', 'count'),
        完播率=('finish', 'mean'),
        点赞率=('like', 'mean'),
    ).reset_index()
    duration_stats['完播率'] = (duration_stats['完播率'] * 100).round(1)
    duration_stats['点赞率'] = (duration_stats['点赞率'] * 100).round(2)

    bar = (
        Bar(init_opts=_base_opts('时长vs互动'))
        .add_xaxis(duration_stats['duration_group'].astype(str).tolist())
        .add_yaxis('完播率(%)', duration_stats['完播率'].tolist(), color=MORANDI_PRIMARY)
        .add_yaxis('点赞率(%)', duration_stats['点赞率'].tolist(), color=MORANDI_ROSE)
        .set_global_opts(
            title_opts=_title_opts('视频时长 vs 完播率 & 点赞率'),
            xaxis_opts=opts.AxisOpts(
                name='视频时长',
                axislabel_opts=opts.LabelOpts(color=MORANDI_TAUPE),
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=MORANDI_CLAY)),
            ),
            yaxis_opts=opts.AxisOpts(
                name='比率(%)',
                splitline_opts=opts.SplitLineOpts(linestyle_opts=opts.LineStyleOpts(color='#EDE7E0')),
            ),
            legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color=MORANDI_TAUPE)),
            toolbox_opts=opts.ToolboxOpts(),
        )
    )
    return bar


def duration_distribution(df: pd.DataFrame) -> Bar:
    """视频时长分布直方图"""
    hist, edges = np.histogram(df['duration_time'], bins=range(0, 65, 5))
    labels = [f'{i}-{i+5}s' for i in range(0, 60, 5)]

    bar = (
        Bar(init_opts=_base_opts('时长分布'))
        .add_xaxis(labels)
        .add_yaxis('作品数(万)', (hist / 10000).round(2).tolist(), color=MORANDI_SAGE)
        .set_global_opts(
            title_opts=_title_opts('视频时长分布（0-60s）'),
            xaxis_opts=opts.AxisOpts(
                name='时长区间',
                axislabel_opts=opts.LabelOpts(rotate=45, color=MORANDI_TAUPE),
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=MORANDI_CLAY)),
            ),
            yaxis_opts=opts.AxisOpts(
                name='作品数(万)',
                splitline_opts=opts.SplitLineOpts(linestyle_opts=opts.LineStyleOpts(color='#EDE7E0')),
            ),
            toolbox_opts=opts.ToolboxOpts(),
        )
    )
    return bar


def music_top_usage(df: pd.DataFrame, top_n: int = 20) -> Bar:
    """热门背景音乐 Top N"""
    music_counts = df.groupby('music_id').agg(
        使用作品数=('item_id', 'nunique'),
        总播放=('item_id', 'count'),
        完播率=('finish', 'mean'),
        点赞率=('like', 'mean'),
    ).reset_index()
    music_counts = music_counts.sort_values('总播放', ascending=False).head(top_n)
    music_counts['完播率'] = (music_counts['完播率'] * 100).round(1)
    music_counts['点赞率'] = (music_counts['点赞率'] * 100).round(2)

    bar = (
        Bar(init_opts=_base_opts('热门音乐'))
        .add_xaxis(music_counts['music_id'].astype(str).tolist())
        .add_yaxis('使用作品数', music_counts['使用作品数'].tolist(), color=MORANDI_PRIMARY)
        .add_yaxis('总播放量(万)', (music_counts['总播放'] / 10000).round(2).tolist(),
                   color=MORANDI_ROSE)
        .set_global_opts(
            title_opts=_title_opts(f'热门背景音乐 Top {top_n}'),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=90, interval=1, color=MORANDI_TAUPE),
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


def item_city_distribution(df: pd.DataFrame, top_n: int = 20) -> Bar:
    """作品发布城市分布 Top N"""
    city_stats = df.groupby('item_city_name').agg(
        作品数=('item_id', 'nunique'),
        完播率=('finish', 'mean'),
    ).reset_index()
    city_stats = city_stats.sort_values('作品数', ascending=False).head(top_n)
    city_stats['完播率'] = (city_stats['完播率'] * 100).round(1)

    bar = (
        Bar(init_opts=_base_opts('发布城市排行'))
        .add_xaxis(city_stats['item_city_name'].tolist())
        .add_yaxis('作品数', city_stats['作品数'].tolist(), color=MORANDI_TAUPE)
        .add_yaxis('完播率(%)', city_stats['完播率'].tolist(), color=MORANDI_ROSE)
        .set_global_opts(
            title_opts=_title_opts(f'作品发布城市 Top {top_n}'),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=45, color=MORANDI_TAUPE),
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=MORANDI_CLAY)),
            ),
            yaxis_opts=opts.AxisOpts(
                name='作品数',
                splitline_opts=opts.SplitLineOpts(linestyle_opts=opts.LineStyleOpts(color='#EDE7E0')),
            ),
            legend_opts=opts.LegendOpts(pos_bottom='0%',
                                        textstyle_opts=opts.TextStyleOpts(color=MORANDI_TAUPE)),
            toolbox_opts=opts.ToolboxOpts(),
        )
    )
    return bar


def like_vs_finish_heatmap(df: pd.DataFrame) -> Bar:
    """完播×点赞 交叉分析"""
    ct = pd.crosstab(df['finish'], df['like'])
    ct.index = ['未看完', '已看完']
    ct.columns = ['未点赞', '已点赞']

    bar = (
        Bar(init_opts=_base_opts('完播×点赞'))
        .add_xaxis(ct.index.tolist())
        .add_yaxis('未点赞', ct['未点赞'].tolist(), color=MORANDI_PRIMARY)
        .add_yaxis('已点赞', ct['已点赞'].tolist(), color=MORANDI_ROSE)
        .set_global_opts(
            title_opts=_title_opts('完播×点赞 交叉分析'),
            xaxis_opts=opts.AxisOpts(
                name='是否完播',
                axislabel_opts=opts.LabelOpts(color=MORANDI_TAUPE),
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=MORANDI_CLAY)),
            ),
            yaxis_opts=opts.AxisOpts(
                name='记录数(百万)',
                splitline_opts=opts.SplitLineOpts(linestyle_opts=opts.LineStyleOpts(color='#EDE7E0')),
            ),
            legend_opts=opts.LegendOpts(pos_bottom='0%',
                                        textstyle_opts=opts.TextStyleOpts(color=MORANDI_TAUPE)),
            toolbox_opts=opts.ToolboxOpts(),
        )
    )
    return bar


def recommend_best_duration(df: pd.DataFrame) -> dict:
    """智能建议：最佳视频时长区间"""
    duration_stats = df.groupby('duration_group', observed=False).agg(
        作品数=('item_id', 'count'),
        完播率=('finish', 'mean'),
        点赞率=('like', 'mean'),
    ).reset_index()
    duration_stats['完播率'] = (duration_stats['完播率'] * 100).round(1)
    duration_stats['点赞率'] = (duration_stats['点赞率'] * 100).round(2)

    duration_stats['综合得分'] = (
        duration_stats['完播率'] * 0.6 + duration_stats['点赞率'] * 20
    )

    best = duration_stats.loc[duration_stats['综合得分'].idxmax()]
    worst = duration_stats.loc[duration_stats['综合得分'].idxmin()]

    return {
        '最佳时长段': str(best['duration_group']),
        '最佳完播率': f"{best['完播率']}%",
        '最佳点赞率': f"{best['点赞率']}%",
        '最佳作品数': f"{int(best['作品数']):,}",
        '最差时长段': str(worst['duration_group']),
        '最差完播率': f"{worst['完播率']}%",
        '最差点赞率': f"{worst['点赞率']}%",
    }
