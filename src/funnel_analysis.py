"""Conversion funnel analysis for the Retailrocket e-commerce events dataset."""
from pathlib import Path
import argparse
import pandas as pd
import matplotlib.pyplot as plt

STAGES = ["view", "addtocart", "transaction"]


def load_events(path):
    df = pd.read_csv(path)
    required = {"timestamp", "visitorid", "event", "itemid"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    df["event_time"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True, errors="coerce")
    df = df.dropna(subset=["event_time", "visitorid", "event", "itemid"])
    df = df[df["event"].isin(STAGES)].copy()
    df["date"] = df["event_time"].dt.date
    df["hour"] = df["event_time"].dt.hour
    return df


def sequential_funnel(df):
    first = df.pivot_table(index="visitorid", columns="event", values="timestamp", aggfunc="min")
    for stage in STAGES:
        if stage not in first.columns:
            first[stage] = pd.NA

    viewed = first["view"].notna()
    carted = first["addtocart"].notna() & viewed & (first["addtocart"] >= first["view"])
    purchased = (
        first["transaction"].notna()
        & carted
        & (first["transaction"] >= first["addtocart"])
    )

    viewers = int(viewed.sum())
    cart_users = int(carted.sum())
    purchasers = int(purchased.sum())

    return pd.DataFrame({
        "stage": STAGES,
        "unique_visitors": [viewers, cart_users, purchasers],
        "rate_from_view": [
            1.0,
            cart_users / viewers if viewers else 0,
            purchasers / viewers if viewers else 0,
        ],
    })


def item_metrics(df):
    x = df[df["event"].isin(["view", "transaction"])].pivot_table(
        index="itemid", columns="event", values="visitorid", aggfunc="nunique", fill_value=0
    ).reset_index()
    for col in ["view", "transaction"]:
        if col not in x:
            x[col] = 0
    x["view_to_transaction_rate"] = x["transaction"].div(x["view"].replace(0, pd.NA))
    return x.sort_values(["view_to_transaction_rate", "view"], ascending=[False, False])


def high_intent_visitors(df):
    flags = pd.crosstab(df["visitorid"], df["event"])
    for col in STAGES:
        if col not in flags:
            flags[col] = 0
    flags["high_intent_no_transaction"] = (flags["addtocart"] > 0) & (flags["transaction"] == 0)
    return flags.reset_index()


def save_outputs(df, out):
    out.mkdir(parents=True, exist_ok=True)
    funnel = sequential_funnel(df)
    funnel.to_csv(out / "funnel_summary.csv", index=False)
    item_metrics(df).to_csv(out / "item_conversion.csv", index=False)
    high_intent_visitors(df).to_csv(out / "visitor_intent.csv", index=False)
    df[df["event"] == "transaction"].groupby("date")["visitorid"].nunique().to_csv(
        out / "daily_purchasers.csv"
    )

    ax = funnel.plot.bar(
        x="stage", y="unique_visitors", legend=False, title="Retailrocket conversion funnel"
    )
    ax.set_ylabel("Unique visitors")
    plt.tight_layout()
    plt.savefig(out / "conversion_funnel.png", dpi=160)
    plt.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="outputs")
    args = parser.parse_args()

    df = load_events(args.input)
    save_outputs(df, Path(args.output))
    print(sequential_funnel(df).to_string(index=False))


if __name__ == "__main__":
    main()
