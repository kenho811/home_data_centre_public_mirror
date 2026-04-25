# /// script
# dependencies = [
#     "altair==6.1.0",
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
    import altair as alt

    def load_dataset():  
        sfc_licenses = pd.read_csv(mo.notebook_location() / 'public' / 'sfc_licences_2026.csv')

        # 1. Convert to datetime objects first (keep as datetime64[ns] for easier manipulation)
        sfc_licenses['effectiveDate'] = pd.to_datetime(sfc_licenses['effectiveDate'])
        sfc_licenses['endDate'] = pd.to_datetime(sfc_licenses['endDate'])

        # 2. Create extra columns snapped to Jan 1st of the respective year
        # This replaces the need for .replace(month=1, day=1)
        sfc_licenses['license_year_created'] = sfc_licenses['effectiveDate'].dt.to_period('Y').dt.to_timestamp()
        sfc_licenses['license_year_terminated'] = sfc_licenses['endDate'].dt.to_period('Y').dt.to_timestamp()
    
        # 3. If you strictly need .date() objects (Python datetime.date) instead of pandas timestamps:
        sfc_licenses['effectiveDate'] = sfc_licenses['effectiveDate'].dt.date
        sfc_licenses['endDate'] = sfc_licenses['endDate'].dt.date
        sfc_licenses['license_year_created'] = sfc_licenses['license_year_created'].dt.date
        sfc_licenses['license_year_terminated'] = sfc_licenses['license_year_terminated'].dt.date
    
        return sfc_licenses



    sfc_licenses = load_dataset()
    sfc_licenses
    return alt, mo, pd, sfc_licenses


@app.cell(hide_code=True)
def _(mo, sfc_licenses):
    _df = mo.sql(
        f"""
        select min(least(effectiveDate, endDate)) as dataset_start_date, 
               max(greatest(effectiveDate, endDate)) as dataset_end_date, 
               count(distinct sfcid) as total_professionals,
               count(distinct prinCeRef) as total_firms,
               count(*) as employment_records,
               avg(endDate - effectiveDate)/365 as average_license_tenure_in_year
        from sfc_licenses
        """
    )
    return


@app.cell
def _(alt, pd, sfc_licenses):
    # 1. Deduplicate to get unique license stints per person
    # We use the raw dates to ensure we correctly identify unique periods
    unique_stints = sfc_licenses.drop_duplicates(subset=['sfcid', 'effectiveDate', 'endDate']).copy()

    # 2. Aggregate counts for Created licenses
    created = unique_stints.groupby('license_year_created').size().reset_index(name='count')
    created.columns = ['year', 'count']
    created['status'] = 'Created'

    # 3. Aggregate counts for Terminated licenses (ignoring active licenses where endDate is null)
    terminated = unique_stints.dropna(subset=['license_year_terminated']).copy()
    terminated = terminated.groupby('license_year_terminated').size().reset_index(name='count')
    terminated.columns = ['year', 'count']
    terminated['status'] = 'Terminated'

    # 4. Combine into a long-format dataframe for Altair
    plot_data = pd.concat([created, terminated])

    # 5. Create the Altair Chart
    chart = alt.Chart(plot_data).mark_line(point=True).encode(
        x=alt.X('year:T', title='Year', axis=alt.Axis(format='%Y')),
        y=alt.Y('count:Q', title='Number of Licenses'),
        color=alt.Color('status:N', 
                        title='Action',
                        scale=alt.Scale(domain=['Created', 'Terminated'], 
                                        range=['#1f77b4', '#d62728'])),
        tooltip=[alt.Tooltip('year:T', format='%Y', title='Year'), 'status', 'count']
    ).properties(
        title='Yearly License Creation and Termination Trends',
        width=600,
        height=400
    ).interactive()

    # If using marimo, simply return the chart object at the end of a cell
    chart
    return


if __name__ == "__main__":
    app.run()
