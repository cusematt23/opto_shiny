#LEARNING LAB
#PART3 SHINY FOR PYTHON
#https://www.youtube.com/watch?v=taZYIqC7VMM&ab_channel=BusinessScience

#Goal: Create static data analysis

#IMPORTS
from shiny import (
    App, render, ui, reactive, Session,
    req
)
from shinywidgets import (
    output_widget, render_widget
)
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import jinja2
import pydfs_lineup_optimizer as dfs
import pulp
#DEFAULT APP INPUTS

TITLE="Daily Fantasy Lineup Optimizer"

#DATA INGEST ------

symbol='MSFT'
period="5y"
window_mavg_short=30
window_mavg_long=90


#FUNCTIONS

#https://getbootstrap.com/docs/5.0/components/card/
def my_card(title, value, width=4, bg_color="bg-info", text_color="text-white"):
    """
    Quick function to create a bootstrap 5 card
    """
    card_ui = ui.div(
        ui.div(
            ui.div(
                ui.div(ui.h4(title), class_="card-title"),
                ui.div(value, class_="card-text"),
                class_="card-body flex-fill"
            ),
            class_ = f"card {text_color} {bg_color}",
            style="flex-grow:1;margin:5px;"
        ),
        class_=f"col-md-{width} d-flex"
    )

    return card_ui

def make_plotly_chart(stock_history, window_mavg_short=30, window_mavg_long=90):
    """
    Function to create a plotly chart
    """
    #Hello, just matching his rows line for line
    stock_df=stock_history[['Close']].reset_index()
    stock_df['mavg_short']=stock_df['Close'].rolling(window=window_mavg_short).mean()
    stock_df['mavg_long']=stock_df['Close'].rolling(window=window_mavg_long).mean()
    fig = px.line(
        data_frame=stock_df.set_index('Date'),
        color_discrete_map={
            "Close": "#212529",
            "mavg_short": "#0d6efd",
            "mavg_long": "#0dcaf0"
        },
        title=None
    )
    fig = fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend_title_text=''
    )
    fig = fig.update_yaxes(
        title="Share Price",
        tickprefix="$",
        gridcolor="#2c3e50"
    )
    fig = fig.update_xaxes(
        title="",
        gridcolor="#2c3e50"
    )
    return fig


#LAYOUT

page_dependencies = ui.tags.head(
    ui.tags.link(rel="stylesheet", type="text/css",href="style.css")
)#rel=relationship to external file, type=type of file, href=location of file

#Navbar
app_ui = ui.page_navbar(
    ui.nav(
        "Stock Analysis",
        ui.layout_sidebar(
            sidebar=ui.panel_sidebar(
                ui.h2("Select a Stock"),
                ui.input_selectize(
                    "stock_symbol",
                    "Stock Symbol",
                    ['AAPL','GOOG','MSFT'],
                    selected='MSFT',
                    multiple=False
                    ),
                width=3
            ),
            main=ui.panel_main(
                ui.h2(
                    ui.output_text("txt")
                ),
                ui.div(
                    output_widget("stock_chart_widget", width="auto", height="auto"),
                   class_="card"
                ),
                ui.navset_pill_card(
                    ui.nav(
                        "Company Summary",
                        ui.output_ui("stock_info_ui")
                    ),
                    ui.nav(
                        "Income Statement",
                        ui.output_table("income_statement_table")   
                    )
                ),
            )
        ),
    ),
    title=ui.tags.div(
        ui.img(src="shipit.png", height="30px", style="margin:5px;"),
        ui.h4(" " + TITLE),
        style="display:flex;-webkit-filter: drop-shadow(2px 2px 2px #222);"
    ),
    bg="#0062cc",
    inverse=True,
    header=page_dependencies       
)


def server(input, output, session:Session):

    #REACTIVITY
    @reactive.Calc
    def stock():
        return yf.Ticker(str(input.stock_symbol()))

    @output
    @render.text
    def txt():
        return f"You selected: {str(input.stock_symbol())}"
    
    #Build a company summary
    @output
    @render.ui
    def stock_info_ui():

        stock_info = stock().info

        app_ui = ui.row(

            #Company info
            ui.h5("Company Information"),
            my_card("Industry", stock_info['industry'], bg_color="bg-dark"),
            my_card("Fulltime Employees", "{:0,.0f}".format(stock_info['fullTimeEmployees']), bg_color="bg-dark"),
            my_card("Website", ui.a(stock_info['website'],href=stock_info['website'],target="_blank"),bg_color="bg-dark"),

            ui.hr(),

            #Financial Ratios
            ui.h5("Financial Ratios"),
            my_card("Profit Margin", "{:0,.1%}".format(stock_info['profitMargins']), bg_color="bg-primary"),
            my_card("Revenue Growth", "{:0,.1%}".format(stock_info['revenueGrowth']), bg_color="bg-primary"),
            my_card("Current Ratio", "{:0,.2f}".format(stock_info['currentRatio']), bg_color="bg-primary"),

            ui.hr(),

            #Financial Operations
            ui.h5("Financial Operations"),
            my_card("Total Revenue", "${:0,.0f}".format(stock_info['totalRevenue']), bg_color="bg-info"),
            my_card("EBITDA", "${:0,.0f}".format(stock_info['ebitda']), bg_color="bg-info"),
            my_card("Operating Cash Flow", "${:0,.0f}".format(stock_info['operatingCashflow']), bg_color="bg-info"),

        )
        return app_ui
    
    #Build stock chart
    @output
    @render_widget
    def stock_chart_widget():
        stock_history = stock().history(period=period)
        fig = make_plotly_chart(stock_history, window_mavg_short, window_mavg_long)
        return go.FigureWidget(fig)
    
    #Build income statement table
    @output
    @render.table
    def income_statement_table():
        stock_incomestmt = stock().incomestmt
        return (
            stock_incomestmt \
                .reset_index()
        )
    #end server()


www_dir = Path(__file__).parent / "www"
#END FUNCTIONS    


app = App(app_ui, server, static_assets=www_dir)





