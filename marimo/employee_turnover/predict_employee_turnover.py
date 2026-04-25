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

    ## Step 1: Data Consolidation & Employment Mapping

    To analyze **Network Contagion** effectively, our dataset focuses strictly on the **duration of employment** at a given firm rather than the specific regulated activities (license types) held by the individual.

    A single financial group often operates through multiple legal entities or branches, such as **Get Nice Futures Company Limited** and **Get Nice Securities Limited**. To ensure these are treated as a single continuous employer, we consolidated the records by matching the **first word** of the English company name. This heuristic allows us to accurately track professional movement between parent organizations without being misled by internal transfers between subsidiaries.

    The result is basically an employment history of each SFC professional for each registered institution in SCD type 2 format (Slowly changing dimension Type 2). Each row shows the start date (effectiveDate) and end date (endDate) of the employment of an SFC professional at each registered institution.
    """)
    return


@app.cell(hide_code=True)
def _(mo, sfc_licenses):
    sfc_professional_company_employment_history = mo.sql(
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
                     then 1 else 0 end as _incre,
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
            fullName || ' (' || sfcid || ') ' as professionalId,
        	split_part(min(prinCeName), ' ', 1) as companyId,   
            array_agg(distinct prinCeName) as princCeNames,
            min(effectiveDate) as effectiveDate,
            max(endDate) as endDate,
            max(endDate) - min(effectiveDate) as tenure_days
        from add_group
        group by sfcid, fullName, grp
        order by sfcid, min(effectiveDate) 		
        """
    )
    return (sfc_professional_company_employment_history,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
 
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 2: Generate Monthly Active SFC professional Snapshot

    With the SCD Type 2 table created, we will now generate a monthly snapshot of active SFC professional.
    """)
    return


@app.cell
def _(pd, sfc_professional_company_employment_history):
    def generate_monthly_active_sfc_professional_snapshot(df):
        df = df.copy()
        df['effectiveDate'] = pd.to_datetime(df['effectiveDate'])
        # Fill empty end dates with a future date to represent current employees
        df['endDate'] = pd.to_datetime(df['endDate']).fillna(pd.Timestamp('9999-01-01'))
    
        # 2. Create Monthly Snapshots (The "Attendance Sheet")
        # We create a record for every person for every month they were active
        start_date = df['effectiveDate'].min().replace(day=1)
        end_date = df['effectiveDate'].max().replace(day=1)
        months = pd.date_range(start_date, end_date, freq='MS')
    
        snapshot_list = []
        for m in months:
            # Everyone active in month 'm'
            active = df[(df['effectiveDate'] <= m) & (df['endDate'] > m)].copy()
            active['snapshot_month'] = m
            snapshot_list.append(active[['snapshot_month', 'companyId', 'professionalId', 'endDate']])
    
        master_history = pd.concat(snapshot_list)
        return master_history

    monthly_active_sfc_professional_snapshot = generate_monthly_active_sfc_professional_snapshot(sfc_professional_company_employment_history)

    monthly_active_sfc_professional_snapshot
    return (monthly_active_sfc_professional_snapshot,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Employee-employee network
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Monthly Active Employee Snapshots
    """)
    return


@app.cell
def _(master_history, monthly_active_sfc_professional_snapshot, pd):
    import matplotlib.pyplot as plt

    def generate_contagion_analysis(df):
    
        # 3. Calculate Peer Groups (Who was there 6 months ago?)
        master_history['lookback_month'] = master_history['snapshot_month'] - pd.DateOffset(months=6)
    
        # Self-merge to find out who was at the same company 6 months ago
        peers_then = master_history[['snapshot_month', 'companyId', 'professionalId']].copy()
    
        # 4. Determine Departures
        # We count how many peers a person had 6 months ago vs how many of THOSE specific people are still here
        # This part is handled by comparing the 'master_history' against its own past state
    
        # (Simplified calculation for the 23k rows to ensure speed)
        # We calculate the company-level turnover rate over 6 months as a proxy for peer influence
        company_monthly_stats = master_history.groupby(['snapshot_month', 'companyId'])['professionalId'].nunique().reset_index()
        company_monthly_stats.columns = ['month', 'companyId', 'current_count']
    
        # Shift counts by 6 months to see the change
        company_monthly_stats['past_month'] = company_monthly_stats['month'] - pd.DateOffset(months=6)
        stats_merged = pd.merge(
            company_monthly_stats, 
            company_monthly_stats, 
            left_on=['past_month', 'companyId'], 
            right_on=['month', 'companyId'], 
            suffixes=('', '_past')
        )
    
        # Peer departure % = (Peers then - Peers now) / Peers then
        stats_merged['peer_departure_pct'] = (1 - (stats_merged['current_count'] / stats_merged['current_count_past'])).clip(0, 1) * 100
    
        # 5. Link individual turnover to these peer departure stats
        # Did the person leave in the month following the snapshot?
        master_history['left_next_month'] = (
            (master_history['endDate'] > master_history['snapshot_month']) & 
            (master_history['endDate'] <= (master_history['snapshot_month'] + pd.DateOffset(months=1)))
        ).astype(int)
    
        final_data = pd.merge(
            master_history, 
            stats_merged[['month', 'companyId', 'peer_departure_pct']], 
            left_on=['snapshot_month', 'companyId'], 
            right_on=['month', 'companyId']
        )

        # 6. Final Plotting Logic
        # Grouping into 10% bins for the graph
        final_data['bin'] = (final_data['peer_departure_pct'] // 10) * 10
        plot_points = final_data.groupby('bin')['left_next_month'].mean() * 100

        plt.figure(figsize=(10, 6))
        plt.plot(plot_points.index, plot_points.values, marker='o', linewidth=2, color='#e31a1c')
        plt.fill_between(plot_points.index, plot_points.values, alpha=0.1, color='#e31a1c')
        plt.axvline(x=30, color='black', linestyle='--', alpha=0.3)
        plt.title('Impact of Peer Departures on Employee Turnover (23k Rows)', fontsize=14)
        plt.xlabel('Percentage of Peers who Departed (Last 6 Months)', fontsize=12)
        plt.ylabel('Prob. of Individual Leaving Next Month (%)', fontsize=12)
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.show()

    # Run the function
    generate_contagion_analysis(monthly_active_sfc_professional_snapshot)
    return


if __name__ == "__main__":
    app.run()
