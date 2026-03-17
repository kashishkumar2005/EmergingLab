"""
Step 4: Power BI Data Preparation & Export
==========================================
Prepares all datasets for Power BI import and creates
a Python-generated Plotly HTML report as an alternative.

Run: python step4_powerbi_prep.py
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

print("=" * 60)
print("  STEP 4: Power BI Data Preparation")
print("  AI-Driven Air Quality Insight Confidence Dashboard")
print("=" * 60)

# ── CONFIG ────────────────────────────────────────────────────────────────────

INPUT_FILE  = "data_with_quality_scores.csv"   # From Step 2
OUTPUT_DIR  = "powerbi_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────

print("\n[1/7] Loading quality-scored data...")

# Check if Step 2 output exists
if not os.path.exists(INPUT_FILE):
    print(f"  ⚠ '{INPUT_FILE}' not found. Generating synthetic demo data...")
    # Generate demo data matching your dataset structure
    np.random.seed(42)
    n = 5000  # demo subset

    states = ['Maharashtra', 'Uttar Pradesh', 'West Bengal', 'Delhi',
              'Karnataka', 'Tamil Nadu', 'Rajasthan', 'Gujarat',
              'Madhya Pradesh', 'Andhra Pradesh']
    cities_map = {
        'Maharashtra':  ['Mumbai', 'Pune', 'Nagpur'],
        'Uttar Pradesh':['Lucknow', 'Kanpur', 'Agra'],
        'West Bengal':  ['Kolkata', 'Howrah', 'Durgapur'],
        'Delhi':        ['Delhi', 'New Delhi'],
        'Karnataka':    ['Bangalore', 'Mysore'],
        'Tamil Nadu':   ['Chennai', 'Coimbatore'],
        'Rajasthan':    ['Jaipur', 'Jodhpur'],
        'Gujarat':      ['Ahmedabad', 'Surat'],
        'Madhya Pradesh':['Bhopal', 'Indore'],
        'Andhra Pradesh':['Hyderabad', 'Visakhapatnam'],
    }

    state_col  = np.random.choice(states, n)
    city_col   = [np.random.choice(cities_map[s]) for s in state_col]
    year_col   = np.random.randint(1987, 2016, n)
    month_col  = np.random.randint(1, 13, n)

    so2   = np.abs(np.random.normal(18,  10, n))
    no2   = np.abs(np.random.normal(30,  15, n))
    rspm  = np.abs(np.random.normal(120, 60, n))
    spm   = np.abs(np.random.normal(250, 90, n))
    pm25  = np.where(np.random.rand(n) < 0.02, np.random.normal(85, 30, n), np.nan)

    missing_pct = np.random.beta(1.5, 8, n) * 100
    outlier_cnt = np.random.poisson(0.3, n)
    invalid_cnt = np.random.binomial(1, 0.05, n)

    quality = (100
               - missing_pct * 0.5
               - outlier_cnt * 5
               - invalid_cnt * 20
               + np.random.normal(0, 3, n))
    quality = np.clip(quality, 0, 100)

    confidence = np.where(quality >= 80, 'High',
                 np.where(quality >= 50, 'Medium', 'Low'))

    df = pd.DataFrame({
        'state':               state_col,
        'city':                city_col,
        'year':                year_col,
        'month':               month_col,
        'so2':                 so2,
        'no2':                 no2,
        'rspm':                rspm,
        'spm':                 spm,
        'pm2_5':               pm25,
        'missing_values_percentage': missing_pct,
        'outlier_count':       outlier_cnt,
        'invalid_count':       invalid_cnt,
        'quality_score':       quality,
        'confidence_level':    confidence,
    })
    print(f"  ✓ Demo dataset created: {len(df):,} records")
else:
    df = pd.read_csv(INPUT_FILE, low_memory=False)
    print(f"  ✓ Loaded: {len(df):,} records from {INPUT_FILE}")

# Ensure year column exists
if 'year' not in df.columns and 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

print(f"  Columns: {list(df.columns)}")

# ── TABLE 1: CITY SUMMARY ─────────────────────────────────────────────────────

print("\n[2/7] Building city summary table...")

pollutant_cols = [c for c in ['so2', 'no2', 'rspm', 'spm', 'pm2_5'] if c in df.columns]

agg_dict = {'quality_score': ['mean', 'std', 'count']}
for p in pollutant_cols:
    agg_dict[p] = 'mean'
if 'missing_values_percentage' in df.columns:
    agg_dict['missing_values_percentage'] = 'mean'
if 'outlier_count' in df.columns:
    agg_dict['outlier_count'] = 'sum'

city_agg = df.groupby(['state', 'city']).agg(agg_dict).reset_index()
city_agg.columns = ['_'.join(c).strip('_') for c in city_agg.columns]

# Add confidence label
def score_to_conf(s):
    if s >= 80: return 'High'
    if s >= 50: return 'Medium'
    return 'Low'

city_agg['confidence_level'] = city_agg['quality_score_mean'].apply(score_to_conf)
city_agg = city_agg.sort_values('quality_score_mean', ascending=False).reset_index(drop=True)
city_agg.insert(0, 'rank', range(1, len(city_agg)+1))

out = os.path.join(OUTPUT_DIR, "city_summary.csv")
city_agg.to_csv(out, index=False)
print(f"  ✓ Saved: {out}  ({len(city_agg)} cities)")

# ── TABLE 2: ANNUAL TIME SERIES ───────────────────────────────────────────────

print("\n[3/7] Building annual time series...")

ts_agg = {'quality_score': 'mean'}
for p in pollutant_cols:
    ts_agg[p] = 'mean'
if 'missing_values_percentage' in df.columns:
    ts_agg['missing_values_percentage'] = 'mean'

ts = df.groupby('year').agg(ts_agg).reset_index()
ts.columns = ['year'] + [f'avg_{c}' if c != 'year' else c for c in ts.columns[1:]]

# Confidence counts per year
if 'confidence_level' in df.columns:
    conf_yr = df.groupby(['year', 'confidence_level']).size().unstack(fill_value=0).reset_index()
    ts = ts.merge(conf_yr, on='year', how='left')

ts = ts.sort_values('year')
out = os.path.join(OUTPUT_DIR, "time_series_annual.csv")
ts.to_csv(out, index=False)
print(f"  ✓ Saved: {out}  ({len(ts)} years)")

# ── TABLE 3: CONFIDENCE DISTRIBUTION ─────────────────────────────────────────

print("\n[4/7] Building confidence distribution table...")

if 'confidence_level' in df.columns:
    conf_total = df['confidence_level'].value_counts().reset_index()
    conf_total.columns = ['confidence_level', 'count']
    conf_total['percentage'] = (conf_total['count'] / len(df) * 100).round(2)

    conf_by_state = df.groupby(['state', 'confidence_level']).size().unstack(fill_value=0).reset_index()
    conf_by_state['total'] = conf_by_state.select_dtypes('number').sum(axis=1)
    for lvl in ['High', 'Medium', 'Low']:
        if lvl in conf_by_state.columns:
            conf_by_state[f'{lvl.lower()}_pct'] = (conf_by_state[lvl] / conf_by_state['total'] * 100).round(1)

    out1 = os.path.join(OUTPUT_DIR, "confidence_totals.csv")
    out2 = os.path.join(OUTPUT_DIR, "confidence_by_state.csv")
    conf_total.to_csv(out1, index=False)
    conf_by_state.to_csv(out2, index=False)
    print(f"  ✓ Saved: {out1}")
    print(f"  ✓ Saved: {out2}")

# ── TABLE 4: POLLUTANT OUTLIER STATS ─────────────────────────────────────────

print("\n[5/7] Building pollutant outlier statistics...")

outlier_rows = []
for p in pollutant_cols:
    col = df[p].dropna()
    if len(col) == 0:
        continue
    z = np.abs((col - col.mean()) / col.std())
    outlier_mask = z > 3
    outlier_rows.append({
        'pollutant':       p.upper().replace('_', '.'),
        'total_readings':  len(col),
        'missing_pct':     round((df[p].isna().sum() / len(df)) * 100, 2),
        'outlier_count':   int(outlier_mask.sum()),
        'outlier_pct':     round(outlier_mask.mean() * 100, 2),
        'mean':            round(col.mean(), 2),
        'median':          round(col.median(), 2),
        'std':             round(col.std(), 2),
        'min':             round(col.min(), 2),
        'max':             round(col.max(), 2),
        'p25':             round(col.quantile(0.25), 2),
        'p75':             round(col.quantile(0.75), 2),
        'p99':             round(col.quantile(0.99), 2),
    })

outlier_df = pd.DataFrame(outlier_rows)
out = os.path.join(OUTPUT_DIR, "pollutant_stats.csv")
outlier_df.to_csv(out, index=False)
print(f"  ✓ Saved: {out}")

# ── TABLE 5: QUALITY SCORE HISTOGRAM BINS ────────────────────────────────────

print("\n[6/7] Building quality score distribution bins...")

bins = list(range(0, 101, 10))
labels = [f"{b}-{b+10}" for b in bins[:-1]]
df['score_bin'] = pd.cut(df['quality_score'], bins=bins, labels=labels, include_lowest=True)
hist_df = df['score_bin'].value_counts().sort_index().reset_index()
hist_df.columns = ['score_range', 'count']
hist_df['percentage'] = (hist_df['count'] / len(df) * 100).round(2)
hist_df['cumulative_pct'] = hist_df['percentage'].cumsum().round(2)

out = os.path.join(OUTPUT_DIR, "quality_score_distribution.csv")
hist_df.to_csv(out, index=False)
print(f"  ✓ Saved: {out}")

# ── TABLE 6: 10% SAMPLED DATA (for Power BI performance) ─────────────────────

print("\n[7/7] Creating sampled dataset for Power BI...")

sample_df = df.sample(frac=0.1, random_state=42)
out = os.path.join(OUTPUT_DIR, "sampled_data_10pct.csv")
sample_df.to_csv(out, index=False)
print(f"  ✓ Saved: {out}  ({len(sample_df):,} records — 10% sample)")

# ── POWER BI GUIDE ────────────────────────────────────────────────────────────

guide = f"""
POWER BI IMPORT GUIDE — Air Quality Insight Confidence Dashboard
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
=================================================================

FILES TO IMPORT INTO POWER BI
==============================
1. city_summary.csv           → City-level quality overview table
2. time_series_annual.csv     → Annual trend line charts
3. confidence_totals.csv      → Donut / pie chart for confidence
4. confidence_by_state.csv    → State-level confidence breakdown (map/bar)
5. pollutant_stats.csv        → Pollutant statistics table
6. quality_score_distribution.csv → Histogram / score bins
7. sampled_data_10pct.csv     → Full detail (10% sample for performance)

RECOMMENDED POWER BI VISUALS
==============================
Visual 1  → KPI Cards (5 cards)
  • Total Records:    COUNT(sampled_data[city])
  • High Confidence:  COUNTIF confidence_level = "High"
  • Medium Conf.:     COUNTIF confidence_level = "Medium"
  • Low Confidence:   COUNTIF confidence_level = "Low"
  • Avg Quality:      AVERAGE(sampled_data[quality_score])

Visual 2  → Line Chart: Quality Over Time
  • X-axis: time_series_annual[year]
  • Y-axis: time_series_annual[avg_quality_score]
  • Trend line: ON

Visual 3  → Donut Chart: Confidence Distribution
  • Values: confidence_totals[count]
  • Legend: confidence_totals[confidence_level]
  • Colors: High=Green, Medium=Yellow, Low=Red

Visual 4  → Map / Filled Map: State Quality
  • Location: confidence_by_state[state]
  • Color saturation: high_pct

Visual 5  → Clustered Bar: Top 20 Cities by Score
  • Y-axis: city_summary[city]
  • X-axis: city_summary[quality_score_mean]
  • Color: city_summary[confidence_level]

Visual 6  → Stacked Bar: Outliers by Pollutant
  • X-axis: pollutant_stats[pollutant]
  • Y-axis: pollutant_stats[outlier_pct]

Visual 7  → Histogram (Column Chart): Score Distribution
  • X-axis: quality_score_distribution[score_range]
  • Y-axis: quality_score_distribution[count]

Visual 8  → Table: City Confidence Details
  • Columns: rank, city, state, quality_score_mean, confidence_level

RELATIONSHIPS
=============
sampled_data[city] → city_summary[city]
sampled_data[year] → time_series_annual[year]
sampled_data[confidence_level] → confidence_totals[confidence_level]

COLOR THEME
===========
High Confidence:   #22D3A5  (green)
Medium Confidence: #F59E0B  (amber)
Low Confidence:    #EF4444  (red)
SO2 line:          #00E5FF  (cyan)
NO2 line:          #7C3AED  (purple)
RSPM line:         #FF6B35  (orange)
SPM line:          #F59E0B  (amber)

SLICERS / FILTERS
=================
• Slicer 1: State (from city_summary[state])
• Slicer 2: Confidence Level (High / Medium / Low)
• Slicer 3: Year range (from time_series_annual[year])
• Slicer 4: Pollutant type

MEASURES TO CREATE (DAX)
=========================
High Confidence % = 
  DIVIDE(
    COUNTROWS(FILTER(sampled_data, sampled_data[confidence_level] = "High")),
    COUNTROWS(sampled_data)
  ) * 100

Avg Quality = AVERAGE(sampled_data[quality_score])

Outlier Records = SUMX(sampled_data, sampled_data[outlier_count])

TIPS
====
• Use sampled_data_10pct.csv for detailed visuals (faster in Power BI)
• Use city_summary.csv for aggregate/map visuals (smaller file, complete)
• Sort confidence_level column: High=1, Medium=2, Low=3
• Set quality_score color scale: Red(0) → Yellow(50) → Green(100)
"""

out = os.path.join(OUTPUT_DIR, "POWER_BI_GUIDE.txt")
with open(out, 'w') as f:
    f.write(guide)
print(f"  ✓ Saved: {out}")

# ── SUMMARY ───────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("  ✅ Step 4 Complete!")
print("=" * 60)
print(f"\n  📁 Output folder: {OUTPUT_DIR}/")
print(f"     ├── city_summary.csv")
print(f"     ├── time_series_annual.csv")
print(f"     ├── confidence_totals.csv")
print(f"     ├── confidence_by_state.csv")
print(f"     ├── pollutant_stats.csv")
print(f"     ├── quality_score_distribution.csv")
print(f"     ├── sampled_data_10pct.csv")
print(f"     └── POWER_BI_GUIDE.txt")
print(f"\n  📊 Records processed: {len(df):,}")

if 'confidence_level' in df.columns:
    vc = df['confidence_level'].value_counts()
    print(f"  🟢 High Confidence:   {vc.get('High',0):,}  ({vc.get('High',0)/len(df)*100:.1f}%)")
    print(f"  🟡 Medium Confidence: {vc.get('Medium',0):,}  ({vc.get('Medium',0)/len(df)*100:.1f}%)")
    print(f"  🔴 Low Confidence:    {vc.get('Low',0):,}  ({vc.get('Low',0)/len(df)*100:.1f}%)")

print(f"\n  📖 Open POWER_BI_GUIDE.txt for import instructions")
print(f"  🌐 Open air_quality_dashboard.html for interactive preview")
print("\n  🚀 Next: Import the CSVs into Power BI Desktop")
print("     File → Get Data → Text/CSV → select each file")
print("=" * 60)
