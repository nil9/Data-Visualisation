# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 20:12:43 2020

@author: Uwe
"""

import pandas as pd

pop_url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
total_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
recovered_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"

pop = pd.read_csv(pop_url)
total = pd.read_csv(total_url)
recovered = pd.read_csv(recovered_url)

selected_countries = ["Germany", "Austria", "Netherlands", "Spain", "Czech Republic", "Italy", "United Kingdom", 
                      "Poland", "Belgium", "Denmark", "Turkey", "Greece", "Croatia"]


# remove unnecessary data
pop = pop[["location", "population"]].drop_duplicates()
pop = pop[pop["location"].isin(selected_countries)]
pop.columns = ["Country", "Pop"]
pop.Pop = pop.Pop.astype(int)

# Province is only NA for data about the country itself, so this removes e.g. UK overseas territories
total = total[total["Country/Region"].isin(selected_countries) & total["Province/State"].isna()]
recovered = recovered[recovered["Country/Region"].isin(selected_countries) & recovered["Province/State"].isna()]
total = total.drop(["Province/State", "Lat", "Long"], axis=1)
recovered = recovered.drop(["Province/State", "Lat", "Long"], axis=1)

# convert to tidy tables
total = pd.melt(total, id_vars=["Country/Region"],
                var_name="Date", value_name = "total_cases")
recovered = pd.melt(recovered, id_vars=["Country/Region"], 
                    var_name="Date", value_name = "recovered_cases")

# merge into one table
data = pd.merge(total, recovered, on=["Country/Region", "Date"])
data.columns = ["Country", "Date", "total_cases", "recovered_cases"]
data = pd.merge(data, pop, on=["Country"])

# calculate active and new cases 
data["active_cases"] = data.total_cases - data.recovered_cases
data.Date = pd.to_datetime(data.Date, format="%m/%d/%y").dt.date
data["new_cases"] = ( data[["Country", "Date", "total_cases"]]
                     .groupby("Country")
                     .diff()["total_cases"]
                     .fillna(0)
                     )
data["new_per_mil"] = data.new_cases / (data.Pop / int(1e6))
data["new_rescale"] = ( data[["Country", "Date", "new_cases"]]
                       .groupby("Country")["new_cases"]
                       .apply(lambda x: x/max(x))
                       )

# todo: how to handle Netherlands+UK (no data for recovered cases)
#       set active_cases to always be 0 or NA? currently just setting to 0
data.loc[data["Country"].isin(["Netherlands", "United Kingdom"]), "active_cases"] = 0

# aggregate data by week (re: concept paper)
data_byweek = data.copy()
data_byweek.Date = pd.to_datetime(data_byweek.Date)
data_byweek.Date = data_byweek.Date.apply(lambda x: x.weekofyear)
data_byweek = data_byweek.groupby(["Country", "Date"]).agg({
    "total_cases": "max",
    "recovered_cases": "max",
    "active_cases": "max",
    "new_cases": "sum",
    "Pop":"first"}
    ).reset_index()
data_byweek["new_per_mil"] = data_byweek.new_cases / (data_byweek.Pop / int(1e6))
data_byweek["new_rescale"] = ( data_byweek[["Country", "Date", "new_cases"]]
                       .groupby("Country")["new_cases"]
                       .apply(lambda x: x/max(x))
                       )

data["active_per_mil"] = data.active_cases / (data.Pop / int(1e6))
data_byweek["active_per_mil"] = data_byweek.active_cases / (data_byweek.Pop / int(1e6))
# todo: if using daily data, decide on heatmap-scaling for "correctional days" ie where new_cases<0


# this script should be run again before turning in the assignment to update the dataset
# the links hardcoded before are supposedly kept up to date, so no changes will need to be made to the code               
data.to_csv("processed_data__daily.csv")
data_byweek.to_csv("processed_data__weekly.csv")