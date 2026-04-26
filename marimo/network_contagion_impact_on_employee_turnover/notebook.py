# /// script
# dependencies = [
#     "altair==6.1.0",
#     "duckdb==1.5.2",
#     "ipython==9.13.0",
#     "marimo",
#     "matplotlib==3.10.9",
#     "networkx==3.6.1",
#     "numpy==2.4.4",
#     "pandas==3.0.2",
#     "polars==1.40.1",
#     "pyarrow==24.0.0",
#     "scikit-learn==1.8.0",
#     "sqlglot==30.6.0",
#     "vegafusion>=2.0.3",
#     "vl-convert-python==1.9.0.post1",
# ]
# requires-python = ">=3.12"
# ///

import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium", layout_file="layouts/notebook.slides.json")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Network Contagion Impact on Employee Turnover

    ### Original Paper on Arxiv: [https://arxiv.org/abs/2509.08001](https://arxiv.org/abs/2509.08001)

    ### What drives employee turnover?
    Have you ever wondered why employees leave their current company for another? Apart from personal career aspirations or compensation, "peer attrition" within the same organization has been shown to be a powerful driver of one's own departure. According to the research paper:

    > *"Our analysis shows a contagion effect: professionals are 23% more likely to leave when over 30% of their peers depart within six months."*

    The paper utilizes machine learning techniques to demonstrate the significant increase in explanatory power when this **network contagion effect** is factored into turnover prediction models.

    ### Predicting Employee Turnover via the Hong Kong SFC Public Register (2003–2026)

    This notebook serves as a practical exploration of these concepts. While the original research dives deep into predictive modeling, this notebook focuses on illustrating the underlying correlations using over two decades of public regulatory data (2003 - 2026).
    """)
    return


@app.cell
def _(mo):
    import polars as pl

    _img = mo.image(
        src=mo.notebook_location() / "public" / "network_contagion_of_peers.png",
    )


    mo.vstack(
        [
            mo.md(
                """
    ## Introduction: Employee-employee Network

    The paper uses a graph approach to create an employee-to-employee network. For any given employee, the departure of neighbouring employees is shown to have an impact.

            """
            ),
            _img,
        ]
    )
    return (pl,)


@app.cell
def _(alt, mo):
    # Assuming 'json_data' is your JSON string

    with open(mo.notebook_location() / "public" / "correlation_of_historical_departure_on_employees_next_month_departure.json", "r") as f:
        _chart_jsonspec = f.read()

    _correlation_chart = alt.Chart.from_json(
        _chart_jsonspec
    )
    _correlation_chart = mo.ui.altair_chart(_correlation_chart)



    mo.vstack(
        [
            mo.md(
                """
    To provide a more intuitive understanding of the research finding, this notebook focuses on correlating depature of employees working in the **same company** and the probability of an employee in the same company leaving the next month.

    ## The process

    This notebook guides you through the end-to-end analytical workflow:

    1.  **Data Preprocessing**: Cleaning and structuring the raw SFC licenses registry data into monthly active SFC professionals snapshots from 2003 to 2026.

    2.  **Feature Engineering**: Constructing complex "lookback" metrics to calculate the percentage of peer departures over rolling 3, 6, and 12-month windows.

    3.  **Data Visualization**: Creating faceted analysis and regression plots to visualize the "tipping points" where peer departures begin to accelerate individual turnover.

    ## The result

    At the end of the notebook, you will see how staff departure in the past X months correlates with the probability of a staff departuring in the next month.

    The visualization demonstrates a **positive correlation** between historical peer attrition and the probability of individual turnover in the following month.

    * **Social Contagion Effect**: As the percentage of the "original" cohort (those present 3, 6, or 12 months ago) decreases, the risk profile of remaining employees shifts upward. This suggests that departures are not isolated events but rather create a "contagion" effect that destabilizes the remaining workforce.

    * **The Stability Threshold**: Companies with peer departure rates below **10–15%** show relatively flat and low individual turnover risk. However, once attrition crosses this threshold, the probability of subsequent exits accelerates, indicating a potential "tipping point" in organizational culture.

    * **Window Sensitivity**: The **6-month and 12-month windows** provide the most stable predictive signals. While 3-month windows capture acute shocks, the longer windows reflect a sustained erosion of the internal social fabric, which serves as a more reliable indicator for long-term retention modeling.


            """
            ),
            _correlation_chart,
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Data
    We utilize the public dataset available on Kaggle: [Hong Kong SFC Register (2003–2026)](https://www.kaggle.com/datasets/gautiermarti/hk-sfc-register).

    It originates from the public register maintained by the **Hong Kong Securities and Futures Commission (SFC)**, which has systematically recorded licensed individuals, corporations, and registered institutions since the implementation of the **Securities and Futures Ordinance (SFO)** on 1 April 2003. It provides us with a unique lens into labor market dynamics.

    With this, we will explore **network contagion**—how the movement of peers within a professional network influences individual turnover.


    ---

    ## 📖 Data Dictionary

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
    return


@app.cell
def _():
    import pandas as pd
    import marimo as mo
    import altair as alt
    from copy import deepcopy


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
    return alt, deepcopy, mo, pd, sfc_licenses


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

    # --- 5. CREATE THE LAYERED _chart ---

    # _base X-axis
    _base = alt.Chart(plot_data).encode(
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
            y=alt.value(0),  # Top of _chart
            y2=alt.value(400),  # Bottom of _chart (adjust if height is different)
        )
    )

    # Line _chart
    lines = _base.mark_line(point=True).encode(
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
    _chart = (
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
    ## Bird Eye view of SFC Licensing: YoY SFC License Creation and Termination (2003–2026)

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
            _chart,
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Data Preprocessing

    ## Step 1: Data Consolidation & Employment Mapping

    To analyze **Network Contagion** effectively, we will have to transform the raw data to focus strictly on the **duration of employment** at a given firm rather than the specific regulated activities (license types) held by the individual.

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
def _(mo, pl, sfc_professional_company_employment_history):
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


    if isinstance(_df, pl.DataFrame):
        _df = _df.to_pandas()
    else:
        _df = _df


    # Extract values for the display
    stats = _df.iloc[0]
    stats_table = mo.ui.table(_df)

    # Reference image from research
    img = mo.image(
        src=mo.notebook_location() / "public" / "sfc_data_statistics.jpg",
    )

    # Final Layout
    mo.vstack(
        [
            mo.md(
                f"""
        ## Statistcs Comparison
        """
            ),
            img,
            stats_table,
            mo.md(
                f"""
        **Analysis of Methodology Differences:**
        The differences between these results and the research table are primarily due to the **Corporate Group Consolidation** preprocessing and the extended observation window. By grouping entities by the first word of their name (e.g., merging "Get Nice Securities" and "Get Nice Futures"), internal transfers within the same financial group are no longer counted as new employment records or exits. This leads to a significant reduction in **Employment Records** and a corresponding increase in **Median License Tenure**, as professional stints are viewed as continuous across parent organizations rather than fragmented across subsidiaries. 

        Furthermore, while the original research statistics covered the period from **2003–2024**, this updated analysis incorporates data up to **2026**, accounting for the higher count of **Total Professionals** ({int(stats["total_professionals"]):,}) and capturing more recent market volatility in the turnover metrics.
        """
            ),
        ]
    )
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
def _(mo):
    # Define the range slider

    default_min_year = 2015
    default_max_year = 2020

    year_slider_for_snapshot = mo.ui.range_slider(
        start=2003,
        stop=2026,
        step=1,
        value=[default_min_year, default_max_year],
        label="Year Range For Monthly Snapshot",
    )

    # Display the slider
    year_slider_for_snapshot


    mo.vstack(
        [
            mo.md(
                f"""
    ## Set range for Monthly Snapshot

    - To prevent memory overflow, the default range is set to {default_min_year} to {default_max_year}


            """
            ),
            year_slider_for_snapshot,
        ]
    )
    return (year_slider_for_snapshot,)


@app.cell
def _(
    deepcopy,
    pd,
    pl,
    sfc_professional_company_employment_history,
    year_slider_for_snapshot,
):
    import datetime


    def generate_monthly_active_sfc_professional_snapshot(
        df, from_year=2003, to_year=2026
    ):
        df = deepcopy(df)
        df["effectiveDate"] = pd.to_datetime(df["effectiveDate"])
        # Fill empty end dates with a future date to represent current employees
        df["endDate"] = pd.to_datetime(df["endDate"]).fillna(
            pd.Timestamp("9999-01-01")
        )

        # 2. Create Monthly Snapshots (The "Attendance Sheet")
        # We create a record for every person for every month they were active
        start_date = datetime.date(year=from_year, month=1, day=1)
        end_date = datetime.date(year=to_year, month=1, day=1)
        months = pd.date_range(start_date, end_date, freq="MS")

        snapshot_list = []
        for m in months:
            # Everyone active in month 'm'
            active = deepcopy(df[(df["effectiveDate"] <= m) & (df["endDate"] > m)])
            active["snapshot_month"] = m
            snapshot_list.append(
                active[
                    ["snapshot_month", "companyId", "professionalId", "endDate"]
                ]
            )

        monthly_active_sfc_professional_snapshot = pd.concat(
            snapshot_list, ignore_index=True
        )

        return monthly_active_sfc_professional_snapshot


    if isinstance(sfc_professional_company_employment_history, pl.DataFrame):
        _sfc_professional_company_employment_history = (
            sfc_professional_company_employment_history.to_pandas()
        )
    else:
        _sfc_professional_company_employment_history = (
            sfc_professional_company_employment_history
        )


    monthly_active_sfc_professional_snapshot = (
        generate_monthly_active_sfc_professional_snapshot(
            _sfc_professional_company_employment_history,
            from_year=year_slider_for_snapshot.value[0],
            to_year=year_slider_for_snapshot.value[1],
        )
    )
    return (monthly_active_sfc_professional_snapshot,)


@app.cell(hide_code=True)
def _(alt, mo, monthly_active_sfc_professional_snapshot):
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


    # Create the bar _chart
    _chart = (
        alt.Chart(active_sfc_professional_by_month)
        .mark_bar()
        .encode(
            x=alt.X("snapshot_month:T", title="Snapshot Month"),
            y=alt.Y("active_sfc_professional:Q", title="Active SFC Professionals"),
            tooltip=[
                alt.Tooltip("snapshot_month:T", title="Month"),
                alt.Tooltip("active_sfc_professional:Q", title="Count"),
            ],
        )
        .properties(
            title="Active SFC Professionals by Month", width=800, height=400
        )
        .interactive()
    )

    # To display or save the _chart


    mo.vstack(
        [
            mo.md(
                """
            ## Month-over-month Active SFC professionals (2003–2026)

            The bar _chart of active SFC professionals reflects a resilient but evolving financial labor market between 2004 and 2026. The data aligns with the observation that the industry has seen consistent net expansion for the majority of the last two decades, characterized by the steady climb from approximately 20,000 professionals to a peak of nearly 40,000. This long-term growth supports the premise that new license creations have generally outpaced terminations over this extended period.

            However, the _chart also validates the impact of external stressors on market momentum. The stagnation observed around 2009 and the more recent plateau starting in 2020 directly mirror the periods where license issuance and termination reached parity. Following the 2020 peak, the slight decline in the total count of active professionals through 2026 suggests a more sustained period of industry contraction or consolidation, where the balance has shifted toward terminations. This recent trend emphasizes how global events can transition the market from a state of steady growth into a phase of significant labor market stress and stagnation.
            """
            ),
            _chart,
            mo.md(
                """
            This is how you would see if you set the range from 2003 to 2026
            """,
            ),
            mo.image(
                src=mo.notebook_location()
                / "public"
                / "monthly_active_sfc_professionals_from_2003_to_2026.svg"
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 3: Feature Engineering

    To predict the probability of turnover, we must define a target variable for the model to learn and independent variables that provide predictive signals. This section adds the following features to the dataset:

    ### 1. **`left_next_month`** (Dependent Variable)
    * **Definition**: A binary flag (0 or 1) indicating whether an employee departs the company in the month immediately following the current snapshot.
    * **Description**: This serves as our "ground truth" or target variable. It is derived by checking if a professional's `endDate` falls within the 30-day window following the `snapshot_month`.
    * **Role**: The model will calculate a probability score between 0 and 1 aiming to estimate this outcome.

    ### 2. **`pct_departed_staff`** (Independent Variable / Predictor)
    * **Definition**: The percentage of a specific cohort of staff—defined as those present at the company exactly $X$ months ago—who are no longer present in the current snapshot month.
    * **Description**: This feature acts as a leading indicator of "social contagion" or organizational instability. Unlike a simple headcount change (which can be masked by new hires), this metric uses a row-level lookup on `professionalId` to track the actual survival rate of a specific peer group.
        * **High values**: Suggest a "sinking ship" scenario where established peers are leaving, potentially increasing the psychological or operational pressure on the remaining staff to depart.
        * **Low values**: Suggest a stable environment with high peer retention, which typically correlates with higher employee loyalty.
    * **Multi-Window Analysis**: By iterating through various lookback periods (e.g., 3, 6, and 12 months), we can evaluate which time horizon provides the strongest signal for predicting imminent turnover.
    """)
    return


@app.cell
def _(mo):
    # Create the multiselect UI element
    lookback_selection = mo.ui.multiselect(
        options=[str(i) for i in range(1, 25)],
        label="Select Lookback Windows (Months):",
        value=["3"],  # Default selection
    )


    # Display the selection

    mo.vstack(
        [
            mo.md(
                """
    # Result: Correlation Peer Attribution and Individual Turnover in Following Month


    #### Warning: Due memory limitation, choose at most 3 windows

            """
            ),
            lookback_selection,
        ]
    )
    return (lookback_selection,)


@app.cell
def _(
    deepcopy,
    lookback_selection,
    monthly_active_sfc_professional_snapshot,
    pd,
):
    def add_left_next_momth(monthly_active_sfc_professional_snapshot):
        # add `left_next_month` to indicate if the professional will leave within the coming month
        monthly_active_sfc_professional_snapshot["left_next_month"] = (
            (
                monthly_active_sfc_professional_snapshot["endDate"]
                > monthly_active_sfc_professional_snapshot["snapshot_month"]
            )
            & (
                monthly_active_sfc_professional_snapshot["endDate"]
                <= (
                    monthly_active_sfc_professional_snapshot["snapshot_month"]
                    + pd.DateOffset(months=1)
                )
            )
        ).astype(int)

        return monthly_active_sfc_professional_snapshot


    def create_multi_lookback_features(df, lookback_months_list):
        """
        Creates a long-form dataframe containing peer departure percentages
        for multiple lookback windows.

        """
        df["snapshot_month"] = pd.to_datetime(df["snapshot_month"])
        all_results = []

        # 1. Identify the unique people at each company per month
        historical_cohorts = df[
            ["snapshot_month", "companyId", "professionalId"]
        ].drop_duplicates()

        for x in lookback_months_list:
            # Create a reference for the cohort from 'x' months ago
            cohort_shifted = deepcopy(historical_cohorts)
            cohort_shifted["comparison_month"] = cohort_shifted[
                "snapshot_month"
            ] + pd.DateOffset(months=x)

            # 2. Match the past cohort to the current state (Today)
            presence_check = pd.merge(
                cohort_shifted,
                df[["snapshot_month", "companyId", "professionalId"]],
                left_on=["comparison_month", "companyId", "professionalId"],
                right_on=["snapshot_month", "companyId", "professionalId"],
                how="left",
                indicator=True,
            )

            # If 'left_only', that specific person from the past is gone today
            presence_check["is_departed"] = (
                presence_check["_merge"] == "left_only"
            ).astype(int)

            # 3. Aggregate to Company-Level Percentage
            departure_stats = (
                presence_check.groupby(["comparison_month", "companyId"])
                .agg(
                    departed_count=("is_departed", "sum"),
                    total_past_cohort_size=("is_departed", "count"),
                )
                .reset_index()
            )

            feature_name = "pct_departed_staff"
            departure_stats[feature_name] = (
                departure_stats["departed_count"]
                / departure_stats["total_past_cohort_size"]
            ) * 100

            # 4. Merge back to individual records for this specific 'x'
            temp_df = pd.merge(
                df,
                departure_stats[["comparison_month", "companyId", feature_name]],
                left_on=["snapshot_month", "companyId"],
                right_on=["comparison_month", "companyId"],
                how="left",
            ).drop(columns=["comparison_month"])

            # Add metadata for facetting
            temp_df["lookback_period"] = f"{x} Months"

            # Drop rows where we don't have enough history for this specific window
            temp_df = temp_df.dropna(subset=[feature_name])

            all_results.append(temp_df)

        # Combine all lookbacks into one long-form dataframe
        return pd.concat(all_results, ignore_index=True)


    selected_months = [int(m) for m in lookback_selection.value]

    selected_months.sort()

    monthly_active_sfc_professional_features_snapshot = add_left_next_momth(
        monthly_active_sfc_professional_snapshot
    )
    monthly_active_sfc_professional_features_snapshot = (
        create_multi_lookback_features(
            monthly_active_sfc_professional_snapshot,
            lookback_months_list=selected_months,
        )
    )

    monthly_active_sfc_professional_features_snapshot
    return (monthly_active_sfc_professional_features_snapshot,)


@app.cell(hide_code=True)
def _(mo, monthly_active_sfc_professional_features_snapshot):
    past_staff_departure_vs_next_month_departure_metrics = mo.sql(
        f"""
        SELECT 
            lookback_period,
            snapshot_month,
            -- companyId,
            -- Since pct_departed_staff is already a company-level calculation, 
            -- AVG will return the value itself for that group.
            AVG(pct_departed_staff) AS pct_departed_staff,
            -- This calculates the turnover probability (e.g., 0.05 for 5%)
            AVG(left_next_month) AS avg_left_next_month
        FROM 
            monthly_active_sfc_professional_features_snapshot
        GROUP BY 
            lookback_period,
            snapshot_month
        """
    )


    mo.vstack(
        [
            mo.md(
                """
            ### Data Aggregation for Visualization
            To visualize the relationship between peer departures and turnover probability, the data is aggregated at the company-month level using the following logic:
            """
            ),
            past_staff_departure_vs_next_month_departure_metrics,
        ]
    )
    return (past_staff_departure_vs_next_month_departure_metrics,)


@app.cell
def _(alt, mo, past_staff_departure_vs_next_month_departure_metrics):
    alt.data_transformers.enable("vegafusion")

    # Build the base chart with a fixed X-axis scale
    _base = alt.Chart(past_staff_departure_vs_next_month_departure_metrics).encode(
        x=alt.X(
            "pct_departed_staff:Q",
            title="Peer Departure % (Past X Months)",
            scale=alt.Scale(domain=[0, 30]),
        ),
        y=alt.Y(
            "avg_left_next_month:Q",
            title="Prob. of Leaving Next Month (Mean)",
            scale=alt.Scale(domain=[0, 0.05]),
        ),
    )

    # Layer 1: Scatter points with TOOLTIPS added here
    _points = _base.mark_point(opacity=0.4, size=25, color="steelblue").encode(
        tooltip=[
            alt.Tooltip("lookback_period:N", title="Window"),
            alt.Tooltip("pct_departed_staff:Q", title="Peer Departure %", format=".2f"),
            alt.Tooltip("avg_left_next_month:Q", title="Avg Prob. of Leaving", format=".4f")
        ]
    )

    # Layer 2: Linear Regression line
    _line = _base.transform_regression(
        "pct_departed_staff", "avg_left_next_month"
    ).mark_line(color="red", size=3)


    # Combine layers and facet by the lookback window
    _chart = (
        (_points + _line)
        .facet(
            facet=alt.Facet(
                "lookback_period:N",
                title=None,
                sort=["3 Months", "6 Months", "12 Months"],
            ),
            columns=3,
        )
        .properties(
            title="Impact of Peer Departures on Individual Turnover Probability"
        )
        .configure_axis(grid=True)
        .configure_view(stroke=None)
        .resolve_axis(x='independent') 
    )

    mo.vstack(
        [
            mo.md(
                """
    The visualization demonstrates a statistically significant **positive correlation** between historical peer attrition and the probability of individual turnover in the following month.

    * **Social Contagion Effect**: As the percentage of the "original" cohort (those present 3, 6, or 12 months ago) decreases, the risk profile of remaining employees shifts upward.
    * **The Stability Threshold**: Companies with peer departure rates below **10–15%** show relatively flat and low individual turnover risk.
    * **Window Sensitivity**: The **6-month and 12-month windows** provide the most stable predictive signals.
                """
            ),
            _chart,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
