# 数据来源与许可证

## 原始交易数据

- 数据集：Online Retail II
- 发布方：UCI Machine Learning Repository
- 作者：Daqing Chen
- DOI：<https://doi.org/10.24432/C5CG6D>
- 数据页面：<https://archive.ics.uci.edu/dataset/502/online+retail+ii>
- 下载地址：<https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip>
- 许可证：Creative Commons Attribution 4.0 International（CC BY 4.0）
- 下载包 SHA-256：`572e36277c2390fbfde10664750731e0a86f55e33470d91919085f0408e67bfb`

该数据包含一家英国非门店零售企业在 2009 年 12 月至 2011 年 12 月期间的交易记录，覆盖订单、商品、数量、价格、客户和国家。

## GitHub 分发策略

仓库不直接提交约 43.5 MB 的原始 Excel 文件。使用者运行：

```powershell
python scripts/download_source_data.py
```

脚本会从 UCI 下载数据、验证 SHA-256 并解压。这样可以：

- 保留权威来源和许可信息。
- 避免仓库包含大型原始文件。
- 保证数据处理流程可复现。
- 降低误传非公开数据的风险。

## 模拟扩展数据

UCI 数据不包含以下目标岗位需要的经营字段：

- 商品采购成本
- 平台费和支付费
- 物流费
- 广告消耗与广告归因
- 库存与在途库存

后续将基于公开交易结构生成独立扩展表。所有扩展字段均标记为 `synthetic`，报告中不会把模拟利润、广告或库存结果描述为真实企业业绩。

## 引用

Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning Repository. <https://doi.org/10.24432/C5CG6D>

