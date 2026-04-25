# /// script
# dependencies = [
#     "altair==6.1.0",
#     "duckdb==1.5.2",
#     "marimo",
#     "matplotlib==3.10.9",
#     "networkx==3.6.1",
#     "numpy==2.4.4",
#     "pandas==3.0.2",
#     "pyarrow==24.0.0",
#     "sqlglot==30.6.0",
# ]
# requires-python = ">=3.12"
# ///

import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Employee Turnover

    ### As explained by Network Contagion Effect and illustrated with public HK SFC licensed professional data from 2003 to 2026
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Dataset
    The data is obtained here: https://www.kaggle.com/datasets/gautiermarti/hk-sfc-register. It shows the start and end date of each SFC licensee professional and the employer he/she is working for. Each row is granular to the level of `regulated Activity`.
    ## Data Dictionary

    - effectiveDate: Start date of the license or regulated activity.
    - endDate: Termination or expiration date of the license or activity.
    - fullname: Full legal name of the license holder (given and family names).
    - sfcid: Unique ID assigned by the SFC to identify each licensee.
    - lcRole: Licensee’s role within the SFC framework: RE: Representative authorized to carry out regulated activities under supervision; RO: Responsible Officer, authorized to supervise regulated activities.
    - prinCeName: Official English name of the firm employing the licensee.
    - prinCeNameChin: Official Chinese name of the firm.
    - prinCeRef: Unique ID assigned by the SFC to each licensed firm.
    - regulatedActivity.status: Current status of the regulated activity: R: Registered/Active; A: Archived/Inactive.
    - regulatedActivity.actType: Numerical code for the type of regulated activity (e.g., 1: Dealing in Securities; 2: Dealing in Futures Contracts; 3: Leveraged Foreign Exchange Trading; etc.).
    - regulatedActivity.actDesc: Description of the regulated activity in English.
    - regulatedActivity.cactDesc: Corresponding description in Chinese.
    """)
    return


@app.cell
def _():
    import pandas as pd
    import marimo as mo
    import altair as alt


    def load_dataset():
        sfc_licenses = pd.read_csv(
            mo.notebook_location() / "public" / "sfc_licences_2026.csv"
        )

        # 1. Convert to datetime objects first (keep as datetime64[ns] for easier manipulation)
        sfc_licenses["effectiveDate"] = pd.to_datetime(
            sfc_licenses["effectiveDate"]
        )
        sfc_licenses["endDate"] = pd.to_datetime(sfc_licenses["endDate"])

        # 2. Create extra columns snapped to Jan 1st of the respective year
        # This replaces the need for .replace(month=1, day=1)
        sfc_licenses["license_year_created"] = (
            sfc_licenses["effectiveDate"].dt.to_period("Y").dt.to_timestamp()
        )
        sfc_licenses["license_year_terminated"] = (
            sfc_licenses["endDate"].dt.to_period("Y").dt.to_timestamp()
        )

        sfc_licenses["effectiveDate"] = sfc_licenses["effectiveDate"].dt.date
        sfc_licenses["endDate"] = sfc_licenses["endDate"].dt.date

        return sfc_licenses

    raw_sfc_licenses = load_dataset()

    raw_sfc_licenses
    return alt, mo, pd, raw_sfc_licenses


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Statistics: SFC Licensing creation and termination
    """)
    return


@app.cell
def _(alt, mo, pd, raw_sfc_licenses):
    # 1-4. (Your existing data processing)

    unique_stints = raw_sfc_licenses.drop_duplicates(
        subset=["sfcid", "effectiveDate", "endDate"]
    ).copy()


    created = (
        unique_stints.groupby("license_year_created")
        .size()
        .reset_index(name="count")
    )

    created.columns = ["year", "count"]

    created["status"] = "Created"


    terminated = unique_stints.dropna(subset=["license_year_terminated"]).copy()

    terminated = (
        terminated.groupby("license_year_terminated")
        .size()
        .reset_index(name="count")
    )

    terminated.columns = ["year", "count"]

    terminated["status"] = "Terminated"


    plot_data = pd.concat([created, terminated])

    # --- NEW: LOGIC TO FIND CROSSOVER POINTS ---
    # ... (Keep your existing data processing up to pivot)

    # Pivot data to compare Created vs Terminated side-by-side
    wide_data = (
        plot_data.pivot(index="year", columns="status", values="count")
        .fillna(0)
        .reset_index()
    )

    # --- NEW: CALCULATE BOUNDARIES FOR VERTICAL SLICES ---
    # ... (Keep your existing data processing up to pivot)

    # Pivot data to compare Created vs Terminated side-by-side
    wide_data = (
        plot_data.pivot(index="year", columns="status", values="count")
        .fillna(0)
        .reset_index()
    )

    # --- FIX: DATE-AWARE OFFSET ---
    # Use pd.DateOffset to safely add 1 year to your datetime objects
    wide_data["next_year"] = wide_data["year"] + pd.DateOffset(years=1)

    # Define crossover logic
    wide_data["diff"] = wide_data["Created"] - wide_data["Terminated"]
    wide_data["prev_diff"] = wide_data["diff"].shift(1)
    crossovers = wide_data[wide_data["diff"] * wide_data["prev_diff"] < 0]

    # --- 5. CREATE THE LAYERED CHART ---

    # Base X-axis
    base = alt.Chart(plot_data).encode(
        x=alt.X("year:T", title="Year", axis=alt.Axis(format="%Y"))
    )

    # Shading: Full vertical slices
    shading = (
        alt.Chart(wide_data)
        .transform_filter("datum.Created > datum.Terminated")
        .mark_rect(opacity=0.15, color="#1f77b4")
        .encode(
            x="year:T",
            x2="next_year:T",
            y=alt.value(0),  # Top of chart
            y2=alt.value(400),  # Bottom of chart (adjust if height is different)
        )
    )

    # Line chart
    lines = base.mark_line(point=True).encode(
        y=alt.Y("count:Q", title="Number of Licenses"),
        color=alt.Color(
            "status:N",
            title="Action",
            scale=alt.Scale(
                domain=["Created", "Terminated"], range=["#1f77b4", "#d62728"]
            ),
        ),
        tooltip=[
            alt.Tooltip("year:T", format="%Y", title="Year"),
            "status",
            "count",
        ],
    )

    # Crossover rules
    rules = (
        alt.Chart(crossovers)
        .mark_rule(color="gray", strokeDash=[4, 4], size=1.5)
        .encode(
            x="year:T",
            tooltip=[
                alt.Tooltip("year:T", format="%Y", title="Intersection Year")
            ],
        )
    )

    # Final Layering
    chart = (
        (shading + lines + rules)
        .properties(
            title="Yearly License Trends (Growth Periods Shaded)",
            width=600,
            height=400,
        )
        .interactive()
    )

    mo.vstack(
        [
            mo.md(
                """
            The temporal dynamics of license activity from 2003 to 2026 show that 
            creations (blue) generally exceed terminations (red), indicating 
            consistent net industry expansion. While the market typically trends 
            upward, significant global events like the 2009 Global Financial Crisis 
            and the 2020 COVID-19 pandemic caused issuance and termination to reach 
            parity. This convergence highlights periods of stagnation and stress 
            in the financial labor market, where new growth was offset by 
            license cancellations.
            """
            ),
            chart,
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Data Preprocessing

    For the purpose of this study on Network Contagion, we are not concerned with the type of reglated activity permitted by the license. We will concern ourselves with the employment duration of the SFC licensee at the specific company.

    The same company may have different branches and thus having different prinCeRef. An Example is

    - Get Nice Futures Company Limited
    - Get Nice Securities Limited

    To make sure a professional is considered to be working for the same company (but different branches), I use the first word in the english name for string matching.
    """)
    return


@app.cell(hide_code=True)
def _(mo, raw_sfc_licenses):
    sfc_licenses = mo.sql(
        f"""
        -- Group all consecutive rows for the same person, of the same company (determined by the first word of the company name) into the same group


        with add_incre as (
            select case when lag( split_part(prinCeName, ' ', 1) ) over(partition by sfcid order by id) != split_part(prinCeName, ' ', 1) then 1 else 0 end as _incre, split_part(prinCeName, ' ', 1), * from raw_sfc_licenses
            ), add_group as (

        select 
               sum(_incre) over(partition by sfcid order by effectiveDate asc) as grp, 
               id,
               _incre,
                fullName,
            prinCeName,
            prinCeRef,
            effectiveDate,
    
               * from add_incre
        ) 
            -- select * from add_group
            select grp,
                   sfcid,
                   fullName,
                   array_agg(distinct prinCeName) as princCeNames,
                   min(effectiveDate) as effectiveDate,
                   max(endDate) as endDate 
            from add_group
            -- where sfcid = 'AAY115'
            group by grp, sfcid, fullName

        order by sfcid, effectiveDate
        limit 200
        """
    )
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Employee-employee network
    """)
    return


if __name__ == "__main__":
    app.run()
