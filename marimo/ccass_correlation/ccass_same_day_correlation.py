# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "altair==5.5.0",
#     "duckdb==1.3.0",
#     "marimo",
#     "numpy==2.2.6",
#     "pandas==2.2.3",
#     "plotly==6.1.1",
#     "scipy==1.15.3",
#     "sqlglot==26.19.0",
# ]
# ///

import marimo

__generated_with = "0.13.5"
app = marimo.App(width="medium")


@app.cell
def _():
    import pandas as pd
    import datetime
    import numpy as np
    import os
    import marimo as mo
    import plotly.graph_objects as go
    import altair as alt

    return alt, mo, pd


@app.cell
def _(mo):
    mo.md(
        r"""
    # Is Following 'Smart Money' and Avoiding 'Dumb Money' a Viable Strategy?"

    ##### A case study on correlating stock price with HKEX Ccass Participants' shareholding data

    ## Disclaimer

    The content of this webpage is not an investment advice and does not constitute any offer or solicitation to offer or recommendation of any investment product. 


    ## Problem Statement

    ### Background

    #### Smart Money and Dumb Money as Market Players

    Understanding the market is crucial for successful investing. One approach is to categorize market participants into two broad groups: informed investors (smart money) and less informed investors (dumb money). The first group includes hedge funds, investment banks, and institutional investors, who have the resources, expertise, and time to conduct thorough research before making investment decisions. The second group consists of retail investors, who often lack the same level of access to information and may react impulsively to market news, sometimes buying or selling at inopportune times.

    Based on this conceptual framework of smart money and dumb money, this article attempts to answer these questions:

    - Does smart money always positively correlates with stock price (as in they have the expertise to predict stock performance) ?
    - Does dumb money always negative correlates with stock price (as in they neither have the time nor expertise to understand the stock market) ?


    ### Methodology

    #### Ccass Participants' shareholding amount as proxy of Smart Money and Dumb Money

    Hong Kong-listed stocks offer a unique advantage for tracking investor behavior: all trades are settled through the Hong Kong Securities Clearing Company (HKSCC) via CCASS (Central Clearing and Settlement System), and regulatory rules mandate T+2 settlement reporting. This means detailed ownership data—including changes in institutional and retail holdings—is publicly available on the HKEX CCASS website [HKEX CCASS website](https://www3.hkexnews.hk/sdw/search/searchsdw.aspx).  

    By analyzing this data, investors can distinguish between "smart money" (institutional players accumulating or reducing stakes) and "dumb money" (retail investors reacting to short-term trends). Tracking these movements can provide valuable insights into market sentiment and potential price trends.

    #### Experiment Setup 

    **⚠️ Disclaimer**: This classification in this experiment represents solely the author's subjective opinion and may not be entirely accurate. It should not be construed as financial advice or a definitive guide to market participant behavior. 

    In this experiment, I use global investment banks like Goldman Sachs, JP Morgan, Morgan Stanley, HSBC, and Merrill Lynch to present smart money. They
    are all major international investment banks with sophisticated trading strategies, extensive research capabilities, and institutional-level market influence. These firms typically manage large portfolios, engage in proprietary trading, and serve as market makers, making them strong representatives of informed, institutional "smart money."

    In contrast, I use retail-focused brokerages or smaller financial firms like (Futu Securities, Bright Smart Securities, Valuable Capital Ltd) to represent dumb money. They serve individual investors, who, according to the stereotype, tend to exhibit less-informed, sentiment-driven trading behavior.


    | Type               | Participant Name                          | CCASS Code(s)  |
    |--------------------|-------------------------------------------|----------------|
    | **Smart Money**    |                                           |                |
    |                    | Goldman Sachs                             | B01451         |
    |                    | JP Morgan                                 | B01504, B01110 |
    |                    | Morgan Stanley                            | B01274         |
    |                    | HSBC                                      | C00019         |
    |                    | Merrill Lynch                             | B01224         |
    |                    | Citibank                                  | C00010         |
    | **Dumb Money**     |                                           |                |
    |                    | Futu Securities                           | B01955         |
    |                    | Bright Smart Securities International     | B01668         |
    |                    | Valuable Capital Ltd                      | B01904         |

    #### Data Extraction

    To correlate the two groups of market participants' shareholding with stock price, two data sources are consulted.

    1. Ccass data (https://www3.hkexnews.hk/sdw/search/searchsdw.aspx)
    2. Investingdotcom data (https://www.investing.com/)

    #### Data Transformation

    ##### T+2 settlement

    - Due to T+2 settlement rule, all ccass data are adjusted to derive the stock position date. An Example calendar as follows:

    ```commandline
    ccass_date	stock_position_date
    2025-05-26	2025-05-22
    2025-05-25	2025-05-21
    2025-05-24	2025-05-21
    (...)
    ```

    ccass_date is the date shown on the page, while stock_position_date is derived by going 2 days backwards.


    ##### Spearman's Rank

    After the Ccass data's stock position date is joined with the stock's close price on the same day, we use spearkman's rank to determine the correlation.
    """
    )
    return


@app.cell
def _():
    legend_dict = {
        'SEHK:02137': {
            'SUMMARY': '''
            <br> SEHK:02137 in the period 1st Jan 2024 to May 2025 shows an example of stock which rises 1 YEAR after a global investment bank BUYs. It shows that smart money does not correlate positively with stock price (at least with a delay of 1 year) </br>        
            ''',
            'STOCK_PRICE': '''
            - Notice how the price stays at 1 HKD since early Apr 2024 and eventually spikes on March 2025. It took almost 1 year for it to rise to 3 dollars on Mar 2024.
            ''',
            'SPEARMANS_RANK': '''
            - Citibank (C00010) is the largest shareholder throughout the period. However, it shows negative correlation with stock price (around -0.4) with small p-value. So it is statistically significant''',
            'SCALED_SHAREHOLDING_AMOUNT_VS_PRICE': '''
            - For Citibank (C00010), notice how the shareholding surged in Apr 2024 when the stock was still relatively low in the  period (at 1 HKD). It stayed high until Dec 2024 and it reduced shareholding. It is at that point that the price surged. This shows that Citigroup has been `accumulating shares` and only later on did the price surged.''',

        },


         'SEHK:02216': {
            'SUMMARY': '''
            <br> SEHK:02216 in the period 1st Jan 2025 to May 2025 shows an example of stock which rises 1 YEAR after a global investment bank BUYs. It shows that smart money does not correlate positively with stock price (at least with a delay of 1 year) </br>        
            ''',
            'STOCK_PRICE': '''
            - Notice how SEHK:02216 stays below 1 HKD in the first 3 months of 2025. Then in Apr 2024, it climbed up and reached 2.5 HKD in May 2025.
            ''',
            'SPEARMANS_RANK': '''
            - While Futu (B01955) only has the 2nd largest shareholding amount throughout the period, it shows a positive correlation of 0.7 with small p-value. So it is statistically significant''',
            'SCALED_SHAREHOLDING_AMOUNT_VS_PRICE': '''
            - For Futu (B01955), notice how its shareholding amount follows closely that of the price. It means that retail clients in Futu is doing a good job "prediciting" stock price movement. ''',
        }
    }
    return (legend_dict,)


@app.cell
def _(mo):
    standard_symbol = mo.ui.dropdown(
        value="SEHK:02137",
        label="Standard Symbol for SEHK",
        options = [
            'SEHK:02137',
            'SEHK:02216'
        ]
    )



    max_p_value = mo.ui.dropdown(
        label="P Value (Reject Null Hypothesis)",
        options=[
            "0.001",
            "0.01",
            "0.05",
        ],
        value="0.05",
    )


    mo.vstack(
        [
            mo.md('# Playground'),
            mo.hstack(
                [
                    standard_symbol,max_p_value
                ],
                justify="center",
                align="stretch",
                widths="full",
            ),
        ]
    )
    return max_p_value, standard_symbol


@app.cell
def _(legend_dict, mo, standard_symbol):
    mo.md(
        '# Summary' + 
        legend_dict.get(standard_symbol.value).get('SUMMARY')
    )
    return


@app.cell
def get_data_df(mo, pd):
    base_url = "https://raw.githubusercontent.com/kenho811/home_data_centre_public_mirror/refs/heads/main/marimo/ccass_correlation"


    shareholding_amount_df: pd.DataFrame = pd.read_csv(
        mo.notebook_dir().joinpath("public/hkex_ccass_stock_participant_shareholding.csv")
    )

    shareholding_amount_df['as_of_date_tz08'] = pd.to_datetime(shareholding_amount_df['as_of_date_tz08'])
    shareholding_amount_df['ccass_date'] = pd.to_datetime(shareholding_amount_df['ccass_date'])

    stock_price_df = pd.read_csv(
        base_url
        + "/public/stock_price.csv"
    )

    stock_price_df['as_of_date'] = pd.to_datetime(stock_price_df['as_of_date'])


    stock_name_df = pd.read_csv(
        base_url
        + "/public/hkex_ccass_stock.csv"
    )


    hkex_ccass_participant_df = pd.read_csv(
        base_url
        + "/public/hkex_ccass_participant.csv"
    )
    return (
        hkex_ccass_participant_df,
        shareholding_amount_df,
        stock_name_df,
        stock_price_df,
    )


@app.cell
def _(mo, shareholding_amount_df: "pd.DataFrame", stock_price_df):
    combined_data = mo.sql(
        f"""
        with add_scaled_shareholding_amount as (

            select *,
                   (shareholding_amount - min(shareholding_amount) over(partition by standard_symbol, participant_id)) / (max(shareholding_amount) over(partition by standard_symbol, participant_id) - min(shareholding_amount) over(partition by standard_symbol, participant_id)) as scaled_shareholding_amount
            from shareholding_amount_df

        ), add_scaled_stock_price as (

            select *,
                   ("close" - min("close") over(partition by standard_symbol))/ (max("close") over(partition by standard_symbol) - min("close") over(partition by standard_symbol)) as scaled_close

            from stock_price_df

            )

        select p.*,
               q."close",
               q."scaled_close" 
        from add_scaled_shareholding_amount p
        inner join add_scaled_stock_price q
        on p.as_of_date_tz08 = q.as_of_date
        and p.standard_symbol = q.standard_symbol
        order by p.as_of_date_tz08
        """,
        output=False
    )
    return (combined_data,)


@app.cell
def _(alt, legend_dict, mo, standard_symbol, stock_name, stock_price_df):
    filtered_stock_price_df = stock_price_df[stock_price_df['standard_symbol'] == standard_symbol.value]


    stock_price_chart =(
          alt.Chart(filtered_stock_price_df).mark_line(
              ).encode(
              x='as_of_date',
              y='close',
              tooltip=['as_of_date', 'close']
              ).properties(
            title=f"{standard_symbol.value} ({stock_name}) Stock Price"
        )
        .interactive()
    )

    mo.vstack(
        [
            mo.md(f'##  Stock Price '),
            stock_price_chart,

            mo.md(
             legend_dict.get(standard_symbol.value).get('STOCK_PRICE')
            )
        ]
    )
    return


@app.cell
def _(alt, legend_dict, mo, standard_symbol, statistics_data, stock_name):
    filtered_statistics = statistics_data[statistics_data['standard_symbol'] == standard_symbol.value]

    spearmans_chart = (
        alt.Chart(filtered_statistics)
        .mark_circle(size=60)
        .encode(
            y="average_shareholding_amount",
            x="spearmans_correlation",
            tooltip=[col for col in statistics_data.columns],
            color=alt.condition(
                "datum.can_reject_null_hypothesis === true",  # JavaScript-style boolean check
                alt.value("darkblue"),  # Bright green
                alt.value("lightgray"),  # Very light gray
            ),
        )
        .properties(
            title=f"Spearmans Rank for {standard_symbol.value} ({stock_name})"
        )
        .interactive()
    )

    text_conditioned = (
        spearmans_chart.mark_text(
            align="left",
            baseline="middle",
        )
        .transform_calculate(
            # Create a new field that combines participant_id and participant_name
            combined_name='datum.participant_id + " ( " + datum.participant_name + " ) " '
        )
        .encode(text="combined_name:N")
        .interactive()
    )

    mo.vstack(
        [

              mo.md('''
              ## Spearman's Rank 

              - X-axis: Spearman Rank. -1 means a very negative correlation. 0 means no correlation. 1 means a very positive correlation.
              - Y-axis: Average shareholding amount of the ccass participant. The higher the amount, the more shares are held by the ccass participant
              '''),

            (spearmans_chart + text_conditioned),

        mo.md(
             legend_dict.get(standard_symbol.value).get('SPEARMANS_RANK')
            )
        ]
    )

    return


@app.cell
def _(mo, standard_symbol):
    standard_symbol_vs_default_participant_mapping = {
        'SEHK:02137': [
            # Citibank
            'C00010'
        ],
        'SEHK:02216': [
            # Citibank
            'B01955'
        ]
    }

    smart_money_participant_ids = [
        # Global Investment banks
        ## Goldman Sachs
        "B01451",
        ## JP Morgan
        "B01504",
        "B01110",
        ## Morgan Stanley
        "B01274",
        ## HSBC
        "C00019",

        ## UBS
        "B01161",
        ## Merrill Lynch 
        "B01224",
         # Citibank
        "C00010"
    ]
    dumb_money_participant_ids = [
        # Brokers with retail clients
        ## FUTU
        "B01955",
        ## BRIGHT SMART SECURITIES INTERNATIONAL
        "B01668",
        ## VALUABLE CAPITAL LTD
        "B01904",
    ]

    all_selectable_participant_ids = smart_money_participant_ids + dumb_money_participant_ids



    participant_id = mo.ui.dropdown(
        value=standard_symbol_vs_default_participant_mapping.get(standard_symbol.value)[0],
        label="participant_id",
        options=all_selectable_participant_ids,
        # max_selections=10,
    )


    return (participant_id,)


@app.cell
def _(
    hkex_ccass_participant_df,
    participant_id,
    standard_symbol,
    stock_name_df,
):
    stock_name = stock_name_df[stock_name_df['standard_symbol'] == standard_symbol.value]['stock_name'].values[0]
    participant_name = hkex_ccass_participant_df[hkex_ccass_participant_df['participant_id'] == participant_id.value]['participant_name'].values[0]
    return participant_name, stock_name


@app.cell
def _(correlation_chart, legend_dict, mo, participant_id, standard_symbol):
    mo.vstack(
        [
            mo.md(
             '## (Min-Max scaled) Shareholding Amount against stock price'
            ),
            participant_id,
            correlation_chart,

          mo.md(
             legend_dict.get(standard_symbol.value).get('SCALED_SHAREHOLDING_AMOUNT_VS_PRICE')
        )

        ]
    )
    return


@app.cell
def _(
    alt,
    combined_data,
    participant_id,
    participant_name,
    standard_symbol,
    stock_name,
):
    filtered_combined_data = combined_data[
        (combined_data['standard_symbol'] == standard_symbol.value) &
        (combined_data['participant_id'] == participant_id.value)
    ]

    title = f"""{standard_symbol.value} ({stock_name}): {participant_id.value} ({participant_name}) Correlation with Stock Price"""

    # Base chart for the first line (scaled_close)
    line1 = alt.Chart(filtered_combined_data).mark_line(color='blue').encode(
        x="as_of_date_tz08",
        y=alt.Y("scaled_close", axis=alt.Axis(title='Scaled Close', titleColor='blue')),
        tooltip=[c for c in filtered_combined_data.columns]
    )

    # Base chart for the second line (scaled_shareholding_amount)
    line2 = alt.Chart(filtered_combined_data).mark_line(color='red').encode(
        x="as_of_date_tz08",
        y=alt.Y("scaled_shareholding_amount", axis=alt.Axis(title='Scaled Shareholding Amount', titleColor='red')),
        tooltip=[c for c in filtered_combined_data.columns]
    )

    correlation_chart = alt.layer(
        line1, line2
    ).transform_calculate(
            # Create a new field that combines participant_id and participant_name
            display_participant_id='datum.participant_id + " ( " + datum.participant_name + " ) " '
        ).resolve_scale(
        y='independent'
    ).properties(
        title=title,
    ).interactive()


    return (correlation_chart,)


@app.cell
def _(combined_data, max_p_value, pd):
    from scipy import stats

    dimensions = [
        "standard_symbol",
        "participant_id",
        "stock_name",
        "participant_name",
    ]
    # Group by participant_id and calculate average shareholding amount
    grouped = (
        combined_data.groupby(dimensions)
        .agg(average_shareholding_amount=("shareholding_amount", "mean"))
        .reset_index()
    )


    # Define a function to calculate Spearman correlation
    def calculate_spearman(group):
        correlation, p_value = stats.spearmanr(
            group["shareholding_amount"], group["close"]
        )
        return pd.Series(
            {
                "spearmans_correlation": correlation,
                "spearmans_p_value": p_value,
                "can_reject_null_hypothesis": True
                if p_value <= float(max_p_value.value)
                else False,
            }
        )


    # Calculate Spearman correlation for each participant_id
    spearman_results = (
        combined_data.groupby(dimensions).apply(calculate_spearman).reset_index()
    )


    # Merge the two results
    statistics_data = pd.merge(grouped, spearman_results, on=dimensions)
    _=statistics_data.sort_values(
        by=["average_shareholding_amount"], ascending=False
    )
    return (statistics_data,)


@app.cell
def _(mo):
    mo.md(
        r"""
    # Discussion

    ## Observations

    We see that

    ### when smart money buys, stock price does not necessary rise.

    Like for SEHK: 02137, even when global investment banks buy shares, that does imply an immediate increase in stock price. In this example, it took almost 1 year for the stock price to rise. 

    ### when dumb money buys, stock price does not necessarily fall

    Like for SEHK: 02216, even when retail customers buy shares, that does a drop in price. Instead, price increases just as they buy more shares


    ## Reasons


    ### CCASS participants are only financial intermediaries

    CCASS data does not fully disclose the stock positions of hedge funds and institutional investors. Many large investors use multiple custodians or hold shares through nominee accounts, making their true positions difficult to track. The buying/selling we see in CCASS might only represent a portion of their overall activity.


    ### Time horizon matters

    Smart money often takes longer-term positions. Their buying might not immediately move prices, especially in liquid stocks. 

    ### Definition of smart/dumb money may be imperfect

    Our classification of participants as smart or dumb money might not always be accurate. Some investors may change strategies, or our categorization criteria might miss important nuances in their trading behavior.
    """
    )
    return


if __name__ == "__main__":
    app.run()
