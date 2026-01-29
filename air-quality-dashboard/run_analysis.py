"""
Run Complete Step 1 Analysis
This script runs both data ingestion and visualization automatically
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required packages are installed"""
    required = ['pandas', 'numpy', 'matplotlib', 'seaborn']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("=" * 80)
        print("MISSING REQUIRED PACKAGES")
        print("=" * 80)
        print(f"\nThe following packages are not installed: {', '.join(missing)}\n")
        print("Please install them using:")
        print(f"    pip install {' '.join(missing)}\n")
        print("Or install all requirements:")
        print("    pip install -r requirements.txt\n")
        print("=" * 80)
        return False
    return True

def check_data_file():
    """Check if data.csv exists"""
    if not os.path.exists('data.csv'):
        print("=" * 80)
        print("DATA FILE NOT FOUND")
        print("=" * 80)
        print("\nError: 'data.csv' file not found in current directory\n")
        print("Please ensure:")
        print("  1. You have extracted data.csv from the zip file")
        print("  2. data.csv is in the same folder as this script")
        print("  3. You are running this script from the correct directory\n")
        print("=" * 80)
        return False
    return True

def run_script(script_name):
    """Run a Python script and handle errors"""
    try:
        print(f"\n{'=' * 80}")
        print(f"RUNNING: {script_name}")
        print("=" * 80 + "\n")
        
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=False, 
                              text=True)
        
        if result.returncode != 0:
            print(f"\n⚠️  Warning: {script_name} completed with errors")
            return False
        else:
            print(f"\n✅ {script_name} completed successfully!")
            return True
            
    except Exception as e:
        print(f"\n❌ Error running {script_name}: {str(e)}")
        return False

def main():
    """Main execution function"""
    print("=" * 80)
    print("AI-DRIVEN AIR QUALITY DASHBOARD - STEP 1 RUNNER")
    print("=" * 80)
    print("\nThis script will:")
    print("  1. Check dependencies")
    print("  2. Run data ingestion")
    print("  3. Generate visualizations")
    print("  4. Create reports\n")
    
    # Check dependencies
    print("[1/4] Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ All dependencies installed\n")
    
    # Check data file
    print("[2/4] Checking for data file...")
    if not check_data_file():
        sys.exit(1)
    print("✅ Data file found\n")
    
    # Run ingestion
    print("[3/4] Running data ingestion...")
    if not run_script('step1_data_ingestion.py'):
        print("\n⚠️  Data ingestion had issues. Check the output above.")
        sys.exit(1)
    
    # Run visualizations
    print("\n[4/4] Generating visualizations...")
    if not run_script('step1_visualizations.py'):
        print("\n⚠️  Visualization generation had issues. Check the output above.")
        sys.exit(1)
    
    # Final summary
    print("\n" + "=" * 80)
    print("🎉 STEP 1 COMPLETE - ALL TASKS FINISHED SUCCESSFULLY!")
    print("=" * 80)
    print("\nGenerated Files:")
    print("  📄 data_processed.csv")
    print("  📄 ingestion_report.txt")
    print("  📄 data_statistics_report.txt")
    print("  📁 visualizations/")
    print("      ├── 01_missing_data.png")
    print("      ├── 02_temporal_coverage.png")
    print("      ├── 03_geographical_distribution.png")
    print("      └── 04_pollutant_distributions.png")
    print("\n" + "=" * 80)
    print("Next: Review outputs and proceed to Step 2 - Data Quality Evaluation")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()