"""Reproducible conversion-funnel analysis for the Multi-Category Store dataset."""
from pathlib import Path
import argparse
import pandas as pd
import matplotlib.pyplot as plt

STAGES = ["view", "cart", "purchase"]

def load_events(path):
    df = pd.read_csv(path)
    required = {"event_time","event_type","product_id","category_id","price","user_id","user_session"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    df["event_time"] = pd.to_datetime(df["event_time"], utc=True, errors="coerce")
    df = df.dropna(subset=["event_time","event_type","user_id","user_session"])
    df = df[df["event_type"].isin(["view","cart","remove_from_cart","purchase"])].copy()
    df["date"] = df["event_time"].dt.date
    df["hour"] = df["event_time"].dt.hour
    return df

def user_funnel(df):
    counts = df[df.event_type.isin(STAGES)].groupby("event_type").user_id.nunique()
    v,c,p = (int(counts.get(s,0)) for s in STAGES)
    return pd.DataFrame({"stage":STAGES,"unique_users":[v,c,p],
        "rate_from_view":[1.0,c/v if v else 0,p/v if v else 0]})

def category_metrics(df):
    key="category_code" if "category_code" in df.columns else "category_id"
    x=df[df.event_type.isin(["view","purchase"])].pivot_table(index=key,columns="event_type",
        values="user_id",aggfunc="nunique",fill_value=0).reset_index()
    for col in ["view","purchase"]:
        if col not in x: x[col]=0
    x["view_to_purchase_rate"]=x["purchase"].div(x["view"].replace(0,pd.NA))
    return x.sort_values(["view_to_purchase_rate","view"],ascending=[False,False])

def session_metrics(df):
    x=pd.crosstab(df["user_session"],df["event_type"])
    for c in STAGES:
        if c not in x: x[c]=0
    x["converted"]=x["purchase"]>0
    x["high_intent_no_purchase"]=(x["cart"]>0)&(x["purchase"]==0)
    return x.reset_index()

def save_outputs(df,out):
    out.mkdir(parents=True,exist_ok=True)
    funnel=user_funnel(df)
    funnel.to_csv(out/"funnel_summary.csv",index=False)
    category_metrics(df).to_csv(out/"category_conversion.csv",index=False)
    session_metrics(df).to_csv(out/"session_metrics.csv",index=False)
    df[df.event_type=="purchase"].groupby("date").user_id.nunique().to_csv(out/"daily_purchasers.csv")
    ax=funnel.plot.bar(x="stage",y="unique_users",legend=False,title="Customer conversion funnel")
    ax.set_ylabel("Unique users"); plt.tight_layout()
    plt.savefig(out/"conversion_funnel.png",dpi=160); plt.close()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True); p.add_argument("--output",default="outputs")
    a=p.parse_args(); df=load_events(a.input); save_outputs(df,Path(a.output))
    print(user_funnel(df).to_string(index=False))

if __name__=="__main__": main()
