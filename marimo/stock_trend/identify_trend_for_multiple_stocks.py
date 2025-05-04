# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "altair==5.5.0",
#     "duckdb==1.2.2",
#     "marimo",
#     "numpy==2.2.5",
#     "pandas==2.2.3",
#     "sqlglot==26.16.4",
# ]
# ///

import marimo

__generated_with = "0.13.4"
app = marimo.App(width="full")


@app.cell
def _(mo):
    mo.md(
        r"""
    # Stock Trend Analytics - UP/FLAT/DOWN classification

    ## Disclaimer

    The content of this webpage is not an investment advice and does not constitute any offer or solicitation to offer or recommendation of any investment product. 

    ## Problem Statement

    Determining a profitable entry and exit point for stock investment is crucial for success in one's investment journey. **Buy low and sell high** is the goal of every investment with an eye on capital gain.

    One of the ways to achieve that is via Contrarian investing. According to [Wikipedia]([https://en.wikipedia.org/wiki/Contrarian_investing](https://en.wikipedia.org/wiki/Contrarian_investing#:~:text=Contrarian%20investing%20is%20related%20to,be%20undervalued%20by%20the%20market.)), `Contrarian investing is related to value investing in that the contrarian is also looking for mispriced investments and buying those that appear to be undervalued by the market.`  A possible implementation is to look for stocks which (i) have experienced significant decrease in stock price and (ii) have sustained that lower price level for a non-trivial duration. The second point is to safeguard against the real danger that the stock goes delisted and the company behind goes bankrupt. Still, it goes without saying that one should always look for confirmations via other means (e.g. fundamental analysis). 

    To that end, this notebook demonstrates a visualisation which places all the stocks traded in HK (categorised by the HK) together and highlight the UP, FLAT and DOWN period.


    ## Methodology

    ### Data Source - 1d Candle

    I have collected the 1d stock candle online. The candle contains Open, High, Low Close of every trading day. I consolidated the candle data into one average price with

    ***Average Price = (Open + High + Low + Close)/ 4***

    ### Breakout 

    #### At least 30/50/70 pct of price change of the difference of maximum and minimum from 2018-01-01 and 2025-05-02

    We need an objective measurement on what constitutes an UP and DOWN. I opted for the below definition.

    ***If the stock price increases by 50% of the difference between its historical maximum and minimum price, then we consider it a breakout.***

    For the historical period, I picked `2018-01-01` until `2025-05-02`

    ### Algorithm

    The algorithm reads the average price in chronological order. It loops through the successively price and compare it with the subperiod's minimum and maximum. Once the price difference reaches the pre-defined breakout specific to that stock (50% of the max - min over the period), then that period will be recorded as a UP or DOWN. 

    ## Result

    - 3 Different Trend Configs available.
    - Stocks are grouped by the index of which they are constituents.
    """
    )
    return


@app.cell
def _():
    import altair as alt
    import pandas as pd
    import datetime
    import numpy as np
    import os
    import marimo as mo
    from typing import List
    from pathlib import Path
    return List, alt, mo, pd


@app.cell
def _(mo, pd):
    hk_indices_df: pd.DataFrame = pd.read_csv(mo.notebook_location() /"public"/ "hk_index_constituent_stock.csv")
    symbols_df: pd.DataFrame = pd.read_csv(mo.notebook_location() /"public"/"stock_display_name.csv")
    trend_config_df: pd.DataFrame = pd.read_csv(mo.notebook_location()/ "public"/"stock_trend_config.csv")
    all_stock_trend = pd.read_csv(mo.notebook_location()/ "./public/stock_trend_from_2018Jan01_to_2025May02.csv")
    all_stock_trend["from_utc_datetime"] = pd.to_datetime(
        all_stock_trend["from_utc_datetime"]
    )
    all_stock_trend["to_utc_datetime"] = pd.to_datetime(
        all_stock_trend["to_utc_datetime"]
    )
    return all_stock_trend, hk_indices_df, symbols_df, trend_config_df


@app.cell
def _(List, hk_indices_df, mo):
    unique_indices: List[str] = sorted(
        hk_indices_df["standard_index_symbol"].unique()
    )

    index_picker = mo.ui.dropdown(
        label="Pick Index to display",
        value="SEHK:HSI",
        options=unique_indices,
    )
    return (index_picker,)


@app.cell
def _(hk_indices_df, index_picker, mo, symbols_df, trend_config_df):
    stock_name_to_val_mapping = {
        d.get("display_name"): d.get("standard_symbol")
        for d in symbols_df.to_dict(orient="records")
        if d.get("standard_symbol")
        in hk_indices_df[
            hk_indices_df["standard_index_symbol"] == index_picker.value
        ]["standard_stock_symbol"].values
    }

    trend_config_name_to_val_mapping = {
        d.get("display_name"): d.get("config_id")
        for d in trend_config_df.to_dict(orient="records")
    }


    symbols_picker = mo.ui.multiselect(
        label="Pick Stocks to display",
        value=[k for k, v in stock_name_to_val_mapping.items()],
        options=stock_name_to_val_mapping,
    )

    # select 2 configs with largest contrast

    trend_config_left_picker = mo.ui.dropdown(
        label="Right Trend Config",
        value="From 2018-01-01 00:00:00.000 to 2025-05-02 00:00:00.000 with trigger ratio 0.7",
        options=trend_config_name_to_val_mapping,
    )

    trend_config_right_picker = mo.ui.dropdown(
        label="Left Trend Config",
        value="From 2018-01-01 00:00:00.000 to 2025-05-02 00:00:00.000 with trigger ratio 0.3",
        options=trend_config_name_to_val_mapping,
    )

    mo.vstack(
        [
            mo.hstack(
                [
                    index_picker,
                    symbols_picker,
                ],
                justify="center",
            ),
            mo.hstack(
                [trend_config_left_picker, trend_config_right_picker],
                justify="center",
            ),
        ]
    )
    return (
        symbols_picker,
        trend_config_left_picker,
        trend_config_name_to_val_mapping,
        trend_config_right_picker,
    )


@app.cell
def _(
    all_stock_trend,
    mo,
    symbols_picker,
    trend_config_left_picker,
    trend_config_right_picker,
):
    def generate_trend_df(trend_config_id: str):
        return mo.sql(
            f"""
        select *  from  all_stock_trend
        where standard_symbol in ( {",".join([f"'{s}'" for s in symbols_picker.value])} )
        and  config_id = '{trend_config_id}'
        order by standard_symbol, from_utc_datetime
        """,
         output=False
        )


    left_trend_df = generate_trend_df(trend_config_left_picker.value)
    right_trend_df = generate_trend_df(trend_config_right_picker.value)
    return left_trend_df, right_trend_df


@app.cell
def _(
    alt,
    left_trend_df,
    mo,
    pd,
    right_trend_df,
    trend_config_left_picker,
    trend_config_name_to_val_mapping,
    trend_config_right_picker,
):
    reversed_trend_config_name_to_val_mapping = {
        v: k for k, v in trend_config_name_to_val_mapping.items()
    }


    def generate_chart(trend_df: pd.DataFrame, config_display_name: str):
        # Create the chart
        main_chart = (
            alt.Chart(trend_df)
            .mark_rect()
            .encode(
                x=alt.X("from_utc_datetime:T", title="Date"),
                x2="to_utc_datetime:T",
                y=alt.Y("display_name:N", title="Symbol"),
                tooltip=list(trend_df.columns),
                color=alt.Color(
                    "trend:N",
                    scale=alt.Scale(
                        domain=["Up", "Down", "Flat"],
                        range=["green", "red", "gray"],
                    ),
                    legend=alt.Legend(title="Trend"),
                ),
            )
        )

        # Create a DataFrame with Jan 1 dates for each year in your data
        min_year = trend_df["from_utc_datetime"].min().year
        max_year = trend_df["to_utc_datetime"].max().year
        jan1_dates = pd.DataFrame(
            {
                "jan1_date": pd.to_datetime(
                    [f"{year}-01-01" for year in range(min_year, max_year + 1)]
                )
            }
        )

        # Create the rule layer for Jan 1 markers
        jan1_rules = (
            alt.Chart(jan1_dates)
            .mark_rule(
                color="black",
                strokeDash=[5, 5],  # Makes the line dashed
                strokeWidth=1,
            )
            .encode(x="jan1_date:T")
        )

        # Create the year labels layer
        year_labels = (
            alt.Chart(jan1_dates)
            .mark_text(
                align="left",
                baseline="top",
                dx=5,  # Small horizontal offset from the line
                dy=5,  # Small vertical offset (positions above the chart)
                fontSize=10,
            )
            .encode(
                x="jan1_date:T",
                text=alt.Text("year(jan1_date):N"),  # Extract just the year
                y=alt.value(0),  # Position at top of chart
            )
        )

        # Combine the charts
        final_chart = (
            (main_chart + jan1_rules + year_labels)
            .configure_view(stroke="transparent")
            .configure_axis(labelLimit=100)
            .properties(
                title=f"Stock Trend Over Time - {config_display_name} ",
                width=800,
            )
            .interactive()
        )
        return final_chart


    left_final_chart = generate_chart(
        left_trend_df,
        config_display_name=reversed_trend_config_name_to_val_mapping.get(
            trend_config_left_picker.value
        ),
    )
    right_final_chart = generate_chart(
        right_trend_df,
        config_display_name=reversed_trend_config_name_to_val_mapping.get(
            trend_config_right_picker.value
        ),
    )

    mo.hstack([left_final_chart, right_final_chart])
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    # Observations

    ## Contrasting Graph with Trigger Ratio = 0.3 (Smaller Ratio Graph) and Trigger Ratio = 0.7 (Larger Ratio Graph)

    - Smaller Ratio Graph has more UPs and DOWNs than Larger Ratio Graph.
    - A prolonged period of UP/DOWN in Larger Ratio Graph tends to be broken down into smaller pieces of UP/DOWNs in Smaller Ratio Graph.
    - Larger Ratio Graph tends to have more periods of FLAT. Reason is that it takes a more significant price change in large ratio graph in order for a period to be classifed as UP/DOWN.
    """
    )
    return


if __name__ == "__main__":
    app.run()
