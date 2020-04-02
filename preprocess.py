"""

Note, this contains both the older V1 processing code
as well as the V2 code.  The V1 code isn't tested to
work for a full processing cycle, and may need
some adjustments.

"""

# pylint: disable=all
import pandas as pd
import dask.dataframe as dd
import os
from datetime import datetime
from luts import speed_ranges

directory = "./data/station"
cols = ["sid", "direction", "speed", "month"]


def preprocess_stations():
    """
    This producess two (large) files which combine
    all the individual station files into one tidy table.

    stations.csv is ready to be processed into the wind roses.
    Values with direction=0 or speed=0 are dropped to avoid
    north bias.

    mean_stations.csv includes direction=0 and speed=0.

    For both, any rows with N/A values are dropped.
    """
    if preprocess:
        print("*** Preprocessing station data for wind roses & averages... ***")
        print("Looking for station CSV files in ", directory)

        data = pd.DataFrame(columns=cols)
        mean_data = pd.DataFrame(columns=cols)

        for filename in os.listdir(directory):
            d = pd.read_csv(os.path.join(directory, filename))

            # Throw away columns we won't use, and null values
            d = d.drop(columns=["sped", "t_actual"])
            d = d.dropna()

            # Copy for slightly different treatment of
            # station data for averages
            m = d.copy(deep=True)

            # Toss rows where direction is 0, because
            # this represents unclear direction.  Otherwise,
            # the data has a "north bias."  Also drop
            # values where the speed is 0 (calm)
            # for the wind roses.
            d = d[d["drct"] != 0]
            d = d[d["sped_adj"] != 0]

            # Pull month out of t_round column.
            d = d.assign(month=pd.to_numeric(d["t_round"].str.slice(5, 7)))
            m = m.assign(month=pd.to_numeric(m["t_round"].str.slice(5, 7)))
            m = m.assign(year=pd.to_numeric(m["t_round"].str.slice(0, 4)))
            d = d.drop(columns=["t_round"])
            m = m.drop(columns=["t_round"])

            # Rename remaining columns
            d.columns = cols
            m.columns = ["sid", "direction", "speed", "month", "year"]
            data = data.append(d)
            mean_data = mean_data.append(m)

        data.to_csv("stations.csv")
        mean_data.to_csv("mean_stations.csv")


# Needs Dask DF not Pandas.
def averages_by_month(mean_data):
    """
    Compute averages for each month by year.
    """
    print("*** Precomputing monthly averages by year... ***")
    d = mean_data.groupby(["sid", "year", "month"]).mean().compute()

    # Drop indices and get table in good shape for writing
    d = d.reset_index()
    d = d.drop(["direction"], axis=1)
    # Weird code -- drop the prior index, which is unnamed
    d = d.loc[:, ~d.columns.str.contains("^Unnamed")]
    d = d.astype({"year": "int16", "month": "int16"})
    d = d.assign(speed=round(d["speed"], 1))
    d.to_csv("monthly_averages.csv")


# Requires Dask DF, not Pandas
def process_calm(mean_data):
    """
    For each station/year/month, generate a count
    of # of calm measurements.
    """
    print("*** Generating calm counts... ***")

    # Create temporary structure which holds
    # total wind counts and counts where calm to compute
    # % of calm measurements.
    t = mean_data.groupby(["sid", "month"]).size().reset_index().compute()
    calms = t

    # Only keep rows where speed == 0
    d = mean_data[(mean_data["speed"] == 0)]
    d = d.groupby(["sid", "month"]).size().reset_index().compute()

    calms = calms.assign(calm=d[[0]])
    calms.columns = ["sid", "month", "total", "calm"]
    calms = calms.assign(percent=round(calms["calm"] / calms["total"], 3) * 100)
    calms.to_csv("calms.csv")


def chunk_to_rose(sgroup, station_name=None):
    """
    Builds data suitable for Plotly's wind roses from
    a subset of data.

    Given a subset of data, group by direction and speed.
    Return accumulator of whatever the results of the
    incoming chunk are.
    """

    # Bin into 36 categories.
    bins = list(range(5, 356, 10))
    bin_names = list(range(1, 36))

    # Accumulator dataframe.
    proc_cols = ["sid", "direction_class", "speed_range", "count"]
    accumulator = pd.DataFrame(columns=proc_cols)

    # Assign directions to bins.
    # We'll use the exceptional 'NaN' class to represent
    # 355º - 5º, which would otherwise be annoying.
    # Assign 0 to that direction class.
    ds = pd.cut(sgroup["direction"], bins, labels=bin_names)
    sgroup = sgroup.assign(direction_class=ds.cat.add_categories("0").fillna("0"))

    # First compute yearly data.
    # For each direction class...
    directions = sgroup.groupby(["direction_class"])
    for direction, d_group in directions:

        # For each wind speed range bucket...
        for bucket, bucket_info in speed_ranges.items():
            d = d_group.loc[
                (
                    sgroup["speed"].between(
                        bucket_info["range"][0], bucket_info["range"][1], inclusive=True
                    )
                    == True
                )
            ]
            count = len(d.index)
            full_count = len(sgroup.index)
            frequency = 0
            if full_count > 0:
                frequency = round(((count / full_count) * 100), 2)

            accumulator = accumulator.append(
                {
                    "sid": station_name,
                    "direction_class": direction,
                    "speed_range": bucket,
                    "count": count,
                    "frequency": frequency,
                },
                ignore_index=True,
            )

    return accumulator


def process_roses(data):
    """
    For each station we need one trace for each direction.

    Each direction has a data series containing the frequency
    of winds within a certain range.

    Columns:

    sid - stationid
    direction_class - number between 0 and 35.  0 represents
       directions between 360-005º (north), and so forth by 10 degree
       intervals.
    speed_range - text fragment from luts.py for the speed class
    month - 0 for year, 1-12 for month

    """
    print("*** Preprocessing wind rose frequency counts... ***")

    proc_cols = ["sid", "direction_class", "speed_range", "count", "month"]
    rose_data = pd.DataFrame(columns=proc_cols)

    groups = data.groupby(["sid"])
    for station_name, station in groups:
        # Yearly data.
        t = chunk_to_rose(station)
        t = t.assign(month=0)  # year
        rose_data = rose_data.append(t)

        # Monthly data.
        station_grouped_by_month = station.groupby(station["month"])
        # TODO -- can this be rewritten to avoid looping
        # over the groupby?  If so, it'd be much much faster.
        for month, station_by_month in station_grouped_by_month:
            acc = pd.DataFrame(columns=proc_cols)
            t = chunk_to_rose(station_by_month, acc)
            t = t.assign(month=month)
            rose_data = rose_data.append(t)

    rose_data.to_csv("roses.csv")


def process_future_roses():
    """
    Process wind roses for future data.

    We create the data with decadal groups this way for display:
    0 = ERA
    1 = CCSM4/CM3, 2031-2050
    2 = CCSM4/CM3, 2080-2099
    """

    places = pd.read_csv("./places.csv")
    cols = [
        "sid",
        "gcm",
        "decadal_group",
        "direction_class",
        "speed_range",
        "count",
        "frequency",
    ]

    future_roses = pd.DataFrame(columns=cols)

    for index, place in places.iterrows():
        print("[future roses] starting " + place["sid"])

        # Read and prep for ERA/CCSM4.
        df = pd.read_csv("./data/wrf_adj/CCSM4_" + place["sid"] + ".csv")
        df.columns = ["gcm", "sid", "ts", "speed", "direction"]
        df["ts"] = pd.to_datetime(df["ts"])
        df["year"] = pd.DatetimeIndex(df["ts"]).year
        df = df.set_index(["gcm", "year"])
        df = df.reset_index()

        dk = df.loc[(df.gcm == "ERA") & (df.year <= 2009)]
        t = chunk_to_rose(dk, place["sid"])
        t["gcm"] = "ERA"
        t["decadal_group"] = 0
        future_roses = future_roses.append(t)

        # For both CCSM4 and CM3, we need two buckets --
        # 2031 - 2050, and 2080-2099.
        dk = df.loc[(df.gcm == "CCSM4") & (df.year >= 2025) & (df.year <= 2054)]
        t = chunk_to_rose(dk, place["sid"])
        t["gcm"] = "CCSM4"
        t["decadal_group"] = 1
        future_roses = future_roses.append(t)

        dk = df.loc[(df.gcm == "CCSM4") & (df.year >= 2070) & (df.year <= 2099)]
        dk = dk.reset_index()  # for performance.
        t = chunk_to_rose(dk, place["sid"])
        t["gcm"] = "CCSM4"
        t["decadal_group"] = 2
        future_roses = future_roses.append(t)

        # Read & prep CM3
        df = pd.read_csv("./data/wrf_adj/CM3_" + place["sid"] + ".csv")
        df.columns = ["gcm", "sid", "ts", "speed", "direction"]
        df["ts"] = pd.to_datetime(df["ts"])
        df["year"] = pd.DatetimeIndex(df["ts"]).year
        df = df.set_index(["gcm", "year"])
        df = df.reset_index()

        dk = df.loc[(df.gcm == "CM3") & (df.year >= 2031) & (df.year <= 2050)]
        dk = dk.reset_index()  # for performance.
        t = chunk_to_rose(dk, place["sid"])
        t["gcm"] = "CM3"
        t["decadal_group"] = 1
        future_roses = future_roses.append(t)

        dk = df.loc[(df.gcm == "CM3") & (df.year >= 2080) & (df.year <= 2099)]
        dk = dk.reset_index()  # for performance.
        t = chunk_to_rose(dk, place["sid"])
        t["gcm"] = "CM3"
        t["decadal_group"] = 2
        future_roses = future_roses.append(t)

    future_roses.to_csv("future_roses.csv")


def process_threshold_percentiles():
    dt = pd.read_csv("WRF_hwe_perc.csv")
    dt = dt.drop(["wd"], axis=1)
    dt["events"] = 0  # add column for count
    dk = dt.groupby(["stid", "gcm", "ts", "ws_thr", "dur_thr"]).count().reset_index()
    dk.to_csv("percentiles.csv")


# Make already-done V2 work skippable.
v2_preprocess = True
if v2_preprocess:
    # process_threshold_percentiles()
    process_future_roses()

# Make all V1 work skippable.
v1_preprocess = False

if v1_preprocess:
    preprocess_stations()

    data = pd.read_csv("stations.csv", index_col=[0])
    mean_data = dd.read_csv("mean_stations.csv")

    process_calm(mean_data)
    # averages_by_month(mean_data)
    # process_roses(data)
