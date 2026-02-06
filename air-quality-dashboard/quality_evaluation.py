"""
AI-Driven Air Quality Insight Confidence Dashboard
Step 2: Data Quality Evaluation (ML)

This script performs:
1. Missing value analysis
2. Outlier detection using Z-score
3. Invalid value detection
4. Duplicate detection
5. Consistency checks
6. Data Quality Score calculation (0-100)
7. Confidence classification (High/Medium/Low)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import os
warnings.filterwarnings('ignore')

class DataQualityEvaluator:
    """Evaluate data quality using ML techniques"""
    
    def __init__(self, filepath):
        """
        Initialize the data quality evaluator
        
        Parameters:
        -----------
        filepath : str
            Path to the processed CSV file
        """
        self.filepath = filepath
        self.df = None
        self.quality_metrics = {}
        self.quality_scores = None
        
    def load_data(self):
        """Load the processed data"""
        print("=" * 80)
        print("STEP 2: DATA QUALITY EVALUATION (ML)")
        print("=" * 80)
        print("\n[1/7] Loading processed data...")
        
        try:
            self.df = pd.read_csv(self.filepath)
            self.df['date'] = pd.to_datetime(self.df['date'])
            
            print(f"✓ Data loaded successfully!")
            print(f"  - Records: {len(self.df):,}")
            print(f"  - Features: {len(self.df.columns)}")
            
        except Exception as e:
            print(f"✗ Error loading data: {str(e)}")
            raise
    
    def analyze_missing_values(self):
        """Analyze missing value patterns"""
        print("\n[2/7] Analyzing missing values...")
        
        # Calculate missing percentages
        missing_data = pd.DataFrame({
            'column': self.df.columns,
            'missing_count': self.df.isna().sum().values,
            'missing_percentage': (self.df.isna().sum().values / len(self.df) * 100).round(2)
        })
        
        # Calculate per-row missing percentage
        self.df['missing_values_count'] = self.df.isna().sum(axis=1)
        self.df['missing_values_percentage'] = (self.df['missing_values_count'] / len(self.df.columns) * 100).round(2)
        
        # Store metrics
        self.quality_metrics['total_missing_cells'] = self.df.isna().sum().sum()
        self.quality_metrics['missing_percentage'] = (self.quality_metrics['total_missing_cells'] / 
                                                      (len(self.df) * len(self.df.columns)) * 100)
        
        print(f"✓ Missing value analysis complete")
        print(f"  - Total missing cells: {self.quality_metrics['total_missing_cells']:,}")
        print(f"  - Overall missing percentage: {self.quality_metrics['missing_percentage']:.2f}%")
        
        # Show columns with most missing data
        top_missing = missing_data.nlargest(5, 'missing_percentage')
        print(f"\n  Top 5 columns with missing data:")
        for _, row in top_missing.iterrows():
            print(f"    {row['column']:25s}: {row['missing_percentage']:6.2f}%")
    
    def detect_outliers_zscore(self):
        """Detect outliers using Z-score method"""
        print("\n[3/7] Detecting outliers using Z-score method...")
        
        pollutants = ['SO2', 'NO2', 'PM2.5', 'RSPM', 'SPM']
        available_pollutants = [p for p in pollutants if p in self.df.columns]
        
        outlier_counts = {}
        
        for pollutant in available_pollutants:
            # Calculate Z-scores
            data = self.df[pollutant].dropna()
            if len(data) > 0:
                mean = data.mean()
                std = data.std()
                
                # Calculate Z-scores only for non-null values
                z_scores = np.abs((self.df[pollutant] - mean) / std)
                
                # Flag outliers (|Z| > 3)
                outliers = z_scores > 3
                outlier_count = outliers.sum()
                outlier_counts[pollutant] = outlier_count
                
                # Create outlier flag column
                self.df[f'{pollutant}_outlier'] = outliers
                
                outlier_pct = (outlier_count / len(data)) * 100
                print(f"  {pollutant:10s}: {outlier_count:6,} outliers ({outlier_pct:5.2f}%)")
        
        # Calculate total outlier score per row
        outlier_columns = [col for col in self.df.columns if col.endswith('_outlier')]
        self.df['outlier_count'] = self.df[outlier_columns].sum(axis=1)
        
        self.quality_metrics['outlier_counts'] = outlier_counts
        print(f"✓ Outlier detection complete")
    
    def detect_invalid_values(self):
        """Detect invalid or impossible values"""
        print("\n[4/7] Detecting invalid values...")
        
        pollutants = ['SO2', 'NO2', 'PM2.5', 'RSPM', 'SPM']
        available_pollutants = [p for p in pollutants if p in self.df.columns]
        
        invalid_counts = {}
        
        for pollutant in available_pollutants:
            # Check for negative values (impossible for concentrations)
            negative_count = (self.df[pollutant] < 0).sum()
            
            # Check for zero values (suspicious but not always invalid)
            zero_count = (self.df[pollutant] == 0).sum()
            
            # Flag invalid values
            self.df[f'{pollutant}_invalid'] = self.df[pollutant] < 0
            
            invalid_counts[pollutant] = {
                'negative': negative_count,
                'zero': zero_count
            }
            
            if negative_count > 0:
                print(f"  {pollutant:10s}: {negative_count:6,} negative values (INVALID)")
            else:
                print(f"  {pollutant:10s}: No invalid values")
        
        # Calculate total invalid values per row
        invalid_columns = [col for col in self.df.columns if col.endswith('_invalid')]
        self.df['invalid_count'] = self.df[invalid_columns].sum(axis=1)
        
        self.quality_metrics['invalid_counts'] = invalid_counts
        print(f"✓ Invalid value detection complete")
    
    def detect_duplicates(self):
        """Detect duplicate records"""
        print("\n[5/7] Detecting duplicate records...")
        
        # Check for exact duplicates
        duplicates = self.df.duplicated()
        duplicate_count = duplicates.sum()
        
        # Check for duplicates based on key fields
        key_fields = ['station_code', 'date', 'city']
        available_keys = [k for k in key_fields if k in self.df.columns]
        
        if available_keys:
            key_duplicates = self.df.duplicated(subset=available_keys, keep=False)
            key_duplicate_count = key_duplicates.sum()
        else:
            key_duplicate_count = 0
        
        self.df['is_duplicate'] = duplicates
        
        self.quality_metrics['duplicate_count'] = duplicate_count
        self.quality_metrics['key_duplicate_count'] = key_duplicate_count
        
        print(f"✓ Duplicate detection complete")
        print(f"  - Exact duplicates: {duplicate_count:,}")
        print(f"  - Key-based duplicates: {key_duplicate_count:,}")
    
    def check_consistency(self):
        """Check data consistency"""
        print("\n[6/7] Checking data consistency...")
        
        consistency_issues = 0
        
        # Check 1: Date consistency (dates should be in valid range)
        if 'date' in self.df.columns:
            invalid_dates = self.df['date'].isna().sum()
            consistency_issues += invalid_dates
        
        # Check 2: Year-Date consistency
        if 'year' in self.df.columns and 'date' in self.df.columns:
            year_mismatch = (self.df['year'] != self.df['date'].dt.year).sum()
            consistency_issues += year_mismatch
        
        # Check 3: Pollutant relationships (optional - some pollutants correlate)
        # PM2.5 should generally be less than or equal to PM10/RSPM
        if 'PM2.5' in self.df.columns and 'RSPM' in self.df.columns:
            # Check where both values exist
            both_exist = self.df['PM2.5'].notna() & self.df['RSPM'].notna()
            inconsistent = (self.df.loc[both_exist, 'PM2.5'] > self.df.loc[both_exist, 'RSPM']).sum()
            consistency_issues += inconsistent
            
            if inconsistent > 0:
                print(f"  ⚠ PM2.5 > RSPM inconsistency: {inconsistent:,} cases")
        
        self.quality_metrics['consistency_issues'] = consistency_issues
        print(f"✓ Consistency check complete")
        print(f"  - Total consistency issues: {consistency_issues:,}")
    
    def calculate_quality_scores(self):
        """Calculate data quality score for each record (0-100)"""
        print("\n[7/7] Calculating data quality scores...")
        
        # Initialize score at 100
        self.df['quality_score'] = 100.0
        
        # Penalty 1: Missing values (-10 points per 10% missing)
        missing_penalty = (self.df['missing_values_percentage'] / 10) * 10
        self.df['quality_score'] -= missing_penalty
        
        # Penalty 2: Outliers (-5 points per outlier)
        outlier_penalty = self.df['outlier_count'] * 5
        self.df['quality_score'] -= outlier_penalty
        
        # Penalty 3: Invalid values (-20 points per invalid value)
        invalid_penalty = self.df['invalid_count'] * 20
        self.df['quality_score'] -= invalid_penalty
        
        # Penalty 4: Duplicates (-30 points if duplicate)
        duplicate_penalty = self.df['is_duplicate'].astype(int) * 30
        self.df['quality_score'] -= duplicate_penalty
        
        # Ensure score is between 0 and 100
        self.df['quality_score'] = self.df['quality_score'].clip(0, 100)
        
        # Calculate statistics
        avg_score = self.df['quality_score'].mean()
        median_score = self.df['quality_score'].median()
        
        print(f"✓ Quality scores calculated")
        print(f"  - Average quality score: {avg_score:.2f}/100")
        print(f"  - Median quality score: {median_score:.2f}/100")
        
        # Score distribution
        high_quality = (self.df['quality_score'] >= 80).sum()
        medium_quality = ((self.df['quality_score'] >= 50) & (self.df['quality_score'] < 80)).sum()
        low_quality = (self.df['quality_score'] < 50).sum()
        
        print(f"\n  Score Distribution:")
        print(f"    High (≥80):   {high_quality:7,} ({high_quality/len(self.df)*100:5.1f}%)")
        print(f"    Medium (50-79): {medium_quality:7,} ({medium_quality/len(self.df)*100:5.1f}%)")
        print(f"    Low (<50):    {low_quality:7,} ({low_quality/len(self.df)*100:5.1f}%)")
    
    def classify_confidence(self):
        """Classify records into confidence levels"""
        print("\n[8/8] Classifying confidence levels...")
        
        def assign_confidence(row):
            """Assign confidence level based on quality metrics"""
            score = row['quality_score']
            missing_pct = row['missing_values_percentage']
            outliers = row['outlier_count']
            invalid = row['invalid_count']
            
            # High confidence criteria
            if score >= 80 and missing_pct < 10 and outliers == 0 and invalid == 0:
                return 'High'
            
            # Low confidence criteria
            elif score < 50 or missing_pct > 30 or invalid > 0:
                return 'Low'
            
            # Medium confidence (everything else)
            else:
                return 'Medium'
        
        self.df['confidence_level'] = self.df.apply(assign_confidence, axis=1)
        
        # Calculate distribution
        confidence_dist = self.df['confidence_level'].value_counts()
        
        print(f"✓ Confidence classification complete")
        print(f"\n  Confidence Distribution:")
        for level in ['High', 'Medium', 'Low']:
            count = confidence_dist.get(level, 0)
            pct = (count / len(self.df)) * 100
            print(f"    {level:8s}: {count:7,} ({pct:5.1f}%)")
        
        self.quality_metrics['confidence_distribution'] = confidence_dist.to_dict()
    
    def save_quality_data(self, output_path='data_with_quality_scores.csv'):
        """Save data with quality scores and confidence levels"""
        print("\n" + "=" * 80)
        print("SAVING DATA WITH QUALITY SCORES")
        print("=" * 80)
        
        try:
            # Select columns to save
            self.df.to_csv(output_path, index=False)
            
            file_size = os.path.getsize(output_path) / (1024**2)
            
            print(f"✓ Data saved successfully!")
            print(f"  Location: {output_path}")
            print(f"  Rows: {len(self.df):,}")
            print(f"  Columns: {len(self.df.columns)}")
            print(f"  File size: {file_size:.2f} MB")
            
        except Exception as e:
            print(f"✗ Error saving data: {str(e)}")
    
    def generate_quality_report(self, report_path='data_quality_report.txt'):
        """Generate comprehensive data quality report"""
        print("\n" + "=" * 80)
        print("GENERATING DATA QUALITY REPORT")
        print("=" * 80)
        
        with open(report_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("DATA QUALITY EVALUATION REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("--- DATASET OVERVIEW ---\n")
            f.write(f"Total Records: {len(self.df):,}\n")
            f.write(f"Total Features: {len(self.df.columns)}\n\n")
            
            f.write("--- MISSING VALUES ---\n")
            f.write(f"Total Missing Cells: {self.quality_metrics['total_missing_cells']:,}\n")
            f.write(f"Missing Percentage: {self.quality_metrics['missing_percentage']:.2f}%\n\n")
            
            f.write("--- OUTLIERS (Z-Score Method) ---\n")
            for pollutant, count in self.quality_metrics['outlier_counts'].items():
                f.write(f"{pollutant}: {count:,} outliers\n")
            f.write("\n")
            
            f.write("--- INVALID VALUES ---\n")
            for pollutant, counts in self.quality_metrics['invalid_counts'].items():
                f.write(f"{pollutant}:\n")
                f.write(f"  Negative values: {counts['negative']:,}\n")
                f.write(f"  Zero values: {counts['zero']:,}\n")
            f.write("\n")
            
            f.write("--- DUPLICATES ---\n")
            f.write(f"Exact duplicates: {self.quality_metrics['duplicate_count']:,}\n")
            f.write(f"Key-based duplicates: {self.quality_metrics['key_duplicate_count']:,}\n\n")
            
            f.write("--- CONSISTENCY ---\n")
            f.write(f"Consistency issues found: {self.quality_metrics['consistency_issues']:,}\n\n")
            
            f.write("--- QUALITY SCORES ---\n")
            f.write(f"Average Score: {self.df['quality_score'].mean():.2f}/100\n")
            f.write(f"Median Score: {self.df['quality_score'].median():.2f}/100\n")
            f.write(f"Min Score: {self.df['quality_score'].min():.2f}/100\n")
            f.write(f"Max Score: {self.df['quality_score'].max():.2f}/100\n\n")
            
            f.write("--- CONFIDENCE LEVELS ---\n")
            for level, count in self.quality_metrics['confidence_distribution'].items():
                pct = (count / len(self.df)) * 100
                f.write(f"{level}: {count:,} ({pct:.2f}%)\n")
            
            f.write("\n--- OUTPUT FILES ---\n")
            f.write("Data with quality scores: data_with_quality_scores.csv\n")
            f.write(f"Quality report: {report_path}\n")
        
        print(f"✓ Quality report saved: {report_path}")
    
    def run_evaluation(self):
        """Execute the complete data quality evaluation pipeline"""
        self.load_data()
        self.analyze_missing_values()
        self.detect_outliers_zscore()
        self.detect_invalid_values()
        self.detect_duplicates()
        self.check_consistency()
        self.calculate_quality_scores()
        self.classify_confidence()
        self.save_quality_data()
        self.generate_quality_report()
        
        print("\n" + "=" * 80)
        print("✓ STEP 2 COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nNext Steps:")
        print("  → Proceed to Step 3: Dashboard Visualization")
        print("  → Use file: data_with_quality_scores.csv")
        print("=" * 80 + "\n")
        
        return self.df


def main():
    """Main execution function"""
    # Check if processed data exists
    if not os.path.exists('data_processed.csv'):
        print("=" * 80)
        print("ERROR: Processed data file not found!")
        print("=" * 80)
        print("\nPlease run Step 1 first: python step1_data_ingestion.py")
        print("This will create the required 'data_processed.csv' file.\n")
        print("=" * 80)
        return None
    
    # Initialize and run the evaluation pipeline
    evaluator = DataQualityEvaluator('data_processed.csv')
    df_with_quality = evaluator.run_evaluation()
    
    return df_with_quality


if __name__ == "__main__":
    df = main()