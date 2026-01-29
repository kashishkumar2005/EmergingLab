"""
VERBOSE DEBUG VERSION - Data Ingestion
This version prints detailed information about every step
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

print("=" * 80)
print("VERBOSE DEBUG MODE - STEP 1 DATA INGESTION")
print("=" * 80)

# Step 0: Initial checks
print("\n[Step 0] Initial Environment Check")
print(f"  Current directory: {os.getcwd()}")
print(f"  Python version: {sys.version}")
print(f"  Files in current directory:")
for f in os.listdir('.')[:10]:
    print(f"    - {f}")

# Step 1: Check if data.csv exists
print("\n[Step 1] Checking for data.csv...")
if not os.path.exists('data.csv'):
    print("  ✗ ERROR: data.csv NOT FOUND!")
    print("  Please make sure data.csv is in the same folder as this script.")
    print(f"  Current folder: {os.getcwd()}")
    sys.exit(1)
else:
    file_size = os.path.getsize('data.csv') / (1024**2)
    print(f"  ✓ data.csv found ({file_size:.1f} MB)")

# Step 2: Load the data
print("\n[Step 2] Loading data.csv...")
try:
    # Try UTF-8 first
    try:
        print("  Attempting UTF-8 encoding...")
        df = pd.read_csv('data.csv', low_memory=False)
        print("  ✓ Loaded with UTF-8 encoding")
    except UnicodeDecodeError:
        print("  ⚠ UTF-8 failed, trying latin1...")
        df = pd.read_csv('data.csv', encoding='latin1', low_memory=False)
        print("  ✓ Loaded with latin1 encoding")
    
    print(f"  Loaded {len(df):,} rows and {len(df.columns)} columns")
    print(f"  Columns: {list(df.columns)}")
    
except Exception as e:
    print(f"  ✗ ERROR loading data: {e}")
    sys.exit(1)

# Step 3: Standardize column names
print("\n[Step 3] Standardizing column names...")
column_mapping = {
    'stn_code': 'station_code',
    'sampling_date': 'sampling_date_text',
    'state': 'state',
    'location': 'city',
    'agency': 'monitoring_agency',
    'type': 'area_type',
    'so2': 'SO2',
    'no2': 'NO2',
    'rspm': 'RSPM',
    'spm': 'SPM',
    'location_monitoring_station': 'monitoring_station',
    'pm2_5': 'PM2.5',
    'date': 'date'
}

existing_mappings = {k: v for k, v in column_mapping.items() if k in df.columns}
df.rename(columns=existing_mappings, inplace=True)
print(f"  ✓ Renamed {len(existing_mappings)} columns")
print(f"  New columns: {list(df.columns)}")

# Step 4: Parse dates
print("\n[Step 4] Parsing dates...")
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['month_name'] = df['date'].dt.strftime('%B')
    print(f"  ✓ Date parsed: {df['date'].min()} to {df['date'].max()}")
    print(f"  ✓ Added temporal features: year, month, month_name")

# Step 5: Convert pollutants to numeric
print("\n[Step 5] Converting pollutants to numeric...")
pollutants = ['SO2', 'NO2', 'PM2.5', 'RSPM', 'SPM']
for pol in pollutants:
    if pol in df.columns:
        df[pol] = pd.to_numeric(df[pol], errors='coerce')
        print(f"  ✓ {pol}: {df[pol].notna().sum():,} valid values")

# Step 6: Save processed data
print("\n[Step 6] Saving processed data...")
output_file = 'data_processed.csv'
try:
    print(f"  Writing to: {output_file}")
    df.to_csv(output_file, index=False)
    
    # Verify the file was created
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file) / (1024**2)
        print(f"  ✓ SUCCESS! File created: {output_file}")
        print(f"  ✓ File size: {file_size:.2f} MB")
        print(f"  ✓ File location: {os.path.abspath(output_file)}")
    else:
        print(f"  ✗ ERROR: File was not created!")
        
except Exception as e:
    print(f"  ✗ ERROR saving file: {e}")
    sys.exit(1)

# Step 7: Create ingestion report
print("\n[Step 7] Creating ingestion report...")
report_file = 'ingestion_report.txt'
try:
    with open(report_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("AIR QUALITY DATA INGESTION REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total Records: {len(df):,}\n")
        f.write(f"Total Columns: {len(df.columns)}\n")
        f.write(f"Date Range: {df['date'].min()} to {df['date'].max()}\n")
        f.write(f"\nOutput File: {output_file}\n")
    
    if os.path.exists(report_file):
        print(f"  ✓ Report created: {report_file}")
        print(f"  ✓ Report location: {os.path.abspath(report_file)}")
    else:
        print(f"  ✗ ERROR: Report was not created!")
        
except Exception as e:
    print(f"  ✗ ERROR creating report: {e}")

# Step 8: Summary
print("\n" + "=" * 80)
print("COMPLETION SUMMARY")
print("=" * 80)
print("\nFiles that should now exist in your folder:")
print(f"  1. {output_file}")
print(f"  2. {report_file}")

print("\nTo verify, check your folder:")
print(f"  Location: {os.getcwd()}")

print("\nLook for these files:")
for f in [output_file, report_file]:
    if os.path.exists(f):
        size = os.path.getsize(f) / (1024**2)
        print(f"  ✓ {f} ({size:.2f} MB)")
    else:
        print(f"  ✗ {f} (NOT FOUND)")

print("\n" + "=" * 80)
print("If you see the files above, SUCCESS! ✓")
print("If not, please share the error messages above.")
print("=" * 80 + "\n")