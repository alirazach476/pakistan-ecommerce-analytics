# Pakistan E-commerce Power BI Project

## Open in Power BI Desktop

1. Install [Power BI Desktop](https://apps.microsoft.com/detail/9ntxr16hnw1t) from Microsoft Store.
2. Open `PakistanEcommerce.pbip` in this folder.
3. When prompted, set PostgreSQL credentials:
   - Server: `127.0.0.1:59612`
   - Database: `pakistan_ecommerce`
   - User: `analytics`
4. Click **Transform Data** > **Refresh** if tables are empty on first load.

## Included

- Semantic model (`PakistanEcommerce.SemanticModel`) — analytics schema tables + KPI measures
- Report (`PakistanEcommerce.Report`) — 6 pages; Executive Overview has KPI cards
- Star-schema relationships pre-defined

## Regenerate

```powershell
$env:PYTHONPATH = (Get-Location).Path
python scripts/generate_powerbi_project.py
```

Ensure PostgreSQL is running and dbt models exist in `analytics` schema.
