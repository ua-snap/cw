# pylint: disable=all
import pandas as pd
import os
from datetime import datetime
from luts import speed_ranges

directory = "./data/station"
cols = ["sid", "direction", "speed", "month"]
data = pd.DataFrame(columns=cols)


def chunk_to_rose(sgroup, accumulator):
    """
    Given a subset of data, group by direction and speed.
    Return accumulator of whatever the results of the
    incoming chunk are.
    """

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


# Make this skippable during dev
preprocess = False

print("Looking for station CSV files in ", directory)

if preprocess:
    print("*** Preprocessing station data for wind roses & averages... ***")
    for filename in os.listdir(directory):
        d = pd.read_csv(os.path.join(directory, filename))

        # Throw away columns we won't use, and null values
        d = d.drop(columns=["sped", "t_actual"])
        d = d.dropna()

        # Toss rows where direction is 0, because
        # this represents unclear direction.  Otherwise,
        # the data has a "north bias."  Also drop
        # values where the speed is 0 (calm)
        # for the wind roses.
        d = d[d["drct"] != 0]

        # TODO: get & count "calm winds"
        # TODO -- keep a count of these for display
        d = d[d["sped_adj"] != 0]

        # Pull month out of t_round column.
        d = d.assign(month=pd.to_numeric(d["t_round"].str.slice(5, 7)))
        d = d.drop(columns=["t_round"])

        # Rename remaining columns
        d.columns = cols
        data = data.append(d)

    data.to_pickle("stations.pickle")
    data.to_csv("stations.csv")

# If we skipped the ingest, read that output.
if preprocess == False:
    data = pd.read_pickle("stations.pickle")


print("*** Preprocessing monthly averages ***")

mean_cols = ["station", "mean", "month", "sd"]
means = pd.DataFrame(columns=mean_cols)
groups = data.groupby(["sid"])
for station_name, station in groups:
    t = pd.DataFrame(columns=mean_cols)
    station_grouped_by_month = station.groupby(station["month"])
    t = t.assign(
        mean=station_grouped_by_month.mean()["speed"].apply(lambda x: round(x, 1)),
        sd=station_grouped_by_month.std()["speed"].apply(lambda x: round(x, 1)),
        station=station_name,
    )
    t = t.assign(month = t.index)
    means = means.append(t)

means.reset_index()
means.to_pickle("means.pickle")
means.to_csv("means.csv")

exit()

print("*** Preprocessing wind rose frequency counts... ***")


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

proc_cols = ["sid", "direction_class", "speed_range", "count", "month"]
rose_data = pd.DataFrame(columns=proc_cols)

# Bin into 36 categories.
bins = list(range(5, 356, 10))
bin_names = list(range(1, 36))

groups = data.groupby(["sid"])
for station_name, station in groups:
    # Yearly data.
    acc = pd.DataFrame(columns=proc_cols)
    t = chunk_to_rose(station, acc)
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


rose_data.to_pickle("roses.pickle")
rose_data.to_csv("roses.csv")
