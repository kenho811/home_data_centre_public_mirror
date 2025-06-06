# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "altair==5.5.0",
#     "duckdb==1.2.2",
#     "marimo==0.13.6",
#     "numpy==2.2.5",
#     "pandas==2.2.3",
#     "sqlglot==26.16.4",
# ]
# ///

import marimo

__generated_with = "0.13.6"
app = marimo.App(width="full", app_title="Stock Trend Analytics")


@app.cell
def _():
    import marimo as mo

    mo.vstack([

    mo.video(
        src=mo.notebook_location()/ 'public' / 'segment_candlestick_chart_for_trend_analysis.mp4'
    )

    ])

    return (mo,)


@app.cell
def introduction(mo):
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

    ***If the stock price increases by 30%/50%/70% of the difference between its historical maximum and minimum price, then we consider it a breakout.***

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
    from typing import List
    from pathlib import Path
    return List, alt, pd


@app.cell
def load_all_data(pd):
    base_url = "https://raw.githubusercontent.com/kenho811/home_data_centre_public_mirror/refs/heads/main/marimo/stock_trend"

    hk_indices_stocks_df: pd.DataFrame = pd.read_csv(
        base_url + "/public/hk_index_constituent_stock.csv"
    )

    sample_stock_prices: pd.DataFrame = pd.read_csv(
        base_url
        + "/public/0001_2216_9992_average_price_from_2018Jan01_to_2025May02.csv"
    )

    hk_indices_df: pd.DataFrame = pd.read_csv(
        base_url + "/public/hk_index_name.csv"
    )

    symbols_df: pd.DataFrame = pd.read_csv(
        base_url + "/public/stock_display_name.csv"
    )

    trend_config_df: pd.DataFrame = pd.read_csv(
        base_url + "/public/stock_trend_config.csv"
    )
    all_stock_trend = pd.read_csv(
        base_url + "/public/stock_trend_from_2018Jan01_to_2025May02.csv"
    )

    all_stock_trend["from_utc_datetime"] = pd.to_datetime(
        all_stock_trend["from_utc_datetime"]
    )
    all_stock_trend["to_utc_datetime"] = pd.to_datetime(
        all_stock_trend["to_utc_datetime"]
    )


    trend_config_name_to_val_mapping = {
        k: v
        for (k, v) in sorted(
            [
                (d.get("display_name"), d.get("config_id"))
                for d in trend_config_df.to_dict(orient="records")
            ],
            key=lambda x: x[0],
        )
    }

    reversed_trend_config_name_to_val_mapping = {
        v: k for k, v in trend_config_name_to_val_mapping.items()
    }
    return (
        all_stock_trend,
        hk_indices_df,
        hk_indices_stocks_df,
        reversed_trend_config_name_to_val_mapping,
        sample_stock_prices,
        symbols_df,
        trend_config_df,
        trend_config_name_to_val_mapping,
    )


@app.cell
def demo_one_stock_1(mo, trend_config_name_to_val_mapping):
    one_stock_trend_config_radio = mo.ui.radio(
        label="Trend Config",
        value="From 2018-01-01 00:00:00.000 to 2025-05-02 00:00:00.000 with trigger ratio 0.3",
        options=trend_config_name_to_val_mapping,
    )

    one_stock_symbol_ratio = mo.ui.radio(
        label="Stock Config",
        value="SEHK:00001",
        options=["SEHK:00001", "SEHK:02216", "SEHK:09992"],
    )

    on_off_trend_overlay = mo.ui.radio(
        label="Trend Overlay",
        value="On",
        options=["On", "Off"],
    )
    return (
        on_off_trend_overlay,
        one_stock_symbol_ratio,
        one_stock_trend_config_radio,
    )


@app.cell
def demo_one_stock_2(
    all_stock_trend,
    alt,
    mo,
    on_off_trend_overlay,
    one_stock_symbol_ratio,
    one_stock_trend_config_radio,
    pd,
    sample_stock_prices: "pd.DataFrame",
    trend_config_df: "pd.DataFrame",
):
    ## DEMO Methodology
    # OHLC Chart

    segmented_df = all_stock_trend[
        (all_stock_trend["standard_symbol"] == one_stock_symbol_ratio.value)
        & (all_stock_trend["config_id"] == one_stock_trend_config_radio.value)
    ]
    filterd_sample_stock_prices = sample_stock_prices[
        sample_stock_prices["standard_symbol"] == one_stock_symbol_ratio.value
    ]


    current_trigger_diff_ratio: float = float(
        trend_config_df[
            trend_config_df["config_id"] == one_stock_trend_config_radio.value
        ]["trigger_diff_ratio"].values[0]
    )

    average_price = (
        alt.Chart(filterd_sample_stock_prices)
        .mark_line()
        .encode(
            x="utc_datetime:T",
            y="average_price:Q",
        )
        .properties(width=1000, height=300)
    ).interactive()


    area_marks = (
        alt.Chart(
            pd.DataFrame(
                segmented_df,
                columns=list(segmented_df.columns),
            )
        )
        .mark_rect(opacity=0.5)
        .encode(
            x="from_utc_datetime:T",
            x2="to_utc_datetime:T",
            y=alt.value(0),  # starts at bottom of chart
            y2=alt.value(400),  # height of your chart
            color=alt.Color(
                "trend:N",
                scale=alt.Scale(
                    domain=["Up", "Down", "Flat"], range=["green", "red", "gray"]
                ),
                legend=None,
            ),
            tooltip=list(segmented_df.columns),
        )
    )


    # Create a DataFrame with Jan 1 dates for each year in your data
    min_year = segmented_df["from_utc_datetime"].min().year
    max_year = segmented_df["to_utc_datetime"].max().year
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

    all_charts = average_price + jan1_rules + year_labels
    if on_off_trend_overlay.value == 'On':
        all_charts += area_marks + jan1_rules + year_labels



    # Combine the charts
    _chart = (
        (all_charts)
        .configure_view(stroke="transparent")
        .configure_axis(labelLimit=100)
        .properties(
            title="Stock Trend Changes Over Time",
            width=800,
        )
        .resolve_scale(y="independent")
        .interactive()
    )


    # Create the final chart
    shared_chart = mo.ui.altair_chart(_chart)
    shared_chart


    mo.vstack(
        [
            mo.md(
                """      
            # Demonstration

            ## PART I: How does it work for one stock?

            Pick one of the configurations below:
            """
            ),
            mo.hstack(
                [
                    mo.vstack(
                        [
                            on_off_trend_overlay,
                            one_stock_trend_config_radio,
                            one_stock_symbol_ratio,
                        ]
                    ),
                    shared_chart,
                ]
            ),
            mo.sql(rf"""select standard_symbol, 
                       min(utc_datetime) as min_utc_datetime, 
                       max(utc_datetime) as max_utc_datetime, 
                       min(average_price) as min_average_price, 
                       max(average_price) as max_average_price, 
                       '{current_trigger_diff_ratio}' as trigger_diff_ratio,
                       max(average_price) - min(average_price) as max_min_diff,
                       (max(average_price) - min(average_price)) * {current_trigger_diff_ratio} as max_min_diff_multiplied_by_ratio
                       from filterd_sample_stock_prices
                       group by 1
                       ;
                       """),
        ]
    )
    return (filterd_sample_stock_prices,)


@app.cell
def _(List, hk_indices_stocks_df: "pd.DataFrame", mo):
    unique_indices: List[str] = sorted(
        hk_indices_stocks_df["standard_index_symbol"].unique()
    )

    index_picker = mo.ui.dropdown(
        label="Pick Index to display",
        value="SEHK:HSI",
        options=unique_indices,
    )
    return (index_picker,)


@app.cell
def _(
    hk_indices_stocks_df: "pd.DataFrame",
    index_picker,
    mo,
    symbols_df: "pd.DataFrame",
    trend_config_name_to_val_mapping,
):
    stock_name_to_val_mapping = {
        d.get("display_name"): d.get("standard_symbol")
        for d in symbols_df.to_dict(orient="records")
        if d.get("standard_symbol")
        in hk_indices_stocks_df[
            hk_indices_stocks_df["standard_index_symbol"] == index_picker.value
        ]["standard_stock_symbol"].values
    }


    symbols_picker = mo.ui.multiselect(
        label="Pick Stocks to display",
        value=[k for k, v in stock_name_to_val_mapping.items()],
        options=stock_name_to_val_mapping,
    )

    # select 2 configs with largest contrast

    trend_config_left_picker = mo.ui.dropdown(
        label="Left Trend Config",
        value="From 2018-01-01 00:00:00.000 to 2025-05-02 00:00:00.000 with trigger ratio 0.7",
        options=trend_config_name_to_val_mapping,
    )

    trend_config_right_picker = mo.ui.dropdown(
        label="Right Trend Config",
        value="From 2018-01-01 00:00:00.000 to 2025-05-02 00:00:00.000 with trigger ratio 0.3",
        options=trend_config_name_to_val_mapping,
    )
    return symbols_picker, trend_config_left_picker, trend_config_right_picker


@app.cell
def _(
    List,
    all_stock_trend,
    mo,
    symbols_picker,
    trend_config_left_picker,
    trend_config_right_picker,
):
    def generate_trend_df(trend_config_id: str, symbols: List):
        return mo.sql(
            f"""
        select *  from  all_stock_trend
        where standard_symbol in ( {",".join([f"'{s}'" for s in symbols])} )
        and  config_id = '{trend_config_id}'
        order by standard_symbol, from_utc_datetime
        """,
            output=False,
        )

    if symbols_picker.value:
        part_2_message = 'OK'

        left_trend_df = generate_trend_df(
            trend_config_left_picker.value, symbols=symbols_picker.value
        )
        right_trend_df = generate_trend_df(
            trend_config_right_picker.value, symbols=symbols_picker.value
        )
    else:
        DEFAULT = ['SEHK:00001']
        part_2_message = f'WARNING: NO STOCKS ARE CHOSEN. DEFAULTED TO {DEFAULT=}'
        left_trend_df = generate_trend_df(
            trend_config_left_picker.value, symbols=DEFAULT
        )
        right_trend_df = generate_trend_df(
            trend_config_right_picker.value, symbols=DEFAULT
        )


    return left_trend_df, part_2_message, right_trend_df


@app.cell
def _(
    alt,
    hk_indices_df: "pd.DataFrame",
    index_picker,
    left_trend_df,
    mo,
    part_2_message,
    pd,
    reversed_trend_config_name_to_val_mapping,
    right_trend_df,
    symbols_picker,
    trend_config_left_picker,
    trend_config_right_picker,
):
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
                title={
                    "text": ["Stock Trend Over Time"],
                    "subtitle": [config_display_name],
                },
                width=500,
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


    mo.vstack(
        [
            mo.md(
                """
                    ## PART II: How do HK stocks trend (By Index)?

                    #### Side by side comparison with 2 different configurations

                    """
            ),


            mo.md(    f"""
                /// admonition | Part II Viz Status:

                {part_2_message}
                ///
                """),

            mo.hstack(
                [
                    index_picker,
                    symbols_picker,
                ],
                justify="center",
            ),
            mo.ui.table(hk_indices_df),
            mo.hstack(
                [trend_config_left_picker, trend_config_right_picker],
                justify="center",
            ),
            mo.hstack([left_final_chart, right_final_chart]),
        ]
    )
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
