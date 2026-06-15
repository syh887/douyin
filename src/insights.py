"""
智能洞察模块
核心价值：告诉创作者"怎么做更好"，而不是仅仅展示数据
"""
import pandas as pd
import numpy as np


def best_publish_time(df: pd.DataFrame) -> dict:
    """
    最佳发布时间分析
    找出完播率和点赞率综合最高的时段
    """
    hour_stats = df.groupby('time_period').agg(
        观看次数=('item_id', 'count'),
        完播率=('finish', 'mean'),
        点赞率=('like', 'mean'),
    ).reset_index()
    hour_stats['完播率'] = (hour_stats['完播率'] * 100).round(1)
    hour_stats['点赞率'] = (hour_stats['点赞率'] * 100).round(2)
    hour_stats['综合得分'] = hour_stats['完播率'] * 0.5 + hour_stats['点赞率'] * 50

    best = hour_stats.loc[hour_stats['综合得分'].idxmax()]

    return {
        '最佳时段': str(best['time_period']),
        '完播率': f"{best['完播率']}%",
        '点赞率': f"{best['点赞率']}%",
        '数据量': f"{int(best['观看次数']):,} 次观看",
    }


def best_duration_analysis(df: pd.DataFrame) -> dict:
    """
    最佳视频时长深度分析
    按秒级粒度分析完播率和点赞率
    """
    # 按秒聚合（只统计 0-60s，长尾数据太少）
    df_short = df[df['duration_time'] <= 60]
    sec_stats = df_short.groupby('duration_time').agg(
        观看次数=('item_id', 'count'),
        完播率=('finish', 'mean'),
        点赞率=('like', 'mean'),
    ).reset_index()
    sec_stats['完播率'] = (sec_stats['完播率'] * 100).round(1)
    sec_stats['点赞率'] = (sec_stats['点赞率'] * 100).round(2)

    # 过滤观看次数过少的秒数（统计意义不足）
    min_views = sec_stats['观看次数'].quantile(0.1)
    sec_stats = sec_stats[sec_stats['观看次数'] >= min_views]

    # 综合得分
    sec_stats['得分'] = sec_stats['完播率'] * 0.6 + sec_stats['点赞率'] * 20
    best = sec_stats.loc[sec_stats['得分'].idxmax()]

    # Top 5 最佳时长
    top5 = sec_stats.nlargest(5, '得分')

    return {
        '最佳时长(秒)': int(best['duration_time']),
        '完播率': f"{best['完播率']}%",
        '点赞率': f"{best['点赞率']}%",
        'Top5推荐时长': [int(x) for x in top5['duration_time'].tolist()],
    }


def channel_performance(df: pd.DataFrame) -> list:
    """
    各分发渠道效果对比
    渠道0=推荐页, 2=同城/附近, 3=搜索, 4=个人主页
    """
    channel_names = {0: '推荐页', 2: '同城/附近', 3: '搜索', 4: '个人主页'}
    stats = df.groupby('channel').agg(
        观看次数=('item_id', 'count'),
        完播率=('finish', 'mean'),
        点赞率=('like', 'mean'),
    ).reset_index()
    stats['渠道'] = stats['channel'].map(channel_names)
    stats['完播率'] = (stats['完播率'] * 100).round(1)
    stats['点赞率'] = (stats['点赞率'] * 100).round(2)
    stats['占比'] = (stats['观看次数'] / stats['观看次数'].sum() * 100).round(1)

    results = []
    for _, row in stats.iterrows():
        results.append({
            '渠道': row['渠道'],
            '占比': f"{row['占比']}%",
            '完播率': f"{row['完播率']}%",
            '点赞率': f"{row['点赞率']}%",
        })
    return results


def correlation_analysis(df: pd.DataFrame) -> dict:
    """
    相关性分析：哪些因素影响完播率和点赞率
    """
    # 对数值型字段计算相关系数
    numeric_cols = ['duration_time', 'H', 'channel']
    df_num = df[numeric_cols + ['finish', 'like']].copy()

    corr = df_num.corr()
    finish_corr = corr['finish'].drop('finish').sort_values(ascending=False)
    like_corr = corr['like'].drop('like').sort_values(ascending=False)

    result = {
        '影响完播率因素': {k: f"{v:.3f}" for k, v in finish_corr.items()},
        '影响点赞率因素': {k: f"{v:.3f}" for k, v in like_corr.items()},
    }

    # 添加通俗解读
    insights = []
    for col in ['duration_time', 'H', 'channel']:
        fc = corr.loc['finish', col]
        lc = corr.loc['like', col]
        col_names = {'duration_time': '视频时长', 'H': '发布时间(小时)', 'channel': '分发渠道'}
        name = col_names.get(col, col)
        insights.append({
            '因素': name,
            '与完播率关系': f"{'正相关' if fc > 0 else '负相关'} ({fc:+.3f})",
            '与点赞率关系': f"{'正相关' if lc > 0 else '负相关'} ({lc:+.3f})",
            '解读': _interpret_correlation(col, fc, lc),
        })

    result['解读'] = insights
    return result


def _interpret_correlation(col: str, fc: float, lc: float) -> str:
    """对相关性给出通俗解读"""
    if col == 'duration_time':
        if fc < -0.05:
            return "视频越短，完播率越高（用户耐心有限）"
        elif fc > 0.05:
            return "视频越长，完播率越高（内容足够吸引人）"
        else:
            return "时长对完播率影响不大，内容质量才是关键"

    if col == 'H':
        if fc > 0.05:
            return "越晚发布，完播率越高（夜间用户更专注）"
        elif fc < -0.05:
            return "越早发布，完播率越高（早晨用户精力充沛）"
        else:
            return "发布时间对完播率影响不大"

    if col == 'channel':
        channels = {0: '推荐', 1: '关注', 2: '搜索', 3: '主页'}
        if fc > 0.05:
            return "推荐页带来的完播率更高"
        else:
            return "关注/搜索渠道的完播率更高（用户目的性更强）"

    return "无明显关联"


def user_portrait_summary(df: pd.DataFrame) -> dict:
    """
    用户画像总结
    帮助创作者了解"你的观众是什么样的"
    """
    total_users = df['uid'].nunique()

    # 完播型用户 vs 点赞型用户
    finish_users = df[df['finish'] == 1]['uid'].nunique()
    like_users = df[df['like'] == 1]['uid'].nunique()

    # 高频用户（观看次数超过均值+1std）
    user_views = df['uid'].value_counts()
    high_freq_threshold = user_views.mean() + user_views.std()
    high_freq_users = (user_views > high_freq_threshold).sum()

    return {
        '总用户数': f"{total_users:,}",
        '完播型用户': f"{finish_users:,} ({finish_users/total_users*100:.1f}%)",
        '点赞型用户': f"{like_users:,} ({like_users/total_users*100:.1f}%)",
        '高频用户': f"{high_freq_users:,} ({high_freq_users/total_users*100:.1f}%)",
        '低频用户': f"{total_users - high_freq_users:,} ({(total_users-high_freq_users)/total_users*100:.1f}%)",
    }
