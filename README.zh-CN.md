# 跨境电商利润与库存分析项目

中文 | [English](README.md)

这是一个面向“跨境电商方向数据分析师”岗位的作品集项目。项目从真实公开订单数据出发，补充可复现的模拟经营数据，形成完整的数据分析闭环：数据下载、清洗、建模、指标口径、SQL 分析、Power BI 建模思路、月度经营复盘和面试讲解稿。

> 数据边界说明：订单交易层使用 UCI Online Retail II 真实公开数据；商品成本、平台费、支付费、物流费、广告投放和库存快照为可复现的模拟扩展数据。模拟数据只用于展示分析方法，不代表任何真实公司的经营结果。

## 这个项目解决什么问题

跨境电商运营、市场、财务和供应链团队通常需要回答这些问题：

1. 哪些市场、渠道、品类和 SKU 带来了销售增长？
2. 销售增长有没有转化为毛利和贡献利润？
3. 哪些广告组合 ROAS 低，需要控预算或重新分配？
4. 哪些 SKU 有缺货风险，哪些 SKU 正在滞销占用现金？
5. 下个月应该如何调整广告预算、商品结构和补货策略？

## 岗位匹配点

这个项目对应招聘 JD 中的核心要求：

| 岗位要求 | 项目中的体现 |
|---|---|
| 周报/月报经营分析 | `reports/monthly_business_review.md` 输出月度经营复盘 |
| 销售、毛利、费用、净利/贡献利润 | `fact_order_profit` 与 SQL KPI 分析覆盖收入、成本、费用、毛利、贡献利润 |
| 渠道、店铺、SKU 维度管理报表 | 使用市场、渠道、品类、SKU 分层分析 |
| 广告投放费用利润分析 | `fact_ad_spend_monthly` 计算广告花费、归因收入、ROAS |
| 库存周转、缺货、滞销分析 | `fact_inventory_monthly` 计算周转天数、缺货标记、滞销标记 |
| ERP/平台/财务/库存多源整合 | 用订单、商品、市场、广告、库存多张表模拟真实公司数据结构 |
| Excel / Power Query / BI 面板能力 | 提供 Power BI 数据模型、DAX 指标和看板设计说明 |
| SQL 查询与聚合能力 | `sql/` 中提供 KPI、利润和库存分析 SQL |

## 项目交付物

- 可复现的数据下载和清洗脚本。
- 真实订单数据的数据质量画像。
- 商品成本、平台费、支付费、物流费、广告和库存模拟扩展表。
- SQLite 数据库，便于本地 SQL 分析。
- SQL 分析脚本：KPI、利润、库存。
- Power BI 数据模型说明和 DAX 指标。
- 管理层月度经营复盘报告。
- 面试讲解稿，帮助解释项目价值和数据边界。
- GitHub 小样例数据，便于面试官快速查看表结构。

## 数据处理流程

```text
UCI Online Retail II 原始 Excel
  -> 清洗为订单明细 fact_order_lines.csv
  -> 生成商品、市场、利润、广告、库存扩展表
  -> 写入 ecommerce_analytics.sqlite
  -> SQL 分析 + 月度经营复盘 + Power BI 建模
```

## 仓库结构

```text
crossborder-ecommerce-analytics/
├─ README.md
├─ README.zh-CN.md
├─ requirements.txt
├─ data/
│  ├─ raw/              # 不提交；脚本下载原始数据到这里
│  ├─ processed/        # 不提交；脚本生成完整 CSV 和 SQLite
│  └─ sample/           # 提交小样例 CSV，供 GitHub 预览
├─ scripts/
│  ├─ download_source_data.py
│  ├─ prepare_orders.py
│  ├─ generate_extensions.py
│  ├─ build_database.py
│  ├─ run_analysis.py
│  ├─ export_samples.py
│  ├─ validate_source_data.py
│  └─ validate_data.py
├─ sql/
│  ├─ 01_schema.sql
│  ├─ 02_kpi_analysis.sql
│  ├─ 03_profit_analysis.sql
│  └─ 04_inventory_analysis.sql
├─ docs/
│  ├─ data_dictionary.md
│  ├─ metric_dictionary.md
│  ├─ data_model.md
│  ├─ interview_guide.md
│  ├─ source_and_license.md
│  ├─ source_profile.json
│  ├─ extension_profile.json
│  └─ validation_results.json
├─ powerbi/
│  ├─ README.md
│  └─ dax_measures.dax
├─ reports/
│  ├─ monthly_business_review.md
│  └─ analysis_summary.json
└─ tests/
   └─ test_data_quality.py
```

## 如何运行

```powershell
python -m pip install -r requirements.txt
python scripts/download_source_data.py
python scripts/prepare_orders.py
python scripts/validate_source_data.py
python scripts/generate_extensions.py
python scripts/build_database.py
python scripts/run_analysis.py
python scripts/validate_data.py
python scripts/export_samples.py
```

说明：

- `data/raw/` 和 `data/processed/` 中的完整数据不提交到 Git，因为文件较大且可以通过脚本重建。
- `data/sample/` 中提交了小样例 CSV，方便 GitHub 访问者快速查看字段结构。

## 核心数据表

| 表名 | 粒度 | 用途 |
|---|---|---|
| `fact_order_lines` | 交易明细行 | 清洗后的真实公开订单数据 |
| `dim_product` | SKU | 商品分类、SKU 分层、模拟单位成本 |
| `dim_market` | 国家 | 市场区域、渠道、费率和物流假设 |
| `fact_order_profit` | 交易明细行 | 收入、成本、费用、毛利、广告前贡献利润 |
| `fact_ad_spend_monthly` | 月份-市场-渠道-品类 | 模拟广告花费、归因收入、ROAS |
| `fact_inventory_monthly` | 月份-SKU | 库存、周转天数、缺货和滞销标记 |

## 核心指标口径

| 指标 | 口径 |
|---|---|
| 销售收入 | 有效销售订单行收入 |
| 毛利 | 销售收入 - 商品成本 |
| 毛利率 | 毛利 / 销售收入 |
| 广告前贡献利润 | 毛利 - 平台费 - 支付费 - 物流费 |
| 贡献利润 | 广告前贡献利润 - 广告花费 |
| 贡献利润率 | 贡献利润 / 销售收入 |
| ROAS | 广告归因收入 / 广告花费 |
| 库存周转天数 | 平均库存成本 / 销售成本 × 天数 |
| 缺货标记 | 期末库存低于短期需求阈值 |
| 滞销标记 | 周转天数较高且仍有较多库存 |

完整指标说明见：[docs/metric_dictionary.md](docs/metric_dictionary.md)

## 最新本地运行结果

当前脚本生成的数据规模：

- 订单明细：1,067,371 行。
- 商品维表：4,916 行。
- 市场维表：43 行。
- 利润事实表：1,067,371 行。
- 广告月表：700 行。
- 库存月表：19,314 行。
- 数据校验全部通过。

月度经营复盘使用 2011-11 作为最新完整月份，并与 2011-10 对比。原始数据中还包含 2011-12 的部分月份数据，但为了避免环比误导，月报没有把不完整月份作为主分析期。

## Power BI 看板设计

建议做 4 页：

1. 经营总览：销售收入、有效订单、毛利率、贡献利润、趋势。
2. SKU / 品类利润：品类、SKU 分层、市场和渠道的利润表现。
3. 广告效率：广告花费、归因收入、ROAS、低效广告组合。
4. 库存行动清单：库存金额、周转天数、缺货风险、滞销 SKU、补货建议。

## 面试时怎么讲

可以用这段 60 秒介绍：

> 我做了一个跨境电商数据分析项目。订单交易层使用 UCI Online Retail II 真实公开数据，公开数据没有成本、广告和库存，所以我额外构建了明确标注的模拟经营层，包括商品成本、平台费、物流费、广告投放和库存快照。项目目标是复现跨境电商数据分析师的实际工作：月度销售和利润复盘、SKU 和渠道利润分析、广告 ROAS 评估、库存周转和缺货/滞销预警，最后输出可执行的运营建议。

面试中要主动说明：

- 真实数据：订单交易明细来自 UCI 公开数据。
- 模拟数据：成本、广告、库存是为了展示分析方法而构建。
- 真实公司落地：应替换为 ERP、财务、广告平台、平台后台和 WMS 仓库数据。
- 项目价值：不是只做图表，而是能把数据转化为预算、补货、清库存和利润优化动作。

详细面试讲法见：[docs/interview_guide.md](docs/interview_guide.md)

## 数据来源

UCI Machine Learning Repository: Online Retail II  
DOI: <https://doi.org/10.24432/C5CG6D>  
License: CC BY 4.0
