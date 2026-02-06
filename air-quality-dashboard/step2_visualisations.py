"""
Step 2: Data Quality Visualizations
Generate visualizations for quality metrics and confidence levels
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
import os
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("Set2")

print("=" * 80)
print("GENERATING DATA QUALITY VISUALIZATIONS")
print("=" * 80)

# Check if quality data exists
if not os.path.exists('data_with_quality_scores.csv'):
    print("\n❌ ERROR: data_with_quality_scores.csv not found!")
    print("Please run step2_quality_evaluation.py first.\n")
    print("=" * 80)
    exit(1)

# Load the quality data
print("\n[1/6] Loading quality-scored data...")
df = pd.read_csv('data_with_quality_scores.csv')
df['date'] = pd.to_datetime(df['date'])
print(f"✓ Loaded {len(df):,} records with quality scores")

# Create output directory
os.makedirs('quality_visualizations', exist_ok=True)

# 1. Quality Score Distribution
print("\n[2/6] Creating quality score distribution...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Histogram
ax1.hist(df['quality_score'], bins=50, color='steelblue', edgecolor='black', alpha=0.7)
ax1.axvline(df['quality_score'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {df["quality_score"].mean():.1f}')
ax1.axvline(df['quality_score'].median(), color='green', linestyle='--', linewidth=2, label=f'Median: {df["quality_score"].median():.1f}')
ax1.set_xlabel('Quality Score', fontsize=12)
ax1.set_ylabel('Frequency', fontsize=12)
ax1.set_title('Distribution of Data Quality Scores', fontsize=14, fontweight='bold')
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# Box plot
ax2.boxplot(df['quality_score'], vert=True, patch_artist=True,
            boxprops=dict(facecolor='lightblue', alpha=0.7),
            medianprops=dict(color='red', linewidth=2))
ax2.set_ylabel('Quality Score', fontsize=12)
ax2.set_title('Quality Score Box Plot', fontsize=14, fontweight='bold')
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('quality_visualizations/01_quality_score_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: quality_visualizations/01_quality_score_distribution.png")

# 2. Confidence Level Distribution
print("\n[3/6] Creating confidence level distribution...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Count plot
confidence_counts = df['confidence_level'].value_counts()
colors = {'High': 'green', 'Medium': 'orange', 'Low': 'red'}
conf_colors = [colors[level] for level in confidence_counts.index]

ax1.bar(confidence_counts.index, confidence_counts.values, color=conf_colors, alpha=0.7, edgecolor='black')
ax1.set_ylabel('Number of Records', fontsize=12)
ax1.set_xlabel('Confidence Level', fontsize=12)
ax1.set_title('Confidence Level Distribution', fontsize=14, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)

# Add percentage labels
for i, (level, count) in enumerate(confidence_counts.items()):
    pct = (count / len(df)) * 100
    ax1.text(i, count + len(df)*0.01, f'{count:,}\n({pct:.1f}%)', 
             ha='center', va='bottom', fontsize=10, fontweight='bold')

# Pie chart
ax2.pie(confidence_counts.values, labels=confidence_counts.index, autopct='%1.1f%%',
        colors=conf_colors, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
ax2.set_title('Confidence Level Proportion', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('quality_visualizations/02_confidence_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: quality_visualizations/02_confidence_distribution.png")

# 3. Outlier Analysis
print("\n[4/6] Creating outlier analysis visualization...")
pollutants = ['SO2', 'NO2', 'PM2.5', 'RSPM', 'SPM']
outlier_cols = [f'{p}_outlier' for p in pollutants if f'{p}_outlier' in df.columns]

if outlier_cols:
    fig, ax = plt.subplots(figsize=(12, 6))
    
    outlier_counts = []
    pollutant_names = []
    
    for col in outlier_cols:
        pollutant = col.replace('_outlier', '')
        count = df[col].sum()
        total = df[pollutant].notna().sum()
        pct = (count / total * 100) if total > 0 else 0
        
        outlier_counts.append(pct)
        pollutant_names.append(pollutant)
    
    bars = ax.bar(pollutant_names, outlier_counts, color='coral', alpha=0.7, edgecolor='black')
    ax.set_ylabel('Outlier Percentage (%)', fontsize=12)
    ax.set_xlabel('Pollutant', fontsize=12)
    ax.set_title('Outlier Detection by Pollutant (Z-Score > 3)', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar, pct in zip(bars, outlier_counts):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{pct:.2f}%', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('quality_visualizations/03_outlier_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Saved: quality_visualizations/03_outlier_analysis.png")

# 4. Quality Score vs Missing Data
print("\n[5/6] Creating quality score vs missing data correlation...")
fig, ax = plt.subplots(figsize=(10, 6))

scatter = ax.scatter(df['missing_values_percentage'], df['quality_score'], 
                    c=df['quality_score'], cmap='RdYlGn', alpha=0.5, s=10)
ax.set_xlabel('Missing Values Percentage (%)', fontsize=12)
ax.set_ylabel('Quality Score', fontsize=12)
ax.set_title('Quality Score vs Missing Data Relationship', fontsize=14, fontweight='bold')
ax.grid(alpha=0.3)

# Add colorbar
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Quality Score', fontsize=10)

# Add trend line
z = np.polyfit(df['missing_values_percentage'], df['quality_score'], 1)
p = np.poly1d(z)
x_trend = np.linspace(df['missing_values_percentage'].min(), df['missing_values_percentage'].max(), 100)
ax.plot(x_trend, p(x_trend), "r--", alpha=0.8, linewidth=2, label='Trend Line')
ax.legend()

plt.tight_layout()
plt.savefig('quality_visualizations/04_quality_vs_missing.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: quality_visualizations/04_quality_vs_missing.png")

# 5. Quality Score Over Time
print("\n[6/6] Creating quality score trends over time...")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Quality by year
yearly_quality = df.groupby('year')['quality_score'].agg(['mean', 'median', 'std'])

ax1.plot(yearly_quality.index, yearly_quality['mean'], marker='o', linewidth=2, label='Mean', color='blue')
ax1.plot(yearly_quality.index, yearly_quality['median'], marker='s', linewidth=2, label='Median', color='green')
ax1.fill_between(yearly_quality.index, 
                 yearly_quality['mean'] - yearly_quality['std'],
                 yearly_quality['mean'] + yearly_quality['std'],
                 alpha=0.2, color='blue', label='±1 Std Dev')
ax1.set_xlabel('Year', fontsize=12)
ax1.set_ylabel('Quality Score', fontsize=12)
ax1.set_title('Data Quality Score Trends by Year', fontsize=14, fontweight='bold')
ax1.legend()
ax1.grid(alpha=0.3)

# Confidence distribution by year
confidence_by_year = pd.crosstab(df['year'], df['confidence_level'], normalize='index') * 100

confidence_by_year.plot(kind='area', stacked=True, ax=ax2, 
                        color=['green', 'orange', 'red'], alpha=0.7)
ax2.set_xlabel('Year', fontsize=12)
ax2.set_ylabel('Percentage (%)', fontsize=12)
ax2.set_title('Confidence Level Distribution Over Time', fontsize=14, fontweight='bold')
ax2.legend(title='Confidence Level', loc='upper left')
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('quality_visualizations/05_quality_trends_over_time.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: quality_visualizations/05_quality_trends_over_time.png")

# 6. Quality Score by City (Top 15)
print("\n[6/6] Creating quality score by city...")
top_cities = df['city'].value_counts().head(15).index
city_quality = df[df['city'].isin(top_cities)].groupby('city')['quality_score'].mean().sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(10, 8))
bars = ax.barh(range(len(city_quality)), city_quality.values, color='skyblue', edgecolor='black')

# Color bars by quality level
for i, (city, score) in enumerate(city_quality.items()):
    if score >= 80:
        bars[i].set_color('green')
        bars[i].set_alpha(0.7)
    elif score >= 50:
        bars[i].set_color('orange')
        bars[i].set_alpha(0.7)
    else:
        bars[i].set_color('red')
        bars[i].set_alpha(0.7)

ax.set_yticks(range(len(city_quality)))
ax.set_yticklabels(city_quality.index, fontsize=10)
ax.set_xlabel('Average Quality Score', fontsize=12)
ax.set_title('Average Data Quality Score by City (Top 15)', fontsize=14, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

# Add value labels
for i, score in enumerate(city_quality.values):
    ax.text(score + 1, i, f'{score:.1f}', va='center', fontsize=9)

plt.tight_layout()
plt.savefig('quality_visualizations/06_quality_by_city.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: quality_visualizations/06_quality_by_city.png")

# Generate summary statistics
print("\n" + "=" * 80)
print("GENERATING QUALITY STATISTICS SUMMARY")
print("=" * 80)

with open('quality_statistics_summary.txt', 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("DATA QUALITY STATISTICS SUMMARY\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    f.write("--- QUALITY SCORE STATISTICS ---\n")
    f.write(f"Mean: {df['quality_score'].mean():.2f}\n")
    f.write(f"Median: {df['quality_score'].median():.2f}\n")
    f.write(f"Std Dev: {df['quality_score'].std():.2f}\n")
    f.write(f"Min: {df['quality_score'].min():.2f}\n")
    f.write(f"Max: {df['quality_score'].max():.2f}\n")
    f.write(f"25th Percentile: {df['quality_score'].quantile(0.25):.2f}\n")
    f.write(f"75th Percentile: {df['quality_score'].quantile(0.75):.2f}\n\n")
    
    f.write("--- CONFIDENCE DISTRIBUTION ---\n")
    for level, count in df['confidence_level'].value_counts().items():
        pct = (count / len(df)) * 100
        f.write(f"{level}: {count:,} ({pct:.2f}%)\n")
    
    f.write("\n--- OUTLIER SUMMARY ---\n")
    f.write(f"Total records with outliers: {(df['outlier_count'] > 0).sum():,}\n")
    f.write(f"Average outliers per record: {df['outlier_count'].mean():.2f}\n")
    
    f.write("\n--- MISSING DATA SUMMARY ---\n")
    f.write(f"Average missing percentage per record: {df['missing_values_percentage'].mean():.2f}%\n")
    f.write(f"Records with >50% missing: {(df['missing_values_percentage'] > 50).sum():,}\n")
    
    f.write("\n--- TOP 10 HIGHEST QUALITY CITIES ---\n")
    top_quality_cities = df.groupby('city')['quality_score'].mean().nlargest(10)
    for i, (city, score) in enumerate(top_quality_cities.items(), 1):
        f.write(f"{i:2d}. {city:30s}: {score:.2f}\n")
    
    f.write("\n--- TOP 10 LOWEST QUALITY CITIES ---\n")
    low_quality_cities = df.groupby('city')['quality_score'].mean().nsmallest(10)
    for i, (city, score) in enumerate(low_quality_cities.items(), 1):
        f.write(f"{i:2d}. {city:30s}: {score:.2f}\n")

print("✓ Saved: quality_statistics_summary.txt")

print("\n" + "=" * 80)
print("✓ VISUALIZATION GENERATION COMPLETED!")
print("=" * 80)
print("\nGenerated Files:")
print("  1. quality_visualizations/01_quality_score_distribution.png")
print("  2. quality_visualizations/02_confidence_distribution.png")
print("  3. quality_visualizations/03_outlier_analysis.png")
print("  4. quality_visualizations/04_quality_vs_missing.png")
print("  5. quality_visualizations/05_quality_trends_over_time.png")
print("  6. quality_visualizations/06_quality_by_city.png")
print("  7. quality_statistics_summary.txt")
print("=" * 80 + "\n")