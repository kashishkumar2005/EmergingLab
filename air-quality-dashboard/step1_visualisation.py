"""
Step 1 Extended: Data Visualization and Initial Insights
Generate visualizations to understand the air quality dataset better
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for compatibility
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
import os
warnings.filterwarnings('ignore')

# Set style for better-looking plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("=" * 80)
print("GENERATING DATA VISUALIZATIONS AND INSIGHTS")
print("=" * 80)

# Check if processed data exists
if not os.path.exists('data_processed.csv'):
    print("\n❌ ERROR: data_processed.csv not found!")
    print("Please run step1_data_ingestion.py first to generate the processed data.\n")
    print("=" * 80)
    exit(1)

# Load the processed data
print("\n[1/5] Loading processed data...")
df = pd.read_csv('data_processed.csv')
df['date'] = pd.to_datetime(df['date'])
print(f"✓ Loaded {len(df):,} records")

# Create figure directory
os.makedirs('visualizations', exist_ok=True)

# 1. Missing Data Heatmap
print("\n[2/5] Creating missing data visualization...")
fig, ax = plt.subplots(figsize=(12, 6))

# Calculate missing percentages
missing_pct = (df.isna().sum() / len(df) * 100).sort_values(ascending=False)
missing_pct = missing_pct[missing_pct > 0]

missing_pct.plot(kind='barh', ax=ax, color='coral')
ax.set_xlabel('Missing Percentage (%)', fontsize=12)
ax.set_ylabel('Column', fontsize=12)
ax.set_title('Missing Data Analysis - Percentage by Column', fontsize=14, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

for i, v in enumerate(missing_pct.values):
    ax.text(v + 1, i, f'{v:.1f}%', va='center', fontsize=10)

plt.tight_layout()
plt.savefig('visualizations/01_missing_data.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: visualizations/01_missing_data.png")

# 2. Temporal Coverage
print("\n[3/5] Creating temporal coverage visualization...")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Records per year
yearly_counts = df.groupby('year').size()
ax1.bar(yearly_counts.index, yearly_counts.values, color='steelblue', alpha=0.7)
ax1.set_xlabel('Year', fontsize=12)
ax1.set_ylabel('Number of Records', fontsize=12)
ax1.set_title('Air Quality Monitoring Records by Year (1987-2015)', fontsize=14, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)
ax1.tick_params(axis='x', rotation=45)

# Add trend line
z = np.polyfit(yearly_counts.index, yearly_counts.values, 2)
p = np.poly1d(z)
ax1.plot(yearly_counts.index, p(yearly_counts.index), "r--", alpha=0.8, linewidth=2, label='Trend')
ax1.legend()

# Records per month (aggregated across all years)
monthly_counts = df.groupby('month').size()
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
ax2.bar(range(1, 13), monthly_counts.values, color='teal', alpha=0.7)
ax2.set_xlabel('Month', fontsize=12)
ax2.set_ylabel('Total Records', fontsize=12)
ax2.set_title('Air Quality Monitoring Records by Month (Aggregated)', fontsize=14, fontweight='bold')
ax2.set_xticks(range(1, 13))
ax2.set_xticklabels(month_names)
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('visualizations/02_temporal_coverage.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: visualizations/02_temporal_coverage.png")

# 3. Geographical Distribution
print("\n[4/5] Creating geographical distribution visualization...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Top 15 states
top_states = df['state'].value_counts().head(15)
ax1.barh(range(len(top_states)), top_states.values, color='mediumseagreen')
ax1.set_yticks(range(len(top_states)))
ax1.set_yticklabels(top_states.index, fontsize=10)
ax1.set_xlabel('Number of Records', fontsize=12)
ax1.set_title('Top 15 States by Monitoring Records', fontsize=14, fontweight='bold')
ax1.grid(axis='x', alpha=0.3)
ax1.invert_yaxis()

for i, v in enumerate(top_states.values):
    ax1.text(v + 500, i, f'{v:,}', va='center', fontsize=9)

# Top 15 cities
top_cities = df['city'].value_counts().head(15)
ax2.barh(range(len(top_cities)), top_cities.values, color='darkslateblue')
ax2.set_yticks(range(len(top_cities)))
ax2.set_yticklabels(top_cities.index, fontsize=10)
ax2.set_xlabel('Number of Records', fontsize=12)
ax2.set_title('Top 15 Cities by Monitoring Records', fontsize=14, fontweight='bold')
ax2.grid(axis='x', alpha=0.3)
ax2.invert_yaxis()

for i, v in enumerate(top_cities.values):
    ax2.text(v + 100, i, f'{v:,}', va='center', fontsize=9)

plt.tight_layout()
plt.savefig('visualizations/03_geographical_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: visualizations/03_geographical_distribution.png")

# 4. Pollutant Distribution
print("\n[5/5] Creating pollutant distribution visualization...")
pollutants = ['SO2', 'NO2', 'PM2.5', 'RSPM', 'SPM']
available_pollutants = [p for p in pollutants if p in df.columns and df[p].notna().sum() > 100]

if len(available_pollutants) > 0:
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()
    
    for idx, pollutant in enumerate(available_pollutants):
        ax = axes[idx]
        data = df[pollutant].dropna()
        
        # Remove extreme outliers for better visualization (keep 99th percentile)
        q99 = data.quantile(0.99)
        data_filtered = data[data <= q99]
        
        ax.hist(data_filtered, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
        ax.set_xlabel(f'{pollutant} Concentration (µg/m³)', fontsize=11)
        ax.set_ylabel('Frequency', fontsize=11)
        ax.set_title(f'{pollutant} Distribution\n(n={len(data):,}, showing up to 99th percentile)', 
                     fontsize=12, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        # Add statistics
        stats_text = f'Mean: {data.mean():.1f}\nMedian: {data.median():.1f}\nStd: {data.std():.1f}'
        ax.text(0.65, 0.95, stats_text, transform=ax.transAxes, fontsize=9,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Remove extra subplots
    for idx in range(len(available_pollutants), 6):
        fig.delaxes(axes[idx])
    
    plt.suptitle('Air Pollutant Concentration Distributions', fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig('visualizations/04_pollutant_distributions.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Saved: visualizations/04_pollutant_distributions.png")

# Generate detailed statistics report
print("\n" + "=" * 80)
print("GENERATING DETAILED STATISTICS REPORT")
print("=" * 80)

with open('data_statistics_report.txt', 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("AIR QUALITY DATA - DETAILED STATISTICS REPORT\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    f.write("--- DATASET OVERVIEW ---\n")
    f.write(f"Total Records: {len(df):,}\n")
    f.write(f"Total Features: {len(df.columns)}\n")
    f.write(f"Date Range: {df['date'].min()} to {df['date'].max()}\n")
    f.write(f"Duration: {df['year'].max() - df['year'].min()} years\n\n")
    
    f.write("--- GEOGRAPHICAL COVERAGE ---\n")
    f.write(f"Total States: {df['state'].nunique()}\n")
    f.write(f"Total Cities: {df['city'].nunique()}\n")
    f.write(f"Total Monitoring Stations: {df['monitoring_station'].nunique()}\n\n")
    
    f.write("Top 10 States by Record Count:\n")
    for i, (state, count) in enumerate(df['state'].value_counts().head(10).items(), 1):
        pct = (count / len(df)) * 100
        f.write(f"  {i:2d}. {state:30s}: {count:7,} records ({pct:5.2f}%)\n")
    
    f.write("\nTop 10 Cities by Record Count:\n")
    for i, (city, count) in enumerate(df['city'].value_counts().head(10).items(), 1):
        pct = (count / len(df)) * 100
        f.write(f"  {i:2d}. {city:30s}: {count:7,} records ({pct:5.2f}%)\n")
    
    f.write("\n--- TEMPORAL ANALYSIS ---\n")
    yearly = df.groupby('year').size()
    f.write(f"Average records per year: {yearly.mean():,.0f}\n")
    f.write(f"Peak year: {yearly.idxmax()} ({yearly.max():,} records)\n")
    f.write(f"Lowest year: {yearly.idxmin()} ({yearly.min():,} records)\n\n")
    
    f.write("--- POLLUTANT STATISTICS ---\n\n")
    for pollutant in available_pollutants:
        data = df[pollutant].dropna()
        f.write(f"{pollutant}:\n")
        f.write(f"  Total Measurements: {len(data):,}\n")
        f.write(f"  Mean: {data.mean():.2f} µg/m³\n")
        f.write(f"  Median: {data.median():.2f} µg/m³\n")
        f.write(f"  Std Dev: {data.std():.2f} µg/m³\n")
        f.write(f"  Min: {data.min():.2f} µg/m³\n")
        f.write(f"  Max: {data.max():.2f} µg/m³\n")
        f.write(f"  25th Percentile: {data.quantile(0.25):.2f} µg/m³\n")
        f.write(f"  75th Percentile: {data.quantile(0.75):.2f} µg/m³\n")
        f.write(f"  95th Percentile: {data.quantile(0.95):.2f} µg/m³\n")
        f.write(f"  99th Percentile: {data.quantile(0.99):.2f} µg/m³\n\n")
    
    f.write("--- DATA QUALITY INDICATORS ---\n")
    f.write(f"Total Missing Values: {df.isna().sum().sum():,}\n")
    f.write(f"Overall Completeness: {((1 - df.isna().sum().sum() / (len(df) * len(df.columns))) * 100):.2f}%\n\n")
    
    f.write("Missing Data by Column:\n")
    missing = df.isna().sum().sort_values(ascending=False)
    for col, count in missing.items():
        if count > 0:
            pct = (count / len(df)) * 100
            f.write(f"  {col:30s}: {count:7,} ({pct:5.2f}%)\n")
    
    f.write("\n--- AREA TYPE DISTRIBUTION ---\n")
    if 'area_type' in df.columns:
        for area, count in df['area_type'].value_counts().items():
            pct = (count / len(df)) * 100
            f.write(f"  {str(area):50s}: {count:6,} ({pct:5.2f}%)\n")

print("✓ Saved: data_statistics_report.txt")

print("\n" + "=" * 80)
print("✓ VISUALIZATION AND ANALYSIS COMPLETED!")
print("=" * 80)
print("\nGenerated Files:")
print("  1. visualizations/01_missing_data.png")
print("  2. visualizations/02_temporal_coverage.png")
print("  3. visualizations/03_geographical_distribution.png")
print("  4. visualizations/04_pollutant_distributions.png")
print("  5. data_statistics_report.txt")
print("=" * 80 + "\n")