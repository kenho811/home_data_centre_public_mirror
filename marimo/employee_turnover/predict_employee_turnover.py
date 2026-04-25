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

    sfc_licenses = load_dataset()

    sfc_licenses
    return alt, mo, pd, sfc_licenses


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## YoY SFC License Creation and Termination (2003–2026)
    """)
    return


@app.cell
def _(alt, mo, pd, sfc_licenses):
    # 1-4. (Your existing data processing)

    unique_stints = sfc_licenses.drop_duplicates(
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
            title="YoY SFC License Trends (Growth Periods Shaded)",
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

    ## Data Consolidation & Employment Mapping

    To analyze **Network Contagion** effectively, our dataset focuses strictly on the **duration of employment** at a given firm rather than the specific regulated activities (license types) held by the individual.

    A single financial group often operates through multiple legal entities or branches, such as **Get Nice Futures Company Limited** and **Get Nice Securities Limited**. To ensure these are treated as a single continuous employer, we consolidated the records by matching the **first word** of the English company name. This heuristic allows us to accurately track professional movement between parent organizations without being misled by internal transfers between subsidiaries.
    """)
    return


@app.cell(hide_code=True)
def _(mo, sfc_licenses):
    _df = mo.sql(
        f"""
        -- Step 1: Merge overlapping date ranges for the same sfcid and prinCeName.
        -- This collapses multiple licenses at the same company into single continuous periods.
        with merged_licenses as (
            select 
                sfcid, 
                fullName, 
                prinCeName, 
                min(effectiveDate) as effectiveDate, 
                max(endDate) as endDate
            from (
                select 
                    *,
                    sum(is_new_start) over (partition by sfcid, prinCeName order by effectiveDate, endDate) as overlap_grp
                from (
                    select 
                        sfcid, fullName, prinCeName, effectiveDate, endDate,
                        case when effectiveDate <= max(endDate) over (
                            partition by sfcid, prinCeName 
                            order by effectiveDate, endDate 
                            rows between unbounded preceding and 1 preceding
                        ) then 0 else 1 end as is_new_start
                    from sfc_licenses
                ) t1
            ) t2
            group by sfcid, fullName, prinCeName, overlap_grp
        ),
        -- Step 2: Group consecutive records where the company's first word is the same.
        add_incre as (
            select 
                *,
                case when lag(split_part(prinCeName, ' ', 1)) over (partition by sfcid order by effectiveDate, endDate, prinCeName) 
                     is distinct from split_part(prinCeName, ' ', 1) 
                     then 1 else 0 end as _incre
            from merged_licenses
        ),
        add_group as (
            select 
                *,
                sum(_incre) over (partition by sfcid order by effectiveDate, endDate, prinCeName rows unbounded preceding) as grp
            from add_incre
        )
        -- Step 3: Final aggregation
        select 
            sfcid,
            fullName,
            fullName || ' (' || sfcid || ') ' as professional_id,
            array_agg(distinct prinCeName) as princCeNames,
            min(effectiveDate) as effectiveDate,
            max(endDate) as endDate,
            max(endDate) - min(effectiveDate) as tenure_days
        from add_group
        group by sfcid, fullName, grp
        order by sfcid, min(effectiveDate)
        limit 500;
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Employee-employee network
    """)
    return


if __name__ == "__main__":
    app.run()
