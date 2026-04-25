# /// script
# dependencies = [
#     "duckdb==1.5.2",
#     "marimo",
#     "pandas==3.0.2",
#     "pyarrow==24.0.0",
#     "sqlglot==30.6.0",
# ]
# requires-python = ">=3.12"
# ///

import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell
def _():
    import pandas as pd
    import marimo as mo

    sfc_licenses = pd.read_csv(mo.notebook_location()/ 'public' / 'sfc_licences_2026.csv')


    # sfc_licenses = sfc_licenses[sfc_licenses['endDate'] < '2025-01-01']
    sfc_licenses
    return mo, sfc_licenses


@app.cell(hide_code=True)
def _(mo, sfc_licenses):
    _df = mo.sql(
        f"""
        select distinct sfcid as total_professionals,
               prinCeRef as total_firms
        from sfc_licenses
        """
    )
    return


if __name__ == "__main__":
    app.run()
