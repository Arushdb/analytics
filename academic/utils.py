# analytics/utils.py
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")  # prevents GUI backend issues
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io, base64

def analyze_marks(marks_by_ct, title="Subject Marks"):
    # Pick a qualitative colormap that looks good with categories
    # plot
    bins = 20
    hist_range = (0, 50)
    alpha = 0.55
    cmap = plt.cm.get_cmap("tab10", max(1,len(marks_by_ct)))
    #summary = defaultdict(list)
    summary = {}
        
    #plt.figure(figsize=(9, 5))
    fig, (ax_hist, ax_box) = plt.subplots(
        1, 2, figsize=(11, 5), gridspec_kw={"width_ratios": [3, 1]}
    )

    cleaned = {}
    for i, (ct, data) in enumerate(marks_by_ct.items()):
        arr = np.asarray(data, dtype=float)
        arr = arr[~np.isnan(arr)]
        cleaned[ct] = arr
        if arr.size:
            s = pd.Series(arr)
            q1 = float(s.quantile(0.25))
            q3 = float(s.quantile(0.75))
            summary[ct] = {
                "Count": int(s.count()),
                "Mean": float(s.mean()),
                "Median": float(s.median()),
                "Std_Dev": float(s.std(ddof=0)),   # population stdev (to match np.std default)
                "Min": float(s.min()),
                "Max": float(s.max()),
                "Range": float(s.max() - s.min()),
                "Q1 (25%)": q1,
                "Q3 (75%)": q3,
                "IQR": float(q3 - q1),
                "Skewness": float(s.skew()),
                "Kurtosis": float(s.kurt()),
            }
            ax_hist.hist(data, bins=bins, range=hist_range, alpha=alpha, label=ct, color=cmap(i), edgecolor="none")
            ax_hist.set_title(f"{title} — Histograms")
            ax_hist.set_xlabel("Marks")
            ax_hist.set_ylabel("Frequency")
            leg = ax_hist.legend(title="Class Tests", frameon=False, loc="upper right")
       
    # --- Right: Boxplots ---
    data_for_box = [cleaned[ct] for ct in cleaned]
    labels = list(cleaned.keys())
    bp = ax_box.boxplot(
        data_for_box,
        vert=True,
        patch_artist=True,
        widths=0.6,
        labels=labels,
        medianprops=dict(color="black"),
    )
    for i, patch in enumerate(bp["boxes"]):
        patch.set_facecolor(cmap(i))
        patch.set_alpha(0.5)
        patch.set_edgecolor(cmap(i))


    ax_box.set_title("Boxplots")
    ax_box.set_ylabel("Marks")
    ax_box.set_xlabel("Class Test")
    ax_box.set_ylim(hist_range)
    ax_box.tick_params(axis="x", rotation=20)

    fig.tight_layout()

    # return as PNG
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight",bbox_extra_artists=(leg,))
    plt.close(fig)
    buf.seek(0)
    histogram_base64 = base64.b64encode(buf.read()).decode("utf-8")

    return summary, histogram_base64
    
   