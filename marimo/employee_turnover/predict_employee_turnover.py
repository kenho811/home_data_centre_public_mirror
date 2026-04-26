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
#     "scikit-learn==1.8.0",
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
    # Network Contagion in Financial Labor Markets
    ### Predicting Employee Turnover via the Hong Kong SFC Public Register (2003–2026)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Researching Network Contagion: The SFC Public Register Dataset

    This dataset is an empirical foundation for analyzing employee turnover and professional network effects within one of the world's premier financial hubs. It originates from the public register maintained by the **Hong Kong Securities and Futures Commission (SFC)**, which has systematically recorded licensed individuals, corporations, and registered institutions since the implementation of the **Securities and Futures Ordinance (SFO)** on 1 April 2003.

    #### **Research Utility**
    This data is primarily utilized to explore **network contagion**—how the movement of peers within a professional network influences individual turnover.


    ---

    ### 📖 Data Dictionary

    * **`fullname`**: Full legal name of the license holder.
    * **`sfcid`**: A unique, permanent identifier assigned by the SFC to each licensee.
    * **`lcRole`**: Licensee’s role (e.g., **RE**: Representative; **RO**: Responsible Officer authorized to supervise activities).
    * **`prinCeName` / `prinCeNameChin`**: Official English and Chinese names of the employing firm.
    * **`prinCeRef`**: Unique central entity ID assigned by the SFC to each licensed firm.
    * **`regulatedActivity.actType` & `actDesc`**: Numerical codes and descriptions for the types of regulated activities authorized (e.g., Type 1: Dealing in Securities; Type 9: Asset Management).
    * **`regulatedActivity.status`**: Current status of the activity (**R**: Registered/Active; **A**: Archived/Inactive).
    * **`effectiveDate`**: Start date of the specific license or regulated activity.
    * **`endDate`**: Termination or expiration date of the license or affiliation.
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
            ## YoY SFC License Creation and Termination (2003–2026)
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

    This differs from the methodology in the research paper, as evident from the statistics summary below.

    Rationale is that, a single financial group often operates through multiple legal entities or branches, such as **Get Nice Futures Company Limited** and **Get Nice Securities Limited**. To ensure these are treated as a single continuous employer, we consolidated the records by matching the **first word** of the English company name. This heuristic allows us to accurately track professional movement between parent organizations without being misled by internal transfers between subsidiaries.

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
def _(mo, sfc_professional_company_employment_history):
    _df = mo.sql(
        f"""
        SELECT 
            -- 1. Total Professionals
            COUNT(DISTINCT sfcid) AS total_professionals,

            -- 2. Total Firms
            COUNT(DISTINCT companyId) AS total_firms,

            -- 3. Employment Records
            COUNT(*) AS employment_records,

            -- 4. Median license tenure (converted from days to years)
            ROUND(MEDIAN(tenure_days) / 365.25, 1) AS median_license_tenure_years,

            -- 5. Monthly turnover rate
            ROUND(
                (COUNT(endDate) * 100.0) / (SUM(tenure_days) / 30.44), 
                1
            ) AS monthly_turnover_rate_pct,

            -- 6. Median number of employees per firm
            (SELECT MEDIAN(emp_count) 
             FROM (
                 SELECT companyId, COUNT(DISTINCT sfcid) AS emp_count 
                 FROM sfc_professional_company_employment_history 
                 GROUP BY companyId
             ) AS firm_stats
            ) AS median_employees_per_firm

        FROM sfc_professional_company_employment_history;
        """
    )

    # Extract values for the display
    stats = _df.iloc[0]
    stats_table = mo.ui.table(
        _df
    )

    # Reference image from research
    img = mo.image(
        src=mo.notebook_location() / "public" / "sfc_data_statistics.jpg", 

    )

    # Final Layout
    mo.vstack([
        mo.md(
        f"""
        ## Statistcs Comparison
        """),
        img,
        stats_table,
        mo.md(
        f"""
        **Analysis of Methodology Differences:**
        The differences between these results and the research table are primarily due to the **Corporate Group Consolidation** preprocessing and the extended observation window. By grouping entities by the first word of their name (e.g., merging "Get Nice Securities" and "Get Nice Futures"), internal transfers within the same financial group are no longer counted as new employment records or exits. This leads to a significant reduction in **Employment Records** and a corresponding increase in **Median License Tenure**, as professional stints are viewed as continuous across parent organizations rather than fragmented across subsidiaries. 

        Furthermore, while the original research statistics covered the period from **2003–2024**, this updated analysis incorporates data up to **2026**, accounting for the higher count of **Total Professionals** ({int(stats['total_professionals']):,}) and capturing more recent market volatility in the turnover metrics.
        """
        )
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
 
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 2: Generate Monthly Active SFC professional Snapshot

    Now we will transform SCD Type 2 table into a monthly snapshot of active SFC professional.

    Here's a summary.

    | Feature | SCD Type 2 (Source) | Monthly Snapshot (Target) |
    | :--- | :--- | :--- |
    | **Row Meaning** | A version of a record. | The state of a record for each month. |
    | **Granularity** | Event-based (new row on change). | Time-based (new row every month). |
    | **Storage** | Efficient (only stores changes). | Heavy (duplicates data for every month). |
    | **Querying** | Harder (requires range logic). | Easiest (filter by a single month). |
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

        monthly_active_sfc_professional_snapshot = pd.concat(snapshot_list, ignore_index=True)


        return monthly_active_sfc_professional_snapshot
    

    monthly_active_sfc_professional_snapshot = generate_monthly_active_sfc_professional_snapshot(sfc_professional_company_employment_history)

    return (monthly_active_sfc_professional_snapshot,)


@app.cell(hide_code=True)
def _(alt, mo, monthly_active_sfc_professional_snapshot, pd):
    active_sfc_professional_by_month = mo.sql(
        f"""
        select
            snapshot_month,
            count(*) as active_sfc_professional
        from
            monthly_active_sfc_professional_snapshot
        group by
            1
        """
    )


    # Assuming active_sfc_professional_by_month is your DataFrame
    # Ensure the snapshot_month is in datetime format for proper temporal scaling
    active_sfc_professional_by_month['snapshot_month'] = pd.to_datetime(active_sfc_professional_by_month['snapshot_month'])

    # Create the bar chart
    _chart = alt.Chart(active_sfc_professional_by_month).mark_bar().encode(
        x=alt.X('snapshot_month:T', title='Snapshot Month'),
        y=alt.Y('active_sfc_professional:Q', title='Active SFC Professionals'),
        tooltip=[
            alt.Tooltip('snapshot_month:T', title='Month'),
            alt.Tooltip('active_sfc_professional:Q', title='Count')
        ]
    ).properties(
        title='Active SFC Professionals by Month',
        width=800,
        height=400
    ).interactive()

    # To display or save the chart



    mo.vstack(
        [
            mo.md(
                """
            ## Month-over-month Active SFC professionals (2003–2026)

            The bar chart of active SFC professionals reflects a resilient but evolving financial labor market between 2004 and 2026. The data aligns with the observation that the industry has seen consistent net expansion for the majority of the last two decades, characterized by the steady climb from approximately 20,000 professionals to a peak of nearly 40,000. This long-term growth supports the premise that new license creations have generally outpaced terminations over this extended period.

            However, the chart also validates the impact of external stressors on market momentum. The stagnation observed around 2009 and the more recent plateau starting in 2020 directly mirror the periods where license issuance and termination reached parity. Following the 2020 peak, the slight decline in the total count of active professionals through 2026 suggests a more sustained period of industry contraction or consolidation, where the balance has shifted toward terminations. This recent trend emphasizes how global events can transition the market from a state of steady growth into a phase of significant labor market stress and stagnation.
            """
            ),
            _chart,
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Step 3: Feature Engineering
    ---------------------------

    To predict the probability of turnover, we need to define exactly what we are trying to forecast and which signals might tip us off. This section adds the following features to the dataset:

    ### 1. **`left_next_month`** (Dependent Variable)

    -   **Definition**: A binary flag (0 or 1) indicating whether an employee departs the company in the month immediately following the current snapshot.

    -   **Description**: This is our "ground truth" or target variable. It is calculated by comparing the professional's `endDate` against the current `snapshot_month`. If the end date falls within the next 30-day window, the value is 1; otherwise, it is 0.

    ### 2. **`pct_departed_staff_in_past_{num_past_months}_months`** (Independent Variable / Predictor)

    -   **Definition**: The percentage of the specific cohort of staff present $X$ months ago who are no longer with the company in the current month.

    -   **Description**: This feature serves as a leading indicator of "social contagion" or organizational instability. Unlike simple headcount changes, this metric performs a row-level lookup on unique IDs to track the actual attrition of a specific peer group.

        -   **High values** suggest a "sinking ship" scenario where established peers are leaving, which may increase the likelihood of the remaining staff departing.

    -   **Low values** suggest a stable environment with high peer retention.
    """)
    return


@app.cell
def _(monthly_active_sfc_professional_snapshot, pd):
    def add_left_next_momth(monthly_active_sfc_professional_snapshot):
        # add `left_next_month` to indicate if the professional will leave within the coming month
        monthly_active_sfc_professional_snapshot['left_next_month'] = (
            (monthly_active_sfc_professional_snapshot['endDate'] > monthly_active_sfc_professional_snapshot['snapshot_month']) & 
            (monthly_active_sfc_professional_snapshot['endDate'] <= (monthly_active_sfc_professional_snapshot['snapshot_month'] + pd.DateOffset(months=1)))
        ).astype(int)

        return monthly_active_sfc_professional_snapshot


    def add_departure_in_past_x_months(monthly_active_sfc_professional_snapshot, num_past_months, col_name):
 
        df = monthly_active_sfc_professional_snapshot
        df['snapshot_month'] = pd.to_datetime(df['snapshot_month'])
    
        # 1. Identify the "Historical Cohort"
        # This is the list of people at each company at every month in the history.
        historical_cohorts = df[['snapshot_month', 'companyId', 'professionalId']].drop_duplicates()
    
        # 2. Align the Past with the Present
        # We shift the date of the cohort FORWARD. 
        # Example: A cohort from 2025-01-01 is now tagged as 'comparison_month' 2025-07-01.
        historical_cohorts['comparison_month'] = historical_cohorts['snapshot_month'] + pd.DateOffset(months=num_past_months)
    
        # 3. Individual-Level Tracking (Left Join)
        # We take the cohort that was there 6 months ago and check if they exist in the current snapshot.
        presence_check = pd.merge(
            historical_cohorts,
            df[['snapshot_month', 'companyId', 'professionalId']],
            left_on=['comparison_month', 'companyId', 'professionalId'],
            right_on=['snapshot_month', 'companyId', 'professionalId'],
            how='left',
            indicator=True
        )
    
        # If indicator is 'left_only', the person was there 6 months ago but is GONE now.
        presence_check['is_departed'] = (presence_check['_merge'] == 'left_only').astype(int)
    
        # 4. Aggregate to Company-Level Percentage
        # Group by the current month (comparison_month) to see the fate of the past cohort.
        departure_stats = presence_check.groupby(['comparison_month', 'companyId']).agg(
            departed_count=('is_departed', 'sum'),
            total_past_cohort_size=('is_departed', 'count')
        ).reset_index()
    
        departure_stats[col_name] = (departure_stats['departed_count'] / departure_stats['total_past_cohort_size']) * 100
    
        # 5. Merge the final metric back to the original dataframe
        final_df = pd.merge(
            df,
            departure_stats[['comparison_month', 'companyId', col_name]],
            left_on=['snapshot_month', 'companyId'],
            right_on=['comparison_month', 'companyId'],
            how='left'
        ).drop(columns=['comparison_month'])
    
        # 6. Drop rows where the historical feature is NULL (e.g., the first X months of history)
        final_df = final_df.dropna(subset=[col_name])

        return final_df

    num_past_months=6

    monthly_active_sfc_professional_features_snapshot = add_left_next_momth(monthly_active_sfc_professional_snapshot)
    monthly_active_sfc_professional_features_snapshot = add_departure_in_past_x_months(monthly_active_sfc_professional_snapshot, num_past_months=num_past_months, col_name=f'pct_departed_staff_in_past_{num_past_months}_months')

    monthly_active_sfc_professional_features_snapshot
    return (monthly_active_sfc_professional_features_snapshot,)


@app.cell
def _(monthly_active_sfc_professional_features_snapshot):
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import roc_auc_score, precision_recall_curve

    # 1. Prepare your Features (X) and Target (y)
    # X needs to be a 2D array for sklearn
    X = monthly_active_sfc_professional_features_snapshot[['pct_departed_staff_in_past_6_months']] 
    y = monthly_active_sfc_professional_features_snapshot['left_next_month']

    # 2. Handle Class Imbalance
    # The paper mentions turnover is only ~2.3%. 
    # We should use 'class_weight' so the model doesn't just predict "0" for everyone.
    model = LogisticRegression(class_weight='balanced')

    # 3. Train the model
    model.fit(X, y)

    # 4. Predict Probabilities
    # predict_proba returns [prob_of_0, prob_of_1]. We want index 1.
    monthly_active_sfc_professional_features_snapshot['predicted_chance'] = model.predict_proba(X)[:, 1]

    print(f"Model Coefficient: {model.coef_[0][0]}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Monthly Active Employee Snapshots
    """)
    return


@app.cell
def _():
    return


@app.cell
def _():
    # 
    return


@app.cell(disabled=True)
def _(monthly_active_sfc_professional_snapshot, pd):
    import matplotlib.pyplot as plt

    def generate_contagion_analysis(monthly_active_sfc_professionals):

        # 3. Calculate Peer Groups (Who was there 6 months ago?)
        monthly_active_sfc_professionals['lookback_month'] = monthly_active_sfc_professionals['snapshot_month'] - pd.DateOffset(months=6)

        # Self-merge to find out who was at the same company 6 months ago
        peers_then = monthly_active_sfc_professionals[['snapshot_month', 'companyId', 'professionalId']].copy()

        # 4. Determine Departures
        # We count how many peers a person had 6 months ago vs how many of THOSE specific people are still here
        # This part is handled by comparing the 'monthly_active_sfc_professionals' against its own past state

        # (Simplified calculation for the 23k rows to ensure speed)
        # We calculate the company-level turnover rate over 6 months as a proxy for peer influence
        company_monthly_stats = monthly_active_sfc_professionals.groupby(['snapshot_month', 'companyId'])['professionalId'].nunique().reset_index()
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
        monthly_active_sfc_professionals['left_next_month'] = (
            (monthly_active_sfc_professionals['endDate'] > monthly_active_sfc_professionals['snapshot_month']) & 
            (monthly_active_sfc_professionals['endDate'] <= (monthly_active_sfc_professionals['snapshot_month'] + pd.DateOffset(months=1)))
        ).astype(int)

        final_data = pd.merge(
            monthly_active_sfc_professionals, 
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
