import pandas as pd
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime
import sys

class ElectionDataAnalyzer:
    """
    A Python-based system for analyzing election results and trends from file-based inputs.
    """
    
    def __init__(self):
        self.data = None
        self.analysis_results = {}
        self.visualizations = {}
        
    def load_data(self, file_path):
        """
        Load election data from CSV or JSON files
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
                
            if file_path.endswith('.csv'):
                self.data = pd.read_csv(file_path)
            elif file_path.endswith('.json'):
                with open(file_path, 'r') as f:
                    self.data = pd.DataFrame(json.load(f))
            else:
                raise ValueError("Unsupported file format. Please use CSV or JSON.")
                
            print("Data loaded successfully!")
            return True
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return False
    
    def validate_data(self):
        """
        Validate the structure of the election data
        """
        required_columns = ['region', 'candidate', 'party', 'votes']
        if not all(col in self.data.columns for col in required_columns):
            missing = [col for col in required_columns if col not in self.data.columns]
            raise ValueError(f"Missing required columns: {missing}")
        return True
    
    def analyze_turnout(self):
        """
        Analyze voter turnout by region
        """
        if self.data is None:
            raise ValueError("No data loaded. Please load data first.")
            
        self.validate_data()
        
        # Calculate total votes per region
        turnout = self.data.groupby('region')['votes'].sum().sort_values(ascending=False)
        self.analysis_results['turnout_by_region'] = turnout
        
        return turnout
    
    def analyze_party_performance(self):
        """
        Analyze performance by political party
        """
        if self.data is None:
            raise ValueError("No data loaded. Please load data first.")
            
        self.validate_data()
        
        # Calculate total votes per party
        party_performance = self.data.groupby('party')['votes'].sum().sort_values(ascending=False)
        self.analysis_results['party_performance'] = party_performance
        
        return party_performance
    
    def analyze_candidate_performance(self):
        """
        Analyze performance by candidate
        """
        if self.data is None:
            raise ValueError("No data loaded. Please load data first.")
            
        self.validate_data()
        
        # Calculate total votes per candidate
        candidate_performance = self.data.groupby(['candidate', 'party'])['votes'].sum().sort_values(ascending=False)
        self.analysis_results['candidate_performance'] = candidate_performance
        
        return candidate_performance
    
    def generate_visualizations(self):
        """
        Generate visualizations for the analyzed data
        """
        if not self.analysis_results:
            raise ValueError("No analysis results available. Please run analysis first.")
            
        plt.figure(figsize=(12, 8))
        
        # Turnout by region visualization
        if 'turnout_by_region' in self.analysis_results:
            plt.subplot(2, 2, 1)
            self.analysis_results['turnout_by_region'].plot(kind='bar', color='skyblue')
            plt.title('Voter Turnout by Region')
            plt.ylabel('Total Votes')
            plt.xticks(rotation=45)
            
        # Party performance visualization
        if 'party_performance' in self.analysis_results:
            plt.subplot(2, 2, 2)
            self.analysis_results['party_performance'].plot(kind='pie', autopct='%1.1f%%')
            plt.title('Vote Share by Party')
            
        # Candidate performance visualization
        if 'candidate_performance' in self.analysis_results:
            plt.subplot(2, 1, 2)
            self.analysis_results['candidate_performance'].head(10).plot(kind='barh', color='lightgreen')
            plt.title('Top 10 Performing Candidates')
            plt.xlabel('Total Votes')
            
        plt.tight_layout()
        
        # Save visualization with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"election_analysis_{timestamp}.png"
        plt.savefig(output_file)
        self.visualizations['latest'] = output_file
        print(f"Visualizations saved to {output_file}")
        
        return output_file
    
    def generate_report(self, output_file='election_report.txt'):
        """
        Generate a text report of the analysis
        """
        if not self.analysis_results:
            raise ValueError("No analysis results available. Please run analysis first.")
            
        with open(output_file, 'w') as f:
            f.write("ELECTION ANALYSIS REPORT\n")
            f.write("="*40 + "\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            if 'turnout_by_region' in self.analysis_results:
                f.write("VOTER TURNOUT BY REGION:\n")
                f.write(self.analysis_results['turnout_by_region'].to_string())
                f.write("\n\n")
                
            if 'party_performance' in self.analysis_results:
                f.write("PARTY PERFORMANCE:\n")
                f.write(self.analysis_results['party_performance'].to_string())
                f.write("\n\n")
                
            if 'candidate_performance' in self.analysis_results:
                f.write("CANDIDATE PERFORMANCE:\n")
                f.write(self.analysis_results['candidate_performance'].head(10).to_string())
                f.write("\n\n")
                
            if 'latest' in self.visualizations:
                f.write(f"Visualization saved to: {self.visualizations['latest']}\n")
                
        print(f"Report generated: {output_file}")
        return output_file

def main():
    """
    Main function to run the Election Data Analyzer
    """
    print("\nELECTION DATA ANALYZER")
    print("="*40)
    
    analyzer = ElectionDataAnalyzer()
    
    while True:
        print("\nMENU:")
        print("1. Load election data")
        print("2. Analyze voter turnout")
        print("3. Analyze party performance")
        print("4. Analyze candidate performance")
        print("5. Generate visualizations")
        print("6. Generate report")
        print("7. Exit")
        
        choice = input("Enter your choice (1-7): ")
        
        try:
            if choice == '1':
                file_path = input("Enter path to election data file (CSV/JSON): ")
                if analyzer.load_data(file_path):
                    print("Data loaded successfully!")
                    
            elif choice == '2':
                result = analyzer.analyze_turnout()
                print("\nVoter Turnout by Region:")
                print(result)
                
            elif choice == '3':
                result = analyzer.analyze_party_performance()
                print("\nParty Performance:")
                print(result)
                
            elif choice == '4':
                result = analyzer.analyze_candidate_performance()
                print("\nCandidate Performance (Top 10):")
                print(result.head(10))
                
            elif choice == '5':
                output_file = analyzer.generate_visualizations()
                print(f"Visualizations saved to {output_file}")
                
            elif choice == '6':
                output_file = analyzer.generate_report()
                print(f"Report generated: {output_file}")
                
            elif choice == '7':
                print("Exiting Election Data Analyzer. Goodbye!")
                break
                
            else:
                print("Invalid choice. Please enter a number between 1 and 7.")
                
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()