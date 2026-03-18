"""
Step 3: LLM Explanations with Groq API (Key in Code)
FASTEST and most RELIABLE option!
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import os
import json
import time
warnings.filterwarnings('ignore')

try:
    import requests
except ImportError:
    print("Please install: pip install requests")
    exit(1)


# ============================================================================
# 🔑 PUT YOUR GROQ API KEY HERE:
# ============================================================================
GROQ_API_KEY = "gsk_YOUR_KEY_HERE"  # ← REPLACE THIS WITH YOUR ACTUAL KEY
# Get free key from: https://console.groq.com/keys
# ============================================================================


class GroqLLMEngine:
    """Generate AI explanations using Groq API (FAST!)"""
    
    def __init__(self, filepath, api_key=GROQ_API_KEY):
        """Initialize with Groq API"""
        self.filepath = filepath
        self.df = None
        self.api_key = api_key
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "mixtral-8x7b-32768"  # Fast and powerful!
        self.explanations = []
        
        print(f"\n🤖 Using Groq API with Mixtral-8x7B")
        print(f"   Key: {api_key[:15]}...{api_key[-5:]}" if len(api_key) > 20 else "   Key: [Please set your key above]")
        
    def load_data(self):
        """Load the quality-scored data"""
        print("\n" + "=" * 80)
        print("STEP 3: LLM INTEGRATION WITH GROQ (FASTEST!)")
        print("=" * 80)
        print("\n[1/6] Loading quality-scored data...")
        
        try:
            self.df = pd.read_csv(self.filepath)
            self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')
            
            print(f"✓ Data loaded successfully!")
            print(f"  - Records: {len(self.df):,}")
            print(f"  - Features: {len(self.df.columns)}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error loading data: {str(e)}")
            return False
    
    def check_api_connection(self):
        """Test Groq API connection"""
        print("\n[2/6] Testing Groq API connection...")
        
        if self.api_key == "gsk_YOUR_KEY_HERE":
            print("❌ ERROR: Please set your Groq API key at the top of this file!")
            print("\nSteps:")
            print("  1. Get free key: https://console.groq.com/keys")
            print("  2. Open this file in a text editor")
            print("  3. Find line ~28: GROQ_API_KEY = \"gsk_YOUR_KEY_HERE\"")
            print("  4. Replace with your actual key")
            print("  5. Save and run again")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": "Say 'API works!'"}
                ],
                "max_tokens": 10,
                "temperature": 0.1
            }
            
            print("  Sending test request...")
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=10)
            
            print(f"  Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                test_response = result['choices'][0]['message']['content']
                print(f"  ✅ Groq API working!")
                print(f"  Test response: {test_response}")
                return True
            elif response.status_code == 401:
                print(f"  ❌ Authentication failed!")
                print(f"  Your API key may be incorrect.")
                print(f"  Get a new key from: https://console.groq.com/keys")
                return False
            else:
                print(f"  ❌ Error {response.status_code}: {response.text[:200]}")
                return False
                
        except requests.exceptions.Timeout:
            print(f"  ❌ Connection timeout")
            print(f"  Check your internet connection")
            return False
        except Exception as e:
            print(f"  ❌ Connection error: {str(e)}")
            return False
    
    def generate_ai_explanation(self, prompt, max_retries=2):
        """Generate explanation using Groq API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an air quality data expert. Provide clear, professional 3-4 sentence explanations focusing on data quality, reliability, and recommended use."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 300,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    explanation = result['choices'][0]['message']['content'].strip()
                    return explanation
                elif response.status_code == 429:
                    # Rate limit
                    if attempt < max_retries - 1:
                        print(f"      Rate limit, waiting 5s...")
                        time.sleep(5)
                        continue
                    return None
                else:
                    print(f"      API error {response.status_code}")
                    return None
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"      Timeout, retrying...")
                    time.sleep(3)
                    continue
                return None
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return None
        
        return None
    
    def generate_rule_based_explanation(self, row):
        """Fallback rule-based explanation"""
        quality_score = row['quality_score']
        confidence = row['confidence_level']
        missing_pct = row['missing_values_percentage']
        outlier_count = row.get('outlier_count', 0)
        
        if quality_score >= 90:
            quality_desc = "excellent"
        elif quality_score >= 80:
            quality_desc = "good"
        elif quality_score >= 70:
            quality_desc = "fair"
        elif quality_score >= 50:
            quality_desc = "poor"
        else:
            quality_desc = "very poor"
        
        explanation = f"This air quality measurement has {quality_desc} data quality "
        explanation += f"(score: {quality_score:.1f}/100). "
        
        if confidence == 'High':
            explanation += "The data is highly reliable with minimal issues, making it suitable for detailed analysis and regulatory compliance. "
        elif confidence == 'Medium':
            explanation += "The data has moderate reliability with some quality concerns, suitable for general trend analysis. "
        else:
            explanation += "The data has low reliability with significant quality issues, recommended for exploratory analysis only. "
        
        if missing_pct > 30:
            explanation += f"Significant missing data ({missing_pct:.1f}%) reduces reliability. "
        elif missing_pct > 10:
            explanation += f"Some data points missing ({missing_pct:.1f}%). "
        elif missing_pct > 0:
            explanation += f"Minimal missing data ({missing_pct:.1f}%). "
        
        if outlier_count > 2:
            explanation += f"Multiple outliers detected ({outlier_count}), indicating unusual pollution events. "
        elif outlier_count > 0:
            explanation += f"{outlier_count} outlier(s) detected. "
        
        if confidence == 'High':
            explanation += "Recommended for: regulatory compliance, health advisories, and predictive modeling."
        elif confidence == 'Medium':
            explanation += "Recommended for: general monitoring and trend observation."
        else:
            explanation += "Use for data exploration only."
        
        return explanation
    
    def create_sample_explanations(self, use_ai=True):
        """Create explanations for sample records"""
        print("\n[3/6] Generating sample explanations with AI...")
        
        # Select diverse samples
        samples = []
        
        high_conf = self.df[self.df['confidence_level'] == 'High'].head(1)
        if len(high_conf) > 0:
            samples.append(('High Confidence Example', high_conf.iloc[0]))
        
        medium_conf = self.df[self.df['confidence_level'] == 'Medium'].head(1)
        if len(medium_conf) > 0:
            samples.append(('Medium Confidence Example', medium_conf.iloc[0]))
        
        low_conf = self.df[self.df['confidence_level'] == 'Low'].head(1)
        if len(low_conf) > 0:
            samples.append(('Low Confidence Example', low_conf.iloc[0]))
        
        best_quality = self.df.nlargest(1, 'quality_score')
        if len(best_quality) > 0:
            samples.append(('Best Quality Example', best_quality.iloc[0]))
        
        worst_quality = self.df.nsmallest(1, 'quality_score')
        if len(worst_quality) > 0:
            samples.append(('Worst Quality Example', worst_quality.iloc[0]))
        
        explanations = []
        ai_success_count = 0
        
        for label, row in samples:
            print(f"\n  Generating: {label}")
            
            explanation = None
            
            if use_ai:
                # Create prompt for AI
                prompt = f"""Analyze this air quality measurement:

Quality Score: {row['quality_score']:.1f}/100
Confidence Level: {row['confidence_level']}
Missing Data: {row['missing_values_percentage']:.1f}%
Outliers: {row.get('outlier_count', 0)}
City: {row.get('city', 'Unknown')}
Date: {row.get('date', 'Unknown')}

Provide a professional 3-4 sentence explanation covering:
1. Overall data quality assessment
2. Reliability and confidence level justification
3. Recommended usage (regulatory, monitoring, or exploratory)"""
                
                explanation = self.generate_ai_explanation(prompt)
                
                if explanation:
                    print(f"    ✅ AI generated ({len(explanation)} chars)")
                    ai_success_count += 1
                else:
                    print(f"    ⚠️  AI failed, using rule-based")
                    explanation = self.generate_rule_based_explanation(row)
            else:
                explanation = self.generate_rule_based_explanation(row)
                print(f"    ✓ Rule-based generated")
            
            explanations.append({
                'label': label,
                'city': row.get('city', 'Unknown'),
                'date': str(row.get('date', 'Unknown')),
                'quality_score': float(row['quality_score']),
                'confidence_level': row['confidence_level'],
                'missing_percentage': float(row['missing_values_percentage']),
                'outlier_count': int(row.get('outlier_count', 0)),
                'explanation': explanation
            })
        
        self.explanations = explanations
        print(f"\n✓ Generated {len(explanations)} explanations")
        if use_ai:
            print(f"  AI-generated: {ai_success_count}/{len(explanations)}")
            print(f"  Rule-based: {len(explanations) - ai_success_count}/{len(explanations)}")
        
        return explanations
    
    def create_city_summaries(self, top_n=10):
        """Create summaries for top cities"""
        print("\n[4/6] Generating city-level summaries...")
        
        top_cities = self.df['city'].value_counts().head(top_n).index
        
        for i, city in enumerate(top_cities, 1):
            city_data = self.df[self.df['city'] == city]
            avg_quality = city_data['quality_score'].mean()
            print(f"    {i:2d}/{top_n}: {city:20s} (Avg Quality: {avg_quality:.1f}/100)")
        
        print(f"✓ Analyzed {top_n} cities")
        return []
    
    def create_overall_insights(self):
        """Generate overall dataset insights"""
        print("\n[5/6] Generating overall dataset insights...")
        
        insights = {
            'total_records': len(self.df),
            'avg_quality_score': self.df['quality_score'].mean(),
            'median_quality_score': self.df['quality_score'].median(),
            'high_confidence_pct': (self.df['confidence_level'] == 'High').sum() / len(self.df) * 100,
            'medium_confidence_pct': (self.df['confidence_level'] == 'Medium').sum() / len(self.df) * 100,
            'low_confidence_pct': (self.df['confidence_level'] == 'Low').sum() / len(self.df) * 100,
        }
        
        narrative = f"""This air quality dataset contains {insights['total_records']:,} measurements.

Quality Assessment: Average score {insights['avg_quality_score']:.1f}/100 (median {insights['median_quality_score']:.1f}/100).

Confidence Distribution:
- High Confidence: {insights['high_confidence_pct']:.1f}% (highly reliable, suitable for regulatory use)
- Medium Confidence: {insights['medium_confidence_pct']:.1f}% (moderate reliability, good for trends)
- Low Confidence: {insights['low_confidence_pct']:.1f}% (exploratory use only)

Recommendation: Prioritize high and medium confidence measurements for decision-making. 
Low confidence data should be flagged for verification or re-collection."""
        
        insights['narrative'] = narrative
        
        print("✓ Overall insights generated")
        return insights
    
    def save_explanations(self):
        """Save explanations to JSON"""
        print("\n[6/6] Saving explanations...")
        
        output = {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'api_provider': 'Groq',
            'model': self.model,
            'sample_explanations': self.explanations,
            'metadata': {
                'total_records': len(self.df),
                'method': 'AI-powered'
            }
        }
        
        try:
            with open('llm_explanations.json', 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            
            print("✓ Saved: llm_explanations.json")
            return True
            
        except Exception as e:
            print(f"✗ Error saving: {str(e)}")
            return False
    
    def generate_report(self):
        """Generate human-readable report"""
        print("\n" + "=" * 80)
        print("GENERATING EXPLANATION REPORT")
        print("=" * 80)
        
        try:
            with open('explanation_report.txt', 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("AI-DRIVEN AIR QUALITY INSIGHT EXPLANATIONS\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"AI Provider: Groq (Mixtral-8x7B)\n")
                f.write(f"Method: AI-powered explanations\n\n")
                
                # Overall insights
                insights = self.create_overall_insights()
                f.write("=" * 80 + "\n")
                f.write("OVERALL DATASET INSIGHTS\n")
                f.write("=" * 80 + "\n\n")
                f.write(insights['narrative'])
                f.write("\n\n")
                
                # Sample explanations
                f.write("=" * 80 + "\n")
                f.write("SAMPLE MEASUREMENT EXPLANATIONS (AI-GENERATED)\n")
                f.write("=" * 80 + "\n\n")
                
                for exp in self.explanations:
                    f.write(f"[{exp['label']}]\n")
                    f.write("-" * 80 + "\n")
                    f.write(f"Location: {exp['city']}\n")
                    f.write(f"Date: {exp['date']}\n")
                    f.write(f"Quality Score: {exp['quality_score']:.1f}/100\n")
                    f.write(f"Confidence Level: {exp['confidence_level']}\n")
                    f.write(f"Missing Data: {exp['missing_percentage']:.1f}%\n")
                    f.write(f"Outliers: {exp['outlier_count']}\n\n")
                    f.write("AI Explanation:\n")
                    f.write(exp['explanation'])
                    f.write("\n\n")
                
                # City summaries
                f.write("=" * 80 + "\n")
                f.write("TOP 10 CITIES BY MONITORING ACTIVITY\n")
                f.write("=" * 80 + "\n\n")
                
                top_cities = self.df['city'].value_counts().head(10)
                for i, (city, count) in enumerate(top_cities.items(), 1):
                    city_data = self.df[self.df['city'] == city]
                    avg_quality = city_data['quality_score'].mean()
                    high_conf_pct = (city_data['confidence_level'] == 'High').sum() / len(city_data) * 100
                    
                    f.write(f"{i:2d}. {city}\n")
                    f.write(f"    Total Measurements: {count:,}\n")
                    f.write(f"    Average Quality Score: {avg_quality:.1f}/100\n")
                    f.write(f"    High Confidence: {high_conf_pct:.1f}%\n\n")
            
            print("✓ Saved: explanation_report.txt")
            return True
            
        except Exception as e:
            print(f"✗ Error generating report: {str(e)}")
            return False
    
    def run_pipeline(self):
        """Execute complete explanation pipeline"""
        if not self.load_data():
            return
        
        api_available = self.check_api_connection()
        
        if not api_available:
            print("\n⚠️  Will use rule-based explanations")
            print("    To use AI: Set your Groq API key at top of this file")
        
        self.create_sample_explanations(use_ai=api_available)
        self.create_city_summaries()
        self.save_explanations()
        self.generate_report()
        
        print("\n" + "=" * 80)
        print("✓ STEP 3 COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"\nMethod used: {'AI-powered (Groq)' if api_available else 'Rule-based'}")
        print("\nGenerated files:")
        print("  → llm_explanations.json")
        print("  → explanation_report.txt")
        print("\nNext steps:")
        print("  → Review explanation_report.txt for insights")
        print("  → Use for dashboard creation")
        print("  → Include in project presentation")
        print("=" * 80 + "\n")


def main():
    """Main execution function"""
    # Check if data exists
    if not os.path.exists('data_with_quality_scores.csv'):
        print("=" * 80)
        print("ERROR: Quality-scored data not found!")
        print("=" * 80)
        print("\nPlease run Step 2 first:")
        print("    python step2_quality_evaluation.py")
        print("\nThis creates the required 'data_with_quality_scores.csv' file.\n")
        print("=" * 80)
        return
    
    # Initialize and run
    engine = GroqLLMEngine('data_with_quality_scores.csv')
    engine.run_pipeline()


if __name__ == "__main__":
    main()