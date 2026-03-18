"""
Step 3B: Dashboard Data Preparation (FIXED VERSION)
Prepare optimized datasets for Power BI / Tableau visualization
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import os
warnings.filterwarnings('ignore')

print("=" * 80)
print("DASHBOARD DATA PREPARATION")
print("=" * 80)

# Load quality-scored data
print("\n[1/5] Loading quality-scored data...")
if not os.path.exists('data_with_quality_scores.csv'):
    print("ERROR: data_with_quality_scores.csv not found!")
    print("Please run Step 2 first.")
    exit(1)

df = pd.read_csv('data_with_quality_scores.csv')
df['date'] = pd.to_datetime(df['date'], errors='coerce')
print(f"✓ Loaded {len(df):,} records")

# Create dashboard-optimized datasets
os.makedirs('dashboard_data', exist_ok=True)

# 1. Summary Statistics by City
print("\n[2/5] Creating city summary dataset...")
city_summary = df.groupby('city').agg({
    'quality_score': ['mean', 'median', 'min', 'max', 'std'],
    'confidence_level': lambda x: (x == 'High').sum() / len(x) * 100,
    'missing_values_percentage': 'mean',
    'outlier_count': 'sum',
    'SO2': ['mean', 'median'],
    'NO2': ['mean', 'median'],
    'PM2.5': ['mean', 'median'],
    'RSPM': ['mean', 'median'],
    'SPM': ['mean', 'median']
}).reset_index()

# Flatten column names
city_summary.columns = ['_'.join(col).strip('_') for col in city_summary.columns.values]
city_summary = city_summary.rename(columns={'city_': 'city'})

# Add record count
city_summary['total_measurements'] = df.groupby('city').size().values

city_summary.to_csv('dashboard_data/city_summary.csv', index=False)
print(f"✓ Saved: dashboard_data/city_summary.csv ({len(city_summary)} cities)")

# 2. Time Series Data (FIXED)
print("\n[3/5] Creating time series dataset...")

# Remove rows with null dates
df_clean = df[df['date'].notna()].copy()

time_series = df_clean.groupby(['year', 'month']).agg({
    'quality_score': 'mean',
    'SO2': 'mean',
    'NO2': 'mean',
    'PM2.5': 'mean',
    'RSPM': 'mean',
    'SPM': 'mean',
    'confidence_level': lambda x: pd.Series([
        (x == 'High').sum(),
        (x == 'Medium').sum(),
        (x == 'Low').sum()
    ]).values
}).reset_index()

# Expand confidence levels
time_series['high_confidence_count'] = time_series['confidence_level'].apply(lambda x: x[0] if isinstance(x, np.ndarray) else 0)
time_series['medium_confidence_count'] = time_series['confidence_level'].apply(lambda x: x[1] if isinstance(x, np.ndarray) else 0)
time_series['low_confidence_count'] = time_series['confidence_level'].apply(lambda x: x[2] if isinstance(x, np.ndarray) else 0)
time_series = time_series.drop('confidence_level', axis=1)

# Add date column (FIXED to handle NaN and float values)
time_series['year'] = time_series['year'].fillna(2000).astype(int)
time_series['month'] = time_series['month'].fillna(1).astype(int).clip(1, 12)

# Create date strings properly
time_series['date'] = pd.to_datetime(
    time_series['year'].astype(str) + '-' + 
    time_series['month'].astype(str).str.zfill(2) + '-01',
    errors='coerce'
)

# Remove any rows where date creation failed
time_series = time_series[time_series['date'].notna()]

time_series.to_csv('dashboard_data/time_series.csv', index=False)
print(f"✓ Saved: dashboard_data/time_series.csv ({len(time_series)} time points)")

# 3. Confidence Distribution
print("\n[4/5] Creating confidence distribution dataset...")
confidence_dist = df.groupby(['city', 'confidence_level']).size().reset_index(name='count')
confidence_pivot = confidence_dist.pivot(index='city', columns='confidence_level', values='count').fillna(0)
confidence_pivot = confidence_pivot.reset_index()

# Calculate percentages
confidence_pivot['total'] = confidence_pivot[['High', 'Medium', 'Low']].sum(axis=1)
confidence_pivot['high_pct'] = (confidence_pivot['High'] / confidence_pivot['total'] * 100).round(2)
confidence_pivot['medium_pct'] = (confidence_pivot['Medium'] / confidence_pivot['total'] * 100).round(2)
confidence_pivot['low_pct'] = (confidence_pivot['Low'] / confidence_pivot['total'] * 100).round(2)

confidence_pivot.to_csv('dashboard_data/confidence_distribution.csv', index=False)
print(f"✓ Saved: dashboard_data/confidence_distribution.csv ({len(confidence_pivot)} cities)")

# 4. Outlier Summary
print("\n[5/5] Creating outlier summary dataset...")
pollutants = ['SO2', 'NO2', 'PM2.5', 'RSPM', 'SPM']
outlier_cols = [f'{p}_outlier' for p in pollutants if f'{p}_outlier' in df.columns]

outlier_summary = []
for col in outlier_cols:
    pollutant = col.replace('_outlier', '')
    total_measurements = df[pollutant].notna().sum()
    outlier_count = df[col].sum()
    outlier_pct = (outlier_count / total_measurements * 100) if total_measurements > 0 else 0
    
    outlier_summary.append({
        'pollutant': pollutant,
        'total_measurements': total_measurements,
        'outlier_count': outlier_count,
        'outlier_percentage': outlier_pct
    })

outlier_df = pd.DataFrame(outlier_summary)
outlier_df.to_csv('dashboard_data/outlier_summary.csv', index=False)
print(f"✓ Saved: dashboard_data/outlier_summary.csv ({len(outlier_df)} pollutants)")

# 5. Create a sampled version for faster dashboard loading
print("\n[6/6] Creating sampled dataset for dashboard...")
# Sample 10% of data while maintaining distribution
sampled_df = df.groupby('confidence_level', group_keys=False).apply(
    lambda x: x.sample(frac=0.1, random_state=42) if len(x) > 0 else x
)
sampled_df.to_csv('dashboard_data/sampled_data.csv', index=False)
print(f"✓ Saved: dashboard_data/sampled_data.csv ({len(sampled_df):,} records)")

# Generate dashboard guide
print("\n" + "=" * 80)
print("CREATING DASHBOARD GUIDE")
print("=" * 80)

with open('dashboard_data/DASHBOARD_GUIDE.txt', 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("DASHBOARD DATA GUIDE\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    f.write("--- AVAILABLE DATASETS ---\n\n")
    
    f.write("1. city_summary.csv\n")
    f.write("   Purpose: City-level aggregated metrics\n")
    f.write("   Use for: City comparison charts, ranking tables\n")
    f.write(f"   Records: {len(city_summary)}\n")
    f.write("   Key columns: city, quality_score_mean, total_measurements,\n")
    f.write("                pollutant averages, confidence percentages\n\n")
    
    f.write("2. time_series.csv\n")
    f.write("   Purpose: Temporal trends and patterns\n")
    f.write("   Use for: Line charts, trend analysis, time-based filtering\n")
    f.write(f"   Records: {len(time_series)}\n")
    f.write("   Key columns: year, month, date, quality_score,\n")
    f.write("                pollutant averages, confidence counts\n\n")
    
    f.write("3. confidence_distribution.csv\n")
    f.write("   Purpose: Confidence level breakdown by city\n")
    f.write("   Use for: Stacked bar charts, confidence heat maps\n")
    f.write(f"   Records: {len(confidence_pivot)}\n")
    f.write("   Key columns: city, High, Medium, Low counts,\n")
    f.write("                high_pct, medium_pct, low_pct\n\n")
    
    f.write("4. outlier_summary.csv\n")
    f.write("   Purpose: Outlier statistics by pollutant\n")
    f.write("   Use for: Quality issue visualization, data reliability charts\n")
    f.write(f"   Records: {len(outlier_df)}\n")
    f.write("   Key columns: pollutant, total_measurements,\n")
    f.write("                outlier_count, outlier_percentage\n\n")
    
    f.write("5. sampled_data.csv\n")
    f.write("   Purpose: 10% sample for faster dashboard loading\n")
    f.write("   Use for: Interactive maps, detailed drill-down views\n")
    f.write(f"   Records: {len(sampled_df):,}\n")
    f.write("   Note: Maintains confidence level distribution\n\n")
    
    f.write("6. data_with_quality_scores.csv (Full dataset)\n")
    f.write("   Purpose: Complete data with all quality metrics\n")
    f.write("   Use for: Detailed analysis, custom calculations\n")
    f.write(f"   Records: {len(df):,}\n")
    f.write("   Warning: Large file, may slow dashboard performance\n\n")
    
    f.write("=" * 80 + "\n")
    f.write("RECOMMENDED DASHBOARD VISUALS\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("1. Overview Page:\n")
    f.write("   - KPI Cards: Total measurements, avg quality score, high confidence %\n")
    f.write("   - Quality Score Distribution (histogram from sampled_data.csv)\n")
    f.write("   - Confidence Level Pie Chart (from confidence_distribution.csv)\n")
    f.write("   - Geographic Map (from city_summary.csv)\n\n")
    
    f.write("2. Time Trends Page:\n")
    f.write("   - Quality Score Over Time (line chart from time_series.csv)\n")
    f.write("   - Confidence Distribution Over Time (stacked area from time_series.csv)\n")
    f.write("   - Pollutant Trends (multiple lines from time_series.csv)\n\n")
    
    f.write("3. City Analysis Page:\n")
    f.write("   - City Ranking Table (from city_summary.csv)\n")
    f.write("   - Top 10 Cities Bar Chart (from city_summary.csv)\n")
    f.write("   - City Confidence Heat Map (from confidence_distribution.csv)\n\n")
    
    f.write("4. Data Quality Page:\n")
    f.write("   - Outlier Analysis Chart (from outlier_summary.csv)\n")
    f.write("   - Missing Data Metrics (from city_summary.csv)\n")
    f.write("   - Quality vs Completeness Scatter (from sampled_data.csv)\n\n")
    
    f.write("=" * 80 + "\n")
    f.write("POWER BI / TABLEAU TIPS\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("Power BI:\n")
    f.write("  1. Import all CSV files from dashboard_data/ folder\n")
    f.write("  2. Create relationships between tables using 'city' field\n")
    f.write("  3. Use sampled_data.csv for map visuals to improve performance\n")
    f.write("  4. Create calculated columns for custom metrics\n")
    f.write("  5. Use slicers for year, city, and confidence level filtering\n\n")
    
    f.write("Tableau:\n")
    f.write("  1. Connect to dashboard_data/ folder as data source\n")
    f.write("  2. Use data blending to combine datasets\n")
    f.write("  3. Create parameters for dynamic filtering\n")
    f.write("  4. Use LOD expressions for advanced calculations\n")
    f.write("  5. Design dashboard with multiple sheets and filters\n\n")
    
    f.write("Color Scheme Recommendations:\n")
    f.write("  - High Confidence: Green (#2ecc71)\n")
    f.write("  - Medium Confidence: Orange (#f39c12)\n")
    f.write("  - Low Confidence: Red (#e74c3c)\n")
    f.write("  - Quality Score: Gradient from Red (0) to Green (100)\n\n")

print("✓ Saved: dashboard_data/DASHBOARD_GUIDE.txt")

print("\n" + "=" * 80)
print("✓ DASHBOARD DATA PREPARATION COMPLETED!")
print("=" * 80)
print("\nGenerated Files in dashboard_data/:")
print("  1. city_summary.csv - City aggregations")
print("  2. time_series.csv - Temporal trends")
print("  3. confidence_distribution.csv - Confidence breakdowns")
print("  4. outlier_summary.csv - Outlier statistics")
print("  5. sampled_data.csv - 10% sample for fast loading")
print("  6. DASHBOARD_GUIDE.txt - Import and visualization guide")
print("\nNext Steps:")
print("  → Import CSV files into Power BI or Tableau")
print("  → Follow DASHBOARD_GUIDE.txt for recommendations")
print("  → Create interactive visualizations")
print("=" * 80 + "\n")