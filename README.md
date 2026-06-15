# 抖音短视频数据智能分析平台

基于 **Streamlit** 构建的抖音短视频数据分析仪表盘，包含用户分析、内容分析、作者分析、智能洞察等功能。

##  功能模块

| 模块 | 说明 |
|------|------|
| **数据概览** | 数据集规模、关键指标总览 |
| **用户分析** | 用户城市分布、互动行为、活跃时段、完播与点赞关系 |
| **作者分析** | 作者产量排名、表现散点图、时长分析、渠道分布 |
| **内容分析** | 时长与完播率、音乐使用排行、城市热度、推荐最佳时长 |
| **智能洞察** | 最佳发布时间、时长建议、渠道表现、相关性分析、用户画像 |

##   运行方式

### 在线体验（推荐）
访问部署链接即可使用，无需安装任何软件。

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
streamlit run app.py
```

##   技术栈

- **前端/框架**: Streamlit
- **数据处理**: Pandas, NumPy
- **可视化**: PyEcharts, Plotly, Matplotlib
- **配色方案**: 莫兰迪色系

##   数据集

- 约 **173 万条** 抖音用户行为记录
- 包含用户信息、视频属性、互动行为（点赞/完播）等字段
- 时间范围：2019-09 ~ 2019-10

##   项目结构

```
douyin-analysis-platform/
├── app.py                 # 主应用入口
├── requirements.txt       # 依赖清单
├── data/
│   └── douyin_dataset.csv # 数据集
├── src/
│   ├── data_loader.py     # 数据加载与预处理
│   ├── user_analysis.py   # 用户分析模块
│   ├── author_analysis.py # 作者分析模块
│   ├── content_analysis.py# 内容分析模块
│   ├── insights.py        # 智能洞察模块
│   └── colors.py          # 莫兰迪色板
└── .gitignore
```
