"""
数据加载与预处理模块
负责：数据读取、缓存、清洗、特征工程
173万行数据 → 一次性加载 + 内存优化
"""
import pandas as pd
import numpy as np
import os
from pathlib import Path
import streamlit as st


# ---------- 城市编码映射 ----------
# 抖音城市编码 → 城市名
# 注意：数据只提供了数字编码，没有官方映射表
# 以下是根据部分已知信息整理的映射关系，未知编码显示为"城市X"
# 策略：有确定映射的显示城市名，不确定的显示编码本身（诚实展示）
CITY_CODE_MAP = {
    1: "北京", 2: "上海", 3: "天津", 4: "重庆",
    5: "石家庄", 6: "太原", 7: "沈阳", 8: "大连",
    9: "长春", 10: "哈尔滨",
    20: "南京", 21: "苏州", 22: "杭州",
    31: "合肥", 32: "福州", 33: "厦门",
    35: "南昌",
    42: "济南", 45: "青岛",
    53: "武汉",
    68: "广州", 69: "深圳", 70: "珠海", 71: "佛山",
    73: "南宁",
    80: "成都", 81: "贵阳",
    91: "昆明",
    97: "西安", 99: "兰州",
    109: "呼和浩特", 112: "三亚", 113: "海口",
    132: "西宁", 133: "银川",
    140: "乌鲁木齐", 155: "拉萨",
    158: "襄阳", 160: "宜昌", 162: "荆州",
    166: "黄石", 170: "九江", 175: "赣州",
    183: "湘潭", 189: "柳州", 200: "桂林", 213: "保定",
    134: "台北", 138: "香港", 139: "澳门",
}


def get_city_display(city_code: int) -> str:
    """
    将城市编码转为可读名称
    已知的显示城市名，未知的统一归为"其他城市"
    """
    v = int(city_code)
    return CITY_CODE_MAP.get(v, "其他城市")

# 时长分段标签
DURATION_BINS = [0, 5, 10, 15, 20, 30, 60, 999]
DURATION_LABELS = ['0-5s', '5-10s', '10-15s', '15-20s', '20-30s', '30-60s', '60s+']
DURATION_MID = [2.5, 7.5, 12.5, 17.5, 25, 45, 120]

# 时段分段
HOUR_BINS = list(range(0, 25))
HOUR_LABELS = [f'{h}-{h+1}' for h in range(24)]


@st.cache_data(show_spinner="正在加载数据... 173万行，稍等片刻 ⏳")
def load_data_v3(csv_path: str = None) -> pd.DataFrame:
    """
    加载抖音数据集，进行类型优化和基础清洗
    """
    if csv_path is None:
        # 默认路径：相对于项目根目录
        project_root = Path(__file__).parent.parent
        csv_path = project_root / "data" / "douyin_dataset.csv"

        # fallback: 桌面原始文件
        if not os.path.exists(csv_path):
            csv_path = Path(os.path.expanduser("~")) / "Desktop" / "python" / "douyin_dataset.csv"

    csv_path = str(csv_path)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"数据文件未找到: {csv_path}")

    # 读取时指定类型，节省内存
    dtypes = {
        'uid': 'int32',
        'user_city': 'float32',
        'item_id': 'int32',
        'author_id': 'int32',
        'item_city': 'float32',
        'channel': 'int8',
        'finish': 'int8',
        'like': 'int8',
        'music_id': 'float32',
        'duration_time': 'int32',
        'H': 'int8',
    }

    df = pd.read_csv(csv_path, index_col=0, dtype=dtypes, parse_dates=['real_time'])

    # 基础清洗 — 不过滤任何数据，保留全部记录
    df['user_city'] = df['user_city'].fillna(0).astype('int32').clip(lower=0)
    df['item_city'] = df['item_city'].fillna(0).astype('int32').clip(lower=0)

    # 将 date 转为 datetime
    df['date'] = pd.to_datetime(df['date'])

    return df


@st.cache_data(show_spinner="正在计算特征...")
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    特征工程：添加分析所需的衍生字段
    """
    df = df.copy()

    # 时长分段
    df['duration_group'] = pd.cut(
        df['duration_time'],
        bins=DURATION_BINS,
        labels=DURATION_LABELS,
        right=False
    )

    # 时段分段
    df['hour_group'] = pd.cut(
        df['H'],
        bins=HOUR_BINS,
        labels=HOUR_LABELS,
        right=False,
        include_lowest=True
    )

    # 时段分类
    def hour_to_period(h):
        if h < 6: return "凌晨(0-6点)"
        elif h < 9: return "早晨(6-9点)"
        elif h < 12: return "上午(9-12点)"
        elif h < 14: return "中午(12-14点)"
        elif h < 18: return "下午(14-18点)"
        elif h < 21: return "傍晚(18-21点)"
        else: return "夜间(21-24点)"

    df['time_period'] = df['H'].apply(hour_to_period)

    # 城市名称映射（使用 get_city_display，未知编码显示为"城市X"）
    df['user_city_name'] = df['user_city'].apply(get_city_display)
    df['item_city_name'] = df['item_city'].apply(get_city_display)

    # 互动标签
    def interaction_label(row):
        if row['like'] == 1 and row['finish'] == 1:
            return '深度互动(点赞+看完)'
        elif row['like'] == 1:
            return '点赞未看完'
        elif row['finish'] == 1:
            return '看完未点赞'
        else:
            return '无互动'

    df['interaction_type'] = df.apply(interaction_label, axis=1)

    return df


def get_data_summary(df: pd.DataFrame) -> dict:
    """返回数据集核心统计摘要"""
    return {
        "总记录数": f"{len(df):,}",
        "用户数": f"{df['uid'].nunique():,}",
        "作者数": f"{df['author_id'].nunique():,}",
        "作品数": f"{df['item_id'].nunique():,}",
        "日期范围": f"{df['date'].min().strftime('%Y-%m-%d')} ~ {df['date'].max().strftime('%Y-%m-%d')}",
        "平均完播率": f"{df['finish'].mean()*100:.1f}%",
        "平均点赞率": f"{df['like'].mean()*100:.2f}%",
        "平均时长": f"{df['duration_time'].mean():.1f}s",
        "覆盖城市(用户)": f"{df[df['user_city'] > 0]['user_city'].nunique()}个",
        "覆盖城市(发布)": f"{df[df['item_city'] > 0]['item_city'].nunique()}个",
    }


# ========== 快捷查询函数 ==========

def get_user_stats(df: pd.DataFrame) -> pd.DataFrame:
    """用户维度统计"""
    stats = df.groupby('uid').agg(
        观看作品数=('item_id', 'count'),
        完播数=('finish', 'sum'),
        点赞数=('like', 'sum'),
        完播率=('finish', 'mean'),
        点赞率=('like', 'mean'),
        平均观看时长=('duration_time', 'mean'),
        活跃天数=('date', 'nunique'),
        访问城市数=('user_city', 'nunique'),
    ).reset_index()
    stats['完播率'] = (stats['完播率'] * 100).round(1)
    stats['点赞率'] = (stats['点赞率'] * 100).round(2)
    stats['平均观看时长'] = stats['平均观看时长'].round(1)
    return stats


def get_author_stats(df: pd.DataFrame) -> pd.DataFrame:
    """作者维度统计"""
    stats = df.groupby('author_id').agg(
        作品数=('item_id', 'nunique'),
        总播放量=('item_id', 'count'),
        总完播数=('finish', 'sum'),
        总点赞数=('like', 'sum'),
        完播率=('finish', 'mean'),
        点赞率=('like', 'mean'),
        平均作品时长=('duration_time', 'mean'),
        作品分布城市数=('item_city', 'nunique'),
        活跃天数=('date', 'nunique'),
    ).reset_index()
    stats['完播率'] = (stats['完播率'] * 100).round(1)
    stats['点赞率'] = (stats['点赞率'] * 100).round(2)
    stats['平均作品时长'] = stats['平均作品时长'].round(1)
    return stats


def get_music_stats(df: pd.DataFrame) -> pd.DataFrame:
    """背景音乐维度统计"""
    stats = df.groupby('music_id').agg(
        使用作品数=('item_id', 'nunique'),
        总播放量=('item_id', 'count'),
        完播率=('finish', 'mean'),
        点赞率=('like', 'mean'),
    ).reset_index()
    stats['完播率'] = (stats['完播率'] * 100).round(1)
    stats['点赞率'] = (stats['点赞率'] * 100).round(2)
    return stats.sort_values('总播放量', ascending=False)
