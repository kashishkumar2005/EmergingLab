"""
AI-Driven Air Quality Insight Confidence Dashboard
Step 1: Data Ingestion and Preprocessing

This script handles:
1. Loading the air quality dataset
2. Initial exploration and profiling
3. Data type standardization
4. Basic preprocessing and cleaning
5. Saving processed data for next steps
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import os
warnings.filterwarnings('ignore')

class AirQualityDataIngestion:
    """Handle data ingestion and initial preprocessing for air quality analysis"""
    
    def __init__(self, filepath):
        """
        Initialize the data ingestion pipeline
        
        Parameters:
        -----------
        filepath : str
            Path to the CSV file containing air quality data
        """
        self.filepath = filepath
        self.df = None
        self.original_shape = None
        self.ingestion_report = {}
        
    def load_data(self):
        """Load the CSV file into a pandas DataFrame"""
        print("=" * 80)
        print("STEP 1: DATA INGESTION AND PREPROCESSING")
        print("=" * 80)
        print("\n[1/6] Loading data from CSV file...")
        
        try:
            # Try UTF-8 first, fall back to latin1 if needed
            try:
                self.df = pd.read_csv(self.filepath, low_memory=False)
            except UnicodeDecodeError:
                print("  ⚠ UTF-8 encoding failed, trying latin1 encoding...")
                self.df = pd.read_csv(self.filepath, encoding='latin1', low_memory=False)
            
            self.original_shape = self.df.shape
            
            print(f"✓ Data loaded successfully!")
            print(f"  - Rows: {self.original_shape[0]:,}")
            print(f"  - Columns: {self.original_shape[1]}")
            
            self.ingestion_report['load_status'] = 'Success'
            self.ingestion_report['original_rows'] = self.original_shape[0]
            self.ingestion_report['original_columns'] = self.original_shape[1]
            
        except Exception as e:
            print(f"✗ Error loading data: {str(e)}")
            self.ingestion_report['load_status'] = f'Failed: {str(e)}'
            raise
            
    def explore_structure(self):
        """Perform initial data exploration"""
        print("\n[2/6] Exploring data structure...")
        
        print("\n--- Column Information ---")
        print(f"Columns ({len(self.df.columns)}):")
        for i, col in enumerate(self.df.columns, 1):
            dtype = self.df[col].dtype
            non_null = self.df[col].notna().sum()
            null_pct = (self.df[col].isna().sum() / len(self.df)) * 100
            print(f"  {i:2d}. {col:30s} | Type: {str(dtype):10s} | Non-null: {non_null:7,} ({100-null_pct:5.1f}%)")
        
        print("\n--- Sample Data (First 5 Rows) ---")
        print(self.df.head())
        
        print("\n--- Data Types Summary ---")
        print(self.df.dtypes.value_counts())
        
        self.ingestion_report['columns'] = list(self.df.columns)
        self.ingestion_report['dtypes'] = self.df.dtypes.astype(str).to_dict()
        
    def standardize_columns(self):
        """Standardize column names and create consistent naming"""
        print("\n[3/6] Standardizing column names...")
        
        # Create a mapping for better column names based on project requirements
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
        
        # Apply mapping where columns exist
        existing_mappings = {k: v for k, v in column_mapping.items() if k in self.df.columns}
        self.df.rename(columns=existing_mappings, inplace=True)
        
        print(f"✓ Columns standardized: {len(existing_mappings)} columns renamed")
        print(f"  New column names: {list(self.df.columns)}")
        
        self.ingestion_report['standardized_columns'] = list(self.df.columns)
        
    def handle_date_parsing(self):
        """Parse and standardize date columns"""
        print("\n[4/6] Processing date information...")
        
        # Convert date column to datetime
        if 'date' in self.df.columns:
            try:
                self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')
                print(f"✓ Date column parsed successfully")
                print(f"  Date range: {self.df['date'].min()} to {self.df['date'].max()}")
                
                # Extract additional temporal features
                self.df['year'] = self.df['date'].dt.year
                self.df['month'] = self.df['date'].dt.month
                self.df['month_name'] = self.df['date'].dt.strftime('%B')
                
                print(f"✓ Temporal features extracted: year, month, month_name")
                
                self.ingestion_report['date_range_start'] = str(self.df['date'].min())
                self.ingestion_report['date_range_end'] = str(self.df['date'].max())
                
            except Exception as e:
                print(f"✗ Error parsing dates: {str(e)}")
                self.ingestion_report['date_parsing_error'] = str(e)
        else:
            print("⚠ No 'date' column found in dataset")
            
    def standardize_pollutant_columns(self):
        """Ensure pollutant columns are numeric"""
        print("\n[5/6] Standardizing pollutant measurements...")
        
        pollutant_cols = ['SO2', 'NO2', 'PM2.5', 'RSPM', 'SPM']
        
        for col in pollutant_cols:
            if col in self.df.columns:
                # Convert to numeric, coercing errors to NaN
                original_dtype = self.df[col].dtype
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                
                non_null_count = self.df[col].notna().sum()
                print(f"  {col:10s}: {original_dtype} → float64 | Non-null values: {non_null_count:,}")
            else:
                print(f"  {col:10s}: Column not found in dataset")
        
        print("✓ Pollutant columns standardized to numeric types")
        
    def generate_summary_statistics(self):
        """Generate and display summary statistics"""
        print("\n[6/6] Generating summary statistics...")
        
        # Basic statistics
        print("\n--- Dataset Summary ---")
        print(f"Total Records: {len(self.df):,}")
        print(f"Total Features: {len(self.df.columns)}")
        print(f"Memory Usage: {self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Missing value summary
        print("\n--- Missing Values Summary ---")
        missing_summary = pd.DataFrame({
            'Column': self.df.columns,
            'Missing_Count': self.df.isna().sum().values,
            'Missing_Percentage': (self.df.isna().sum().values / len(self.df) * 100).round(2)
        })
        missing_summary = missing_summary[missing_summary['Missing_Count'] > 0].sort_values(
            'Missing_Percentage', ascending=False
        )
        
        if len(missing_summary) > 0:
            print(missing_summary.to_string(index=False))
        else:
            print("No missing values found!")
        
        # Pollutant statistics
        pollutant_cols = ['SO2', 'NO2', 'PM2.5', 'RSPM', 'SPM']
        available_pollutants = [col for col in pollutant_cols if col in self.df.columns]
        
        if available_pollutants:
            print("\n--- Pollutant Statistics ---")
            stats = self.df[available_pollutants].describe().round(2)
            print(stats)
        
        # Geographical coverage
        if 'state' in self.df.columns:
            print("\n--- Geographical Coverage ---")
            print(f"Total States: {self.df['state'].nunique()}")
            print(f"Top 5 States by Record Count:")
            top_states = self.df['state'].value_counts().head()
            for state, count in top_states.items():
                print(f"  {state:30s}: {count:,} records")
        
        if 'city' in self.df.columns:
            print(f"\nTotal Cities: {self.df['city'].nunique()}")
            print(f"Top 5 Cities by Record Count:")
            top_cities = self.df['city'].value_counts().head()
            for city, count in top_cities.items():
                print(f"  {city:30s}: {count:,} records")
        
        # Temporal coverage
        if 'year' in self.df.columns:
            print("\n--- Temporal Coverage ---")
            print(f"Years covered: {self.df['year'].min()} - {self.df['year'].max()}")
            print(f"Total years: {self.df['year'].nunique()}")
        
        self.ingestion_report['summary_generated'] = True
        
    def save_processed_data(self, output_path='data_processed.csv'):
        """Save the preprocessed data"""
        print("\n" + "=" * 80)
        print("SAVING PROCESSED DATA")
        print("=" * 80)
        
        try:
            self.df.to_csv(output_path, index=False)
            file_size = os.path.getsize(output_path) / 1024**2
            
            print(f"✓ Processed data saved successfully!")
            print(f"  Location: {output_path}")
            print(f"  Rows: {len(self.df):,}")
            print(f"  Columns: {len(self.df.columns)}")
            print(f"  File size: {file_size:.2f} MB")
            
            self.ingestion_report['output_file'] = output_path
            self.ingestion_report['final_rows'] = len(self.df)
            self.ingestion_report['final_columns'] = len(self.df.columns)
            
        except Exception as e:
            print(f"✗ Error saving data: {str(e)}")
            self.ingestion_report['save_error'] = str(e)
            
    def generate_ingestion_report(self, report_path='ingestion_report.txt'):
        """Generate a detailed ingestion report"""
        print("\n" + "=" * 80)
        print("GENERATING INGESTION REPORT")
        print("=" * 80)
        
        with open(report_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("AIR QUALITY DATA INGESTION REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("--- INGESTION SUMMARY ---\n")
            f.write(f"Load Status: {self.ingestion_report.get('load_status', 'Unknown')}\n")
            f.write(f"Original Rows: {self.ingestion_report.get('original_rows', 'N/A'):,}\n")
            f.write(f"Original Columns: {self.ingestion_report.get('original_columns', 'N/A')}\n")
            f.write(f"Final Rows: {self.ingestion_report.get('final_rows', 'N/A'):,}\n")
            f.write(f"Final Columns: {self.ingestion_report.get('final_columns', 'N/A')}\n\n")
            
            f.write("--- DATA QUALITY OVERVIEW ---\n")
            f.write(f"Missing Values: {self.df.isna().sum().sum():,} total cells\n")
            f.write(f"Missing Value %: {(self.df.isna().sum().sum() / (len(self.df) * len(self.df.columns)) * 100):.2f}%\n\n")
            
            if 'date_range_start' in self.ingestion_report:
                f.write("--- TEMPORAL COVERAGE ---\n")
                f.write(f"Start Date: {self.ingestion_report['date_range_start']}\n")
                f.write(f"End Date: {self.ingestion_report['date_range_end']}\n\n")
            
            f.write("--- COLUMNS ---\n")
            for col in self.ingestion_report.get('standardized_columns', []):
                f.write(f"  - {col}\n")
            
            f.write("\n--- OUTPUT ---\n")
            f.write(f"Processed Data: {self.ingestion_report.get('output_file', 'N/A')}\n")
            f.write(f"Report File: {report_path}\n")
            
        print(f"✓ Ingestion report saved: {report_path}")
        
    def run_pipeline(self):
        """Execute the complete data ingestion pipeline"""
        self.load_data()
        self.explore_structure()
        self.standardize_columns()
        self.handle_date_parsing()
        self.standardize_pollutant_columns()
        self.generate_summary_statistics()
        self.save_processed_data()
        self.generate_ingestion_report()
        
        print("\n" + "=" * 80)
        print("✓ STEP 1 COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nNext Steps:")
        print("  → Proceed to Step 2: Data Quality Evaluation")
        print("  → Use file: data_processed.csv")
        print("=" * 80 + "\n")
        
        return self.df


def main():
    """Main execution function"""
    # Check if data file exists
    if not os.path.exists('data.csv'):
        print("=" * 80)
        print("ERROR: Data file not found!")
        print("=" * 80)
        print("\nPlease ensure 'data.csv' is in the same directory as this script.")
        print("Extract it from the zip file if you haven't already.\n")
        print("=" * 80)
        return None
    
    # Initialize and run the ingestion pipeline
    ingestion = AirQualityDataIngestion('data.csv')
    processed_df = ingestion.run_pipeline()
    
    return processed_df


if __name__ == "__main__":
    df = main()