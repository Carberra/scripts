import calendar
import datetime as dt
import sys

import analytix
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

YEAR = dt.date.today().year
DAYS_IN_YEAR = 366 if calendar.isleap(YEAR) else 365
GOAL = int(sys.argv[1])

if __name__ == "__main__":
    analytix.enable_logging()

    with analytix.Client("secrets.json") as client:
        df = (
            client.fetch_report(
                dimensions=("day",),
                metrics=("subscribersGained", "subscribersLost"),
                start_date=dt.date(2005, 1, 1),
                end_date=dt.date(YEAR, 12, 1),
            )
            .to_pandas()
            .set_index("day")
        )

    df["subscribersNet"] = df["subscribersGained"] - df["subscribersLost"]
    df["subscriberTotal"] = df["subscribersNet"].cumsum()

    last_year_end = df[df.index.year == 2023]["subscriberTotal"].iloc[-1]

    dr = pd.date_range(dt.date(YEAR, 1, 1), dt.date(YEAR, 12, 31))
    year_df = pd.DataFrame(
        {
            "day": pd.date_range(dt.date(YEAR, 1, 1), dt.date(YEAR, 12, 31)),
            "actual": df[df.index.year == YEAR]["subscriberTotal"].reindex(dr),
            "target": np.full((366), np.nan),
        },
    ).set_index("day")

    year_df.loc[year_df.index[0], "target"] = year_df.loc[year_df.index[0], "actual"]
    year_df.loc[year_df.index[-1], "target"] = GOAL
    year_df["target"] = year_df["target"].interpolate().astype(int)
    year_df.to_csv(f"sub-targets-{YEAR}-{GOAL}.csv")

    fig = plt.figure(figsize=(12, 6))
    plt.xlabel("Time")
    plt.ylabel("Subscribers")
    sns.lineplot(year_df)
    fig.tight_layout()
    fig.savefig(f"sub-targets-{YEAR}-{GOAL}.png")
