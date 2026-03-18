"""
Run Complete Step 3 Analysis
LLM Explanations + Dashboard Preparation
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required packages are installed"""
    required = ['pandas', 'numpy', 'requests']
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
        print("=" * 80)
        return False
    return True

def check_data_file():
    """Check if data_with_quality_scores.csv exists"""
    if not os.path.exists('data_with_quality_scores.csv'):
        print("=" * 80)
        print("DATA FILE NOT FOUND")
        print("=" * 80)
        print("\nError: 'data_with_quality_scores.csv' file not found\n")
        print("Please run Step 2 first:")
        print("    python step2_quality_evaluation.py\n")
        print("This will create the required quality-scored data file.\n")
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
    print("AI-DRIVEN AIR QUALITY DASHBOARD - STEP 3 RUNNER")
    print("=" * 80)
    print("\nThis script will:")
    print("  1. Check dependencies")
    print("  2. Generate LLM-based explanations")
    print("  3. Prepare data for dashboard")
    print("  4. Create visualization-ready datasets\n")
    
    # Check dependencies
    print("[1/4] Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ All dependencies installed\n")
    
    # Check data file
    print("[2/4] Checking for quality-scored data...")
    if not check_data_file():
        sys.exit(1)
    print("✅ Quality-scored data file found\n")
    
    # Run LLM explanations
    print("[3/4] Generating LLM explanations...")
    llm_success = run_script('step3_llm_explanations.py')
    if not llm_success:
        print("\n⚠️  LLM explanations had issues but continuing...")
    
    # Run dashboard preparation
    print("\n[4/4] Preparing dashboard data...")
    if not run_script('step3_dashboard_prep.py'):
        print("\n⚠️  Dashboard preparation had issues. Check the output above.")
        sys.exit(1)
    
    # Final summary
    print("\n" + "=" * 80)
    print("🎉 STEP 3 COMPLETE - ALL TASKS FINISHED SUCCESSFULLY!")
    print("=" * 80)
    print("\nGenerated Files:")
    print("\n📊 LLM Explanations:")
    print("  📄 llm_explanations.json")
    print("  📄 explanation_report.txt")
    print("\n📈 Dashboard Data:")
    print("  📁 dashboard_data/")
    print("      ├── city_summary.csv")
    print("      ├── time_series.csv")
    print("      ├── confidence_distribution.csv")
    print("      ├── outlier_summary.csv")
    print("      ├── sampled_data.csv")
    print("      └── DASHBOARD_GUIDE.txt")
    print("\n" + "=" * 80)
    print("Next Steps:")
    print("  1. Review explanation_report.txt for AI-generated insights")
    print("  2. Import dashboard_data/*.csv into Power BI or Tableau")
    print("  3. Follow DASHBOARD_GUIDE.txt for visualization recommendations")
    print("  4. Create interactive dashboard with confidence indicators")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
