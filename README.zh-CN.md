# 跨境电商经营分析自动化工具原型

中文 | [English](README.md)

这个项目用于演示如何把跨境电商订单、广告、库存和成本数据统一成经营分析结果。当前版本支持样例数据和 CSV 上传，后续可以扩展为平台后台或 API 自动接入。

## 方案逻辑

```text
平台后台 / CSV 导出 / 未来 API
  -> 标准化订单、成本、广告、库存表
  -> 自动校验字段和数据质量
  -> KPI 与利润计算
  -> 广告和库存异常诊断
  -> SKU × 地区推广机会评分
  -> 经营分析页面
  -> 导出月度经营复盘
```

当前 MVP 支持样例数据和 CSV 上传。仓库中预留了 Shopify、Amazon、ERP、WMS、广告平台等 API 接入位置，用于说明真实业务中如何扩展。

> 数据边界：订单交易数据来自 UCI Online Retail II 真实公开数据；成本、广告和库存字段是为了项目演示而构建的模拟经营数据，不代表任何真实公司的经营结果。

## 工具原型包含什么

Streamlit 页面支持：

- 使用本地完整数据、GitHub 样例数据或上传 CSV；
- 自动检查关键字段是否齐全；
- 展示经营 KPI 卡片；
- 展示月度收入、毛利、贡献利润趋势；
- 展示品类利润和市场利润；
- 识别 SKU × 地区推广机会；
- 展示低 ROAS 广告组合；
- 展示缺货和滞销 SKU；
- 下载 Markdown 月度经营复盘。

## SKU × 地区推广优先级模型

这个模型用于判断：

> 哪个 SKU 在哪个地区更值得投入推广资源？

模型综合四类指标：

| 指标 | 含义 |
|---|---|
| 销量贡献度 | 该组合销量 ÷ 全店销量 |
| GMV 贡献度 | 该组合 GMV ÷ 全店 GMV |
| 销量增长动量 | 根据周期销量趋势计算增长斜率 |
| 有效订单率 | 有效订单数 ÷ 总订单数 |

综合得分：

```text
综合得分 =
销量贡献得分 × 30%
+ GMV贡献得分 × 25%
+ 增长动量得分 × 20%
+ 有效订单率得分 × 25%
```

评分分层：

| 综合得分 | 分层 |
|---:|---|
| 75 分以上 | 重点加码 |
| 60-75 分 | 稳定投入 |
| 40-60 分 | 观察优化 |
| 40 分以下 | 缩减测试 |

## 经营报表示例

最新完整分析月为 2011-11，对比 2011-10。

| 月份 | 有效订单 | 销售收入 | 毛利率 | 广告花费 | 贡献利润 | 贡献利润率 |
|---|---:|---:|---:|---:|---:|---:|
| 2011-10 | 2,040 | GBP 1.15M | 40.0% | GBP 26.1k | GBP 225.1k | 19.5% |
| 2011-11 | 2,769 | GBP 1.51M | 24.4% | GBP 36.9k | GBP 88.4k | 5.9% |

核心结论：

- 销售收入增长，但贡献利润下降，说明增长质量变差；
- 高销售额品类不一定高利润，需要结合成本和费用看贡献利润；
- 广告预算不能只看 ROAS，还要结合贡献利润和库存状态；
- 库存管理要区分“快断货 SKU”和“滞销占资 SKU”。

## 主要交付物

- [Analytics Hub Streamlit 工具入口](app/streamlit_app.py)
- [系统设计说明](docs/system_design.md)
- [SKU × 地区推广优先级模型](docs/sku_region_scoring_model.md)
- [月度经营复盘](reports/monthly_business_review.md)
- [指标字典](docs/metric_dictionary.md)
- [数据字典](docs/data_dictionary.md)
- [数据模型说明](docs/data_model.md)
- [Power BI DAX 指标](powerbi/dax_measures.dax)
- [样例数据预览](data/sample)

技术复现和启动说明单独放在 [docs/reproducibility.md](docs/reproducibility.md)。

## 数据来源

UCI Machine Learning Repository: Online Retail II  
DOI: <https://doi.org/10.24432/C5CG6D>  
License: CC BY 4.0
