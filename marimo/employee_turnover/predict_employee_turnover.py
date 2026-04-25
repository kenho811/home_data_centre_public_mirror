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

        # 3. If you strictly need .date() objects (Python datetime.date) instead of pandas timestamps:
        sfc_licenses["effectiveDate"] = sfc_licenses["effectiveDate"].dt.date
        sfc_licenses["endDate"] = sfc_licenses["endDate"].dt.date
        sfc_licenses["license_year_created"] = sfc_licenses[
            "license_year_created"
        ].dt.date
        sfc_licenses["license_year_terminated"] = sfc_licenses[
            "license_year_terminated"
        ].dt.date

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


@app.cell
def _(pd, sfc_licenses):
    import networkx as nx
    import matplotlib.pyplot as plt
    from itertools import combinations

    # 1. Prepare Temporal Data
    # Ensure dates are datetime objects for calculation
    sfc_licenses['effectiveDate'] = pd.to_datetime(sfc_licenses['effectiveDate'])
    # Replace missing end dates with today's date to represent active roles
    sfc_licenses['endDate'] = pd.to_datetime(sfc_licenses['endDate']).fillna(pd.to_datetime('today'))

    # 2. Define Professionals and Career Seniority
    # We define "career length" as the total span between their first and last records
    professionals = sfc_licenses.groupby('sfcid').agg({
        'fullname': 'first',
        'effectiveDate': 'min',
        'endDate': 'max'
    })
    # Calculate career length in days (used for normalization)
    professionals['career_days'] = (professionals['endDate'] - professionals['effectiveDate']).dt.days.replace(0, 1)

    # 3. Identify Co-employment Edges
    # Group by firm (prinCeRef) to find people who worked in the same institution
    firms = sfc_licenses.groupby('prinCeRef')
    edge_weights = {}

    for firm_id, group in firms:
        staff_ids = group['sfcid'].unique()
        if len(staff_ids) < 2:
            continue
    
        # Iterate through all unique pairs of staff at this specific firm
        for u, v in combinations(staff_ids, 2):
            u_periods = group[group['sfcid'] == u][['effectiveDate', 'endDate']]
            v_periods = group[group['sfcid'] == v][['effectiveDate', 'endDate']]
        
            overlap_days = 0
            for _, u_row in u_periods.iterrows():
                for _, v_row in v_periods.iterrows():
                    # Find the intersection of their employment intervals
                    start_max = max(u_row['effectiveDate'], v_row['effectiveDate'])
                    end_min = min(u_row['endDate'], v_row['endDate'])
                
                    if start_max < end_min:
                        overlap_days += (end_min - start_max).days
        
            if overlap_days > 0:
                pair = tuple(sorted((u, v)))
                edge_weights[pair] = edge_weights.get(pair, 0) + overlap_days

    # 4. Construct the Network Graph
    G = nx.Graph()

    for (u, v), overlap in edge_weights.items():
        # Normalize weight by career length to account for seniority differences
        # Weight calculation: Overlap / Average Career Length
        avg_career = (professionals.loc[u, 'career_days'] + professionals.loc[v, 'career_days']) / 2
        norm_weight = overlap / avg_career
    
        G.add_edge(
            professionals.loc[u, 'fullname'], 
            professionals.loc[v, 'fullname'], 
            weight=norm_weight
        )

    # 5. Visualise Results
    plt.figure(figsize=(14, 10))

    # The spring layout positions nodes based on connection strength
    pos = nx.spring_layout(G, k=0.4, iterations=50)

    # Draw the nodes (professionals)
    nx.draw_networkx_nodes(G, pos, node_size=1000, node_color='lightcoral', edgecolors='black')

    # Draw edges (connections) where thickness represents normalized overlap
    weights = [G[u][v]['weight'] * 20 for u, v in G.edges()]
    nx.draw_networkx_edges(G, pos, width=weights, alpha=0.5, edge_color='slategrey')

    # Label nodes with names
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')

    plt.title("Employee-Employee Co-employment Network", fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    plt.show()
    return


if __name__ == "__main__":
    app.run()
