# Analytics Hub System Design

## Purpose

The Analytics Hub turns the portfolio from a static analysis case into a reusable operating-review tool prototype. It is designed to show that the same analytical logic can be connected to platform exports or future APIs.

## MVP Flow

```text
CSV / platform export / future API
  -> schema validation
  -> standardized profit, ad, and inventory tables
  -> KPI engine
  -> automated diagnostics
  -> Streamlit operating dashboard
  -> downloadable monthly review
```

## Current input modes

- Built-in generated dataset when local processed files exist.
- Committed sample dataset when full data is not available.
- Uploaded CSV files from the Streamlit sidebar.

## Future API integration points

Connector stubs are included for future extension:

- `connectors/shopify_connector_stub.py`
- `connectors/amazon_connector_stub.py`
- `connectors/csv_connector.py`

In a real company, these connector stubs can be replaced with:

- Shopify Admin API;
- Amazon SP-API and Amazon Ads API;
- TikTok Shop API;
- ERP product-cost export;
- WMS inventory snapshot;
- finance settlement export.

## Analytical modules

| Module | Responsibility |
|---|---|
| `analytics_hub/io.py` | Load default/sample/uploaded data and validate required columns |
| `analytics_hub/kpi_engine.py` | Calculate monthly KPI scorecards, category profit, and market profit |
| `analytics_hub/diagnostics.py` | Find low-margin categories, low-ROAS campaigns, and inventory action items |
| `analytics_hub/report_generator.py` | Generate downloadable Markdown business reviews |
| `app/streamlit_app.py` | Web interface for uploads, KPI review, diagnostics, and report export |

## Hiring-review positioning

This is intentionally an MVP, not a production SaaS product. It demonstrates the system thinking expected from an e-commerce data analyst:

- standardize messy platform data;
- enforce metric definitions;
- automate recurring KPI reporting;
- detect operating exceptions;
- export a business-readable review.
