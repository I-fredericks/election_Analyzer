import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import json
import os
from datetime import datetime

class ElectionAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Election Data Analyzer - Enhanced Visualization")
        self.root.geometry("1200x800")  # Increased window size
        self.root.minsize(1000, 700)  # Minimum size constraint
        self.data = None
        self.analysis_results = {}
        self.current_single_viz = None  # Track if showing single visualization

        # Configure styles
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))

        # Create paned window for resizable panels
        self.main_paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel for controls (30% width)
        self.control_frame = ttk.Frame(self.main_paned, width=360)
        self.main_paned.add(self.control_frame)  # Removed weight parameter

        # Header
        ttk.Label(self.control_frame, text="ELECTION DATA ANALYZER",
                 style='Header.TLabel').pack(pady=10)

        # Data loading section
        self.load_frame = ttk.LabelFrame(self.control_frame, text="Data Loading")
        self.load_frame.pack(fill=tk.X, pady=5, padx=5)
        ttk.Button(self.load_frame, text="Load CSV File",
                 command=lambda: self.load_data('csv')).pack(fill=tk.X, pady=2)
        ttk.Button(self.load_frame, text="Load JSON File",
                 command=lambda: self.load_data('json')).pack(fill=tk.X, pady=2)
        self.file_label = ttk.Label(self.load_frame, text="No file loaded")
        self.file_label.pack(fill=tk.X, pady=5)

        # Analysis section
        self.analysis_frame = ttk.LabelFrame(self.control_frame, text="Analysis")
        self.analysis_frame.pack(fill=tk.X, pady=5, padx=5)
        ttk.Button(self.analysis_frame, text="Voter Turnout by Region",
                 command=self.analyze_turnout).pack(fill=tk.X, pady=2)
        ttk.Button(self.analysis_frame, text="Party Performance",
                 command=self.analyze_party_performance).pack(fill=tk.X, pady=2)
        ttk.Button(self.analysis_frame, text="Candidate Performance",
                 command=self.analyze_candidate_performance).pack(fill=tk.X, pady=2)

        # Visualization controls section
        self.viz_control_frame = ttk.LabelFrame(self.control_frame, text="Visualization Controls")
        self.viz_control_frame.pack(fill=tk.X, pady=5, padx=5)
        ttk.Button(self.viz_control_frame, text="Generate All Visualizations",
                 command=self.generate_visualizations).pack(fill=tk.X, pady=2)
        ttk.Button(self.viz_control_frame, text="Maximize Turnout Chart",
                 command=lambda: self.show_single_viz('turnout')).pack(fill=tk.X, pady=2)
        ttk.Button(self.viz_control_frame, text="Maximize Party Chart",
                 command=lambda: self.show_single_viz('party')).pack(fill=tk.X, pady=2)
        ttk.Button(self.viz_control_frame, text="Maximize Candidates Chart",
                 command=lambda: self.show_single_viz('candidates')).pack(fill=tk.X, pady=2)
        ttk.Button(self.viz_control_frame, text="Return to Multi-View",
                 command=self.show_multi_viz).pack(fill=tk.X, pady=2)

        # Report section
        self.report_frame = ttk.LabelFrame(self.control_frame, text="Reporting")
        self.report_frame.pack(fill=tk.X, pady=5, padx=5)
        ttk.Button(self.report_frame, text="Generate Report",
                 command=self.generate_report).pack(fill=tk.X, pady=2)

        # Right panel for display (70% width)
        self.display_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.display_frame)  # Removed weight parameter

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.display_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Results tab
        self.results_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.results_tab, text="Analysis Results")
        self.results_text = tk.Text(self.results_tab, wrap=tk.WORD, state=tk.DISABLED)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Visualization tab
        self.viz_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.viz_tab, text="Visualizations")

        # Visualization container with scrollbar
        self.viz_container = ttk.Frame(self.viz_tab)
        self.viz_container.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Initialize visualization variables
        self.figure = None
        self.canvas = None
        self.toolbar = None

    def load_data(self, file_type):
        """Load election data from file"""
        file_path = filedialog.askopenfilename(
            filetypes=[(f"{file_type.upper()} files", f"*.{file_type}")])
        
        if not file_path:
            return
            
        try:
            if file_type == 'csv':
                self.data = pd.read_csv(file_path)
            elif file_type == 'json':
                with open(file_path, 'r') as f:
                    self.data = pd.DataFrame(json.load(f))
            
            # Validate data structure
            required_columns = ['region', 'candidate', 'party', 'votes']
            if not all(col in self.data.columns for col in required_columns):
                missing = [col for col in required_columns if col not in self.data.columns]
                raise ValueError(f"Missing required columns: {missing}")
            
            self.file_label.config(text=f"Loaded: {os.path.basename(file_path)}")
            self.status_var.set(f"Successfully loaded {file_type.upper()} file")
            self.update_results("Data loaded successfully!\n\n" + 
                              f"Records loaded: {len(self.data)}\n" +
                              f"Columns: {', '.join(self.data.columns)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
            self.status_var.set("Error loading file")
    
    def validate_data(self):
        """Check if data is loaded and valid"""
        if self.data is None:
            messagebox.showwarning("No Data", "Please load election data first")
            return False
        return True
    
    def analyze_turnout(self):
        """Analyze voter turnout by region"""
        if not self.validate_data():
            return
            
        try:
            turnout = self.data.groupby('region')['votes'].sum().sort_values(ascending=False)
            self.analysis_results['turnout_by_region'] = turnout
            
            result_text = "VOTER TURNOUT BY REGION:\n\n"
            result_text += turnout.to_string()
            
            self.update_results(result_text)
            self.status_var.set("Voter turnout analysis completed")
            
        except Exception as e:
            messagebox.showerror("Analysis Error", str(e))
            self.status_var.set("Error in turnout analysis")
    
    def analyze_party_performance(self):
        """Analyze performance by political party"""
        if not self.validate_data():
            return
            
        try:
            party_perf = self.data.groupby('party')['votes'].sum().sort_values(ascending=False)
            self.analysis_results['party_performance'] = party_perf
            
            result_text = "PARTY PERFORMANCE:\n\n"
            result_text += party_perf.to_string()
            
            self.update_results(result_text)
            self.status_var.set("Party performance analysis completed")
            
        except Exception as e:
            messagebox.showerror("Analysis Error", str(e))
            self.status_var.set("Error in party performance analysis")
    
    def analyze_candidate_performance(self):
        """Analyze performance by candidate"""
        if not self.validate_data():
            return
            
        try:
            candidate_perf = self.data.groupby(['candidate', 'party'])['votes'].sum().sort_values(ascending=False)
            self.analysis_results['candidate_performance'] = candidate_perf
            
            result_text = "TOP 10 CANDIDATES BY PERFORMANCE:\n\n"
            result_text += candidate_perf.head(10).to_string()
            
            self.update_results(result_text)
            self.status_var.set("Candidate performance analysis completed")
            
        except Exception as e:
            messagebox.showerror("Analysis Error", str(e))
            self.status_var.set("Error in candidate performance analysis")

    def clear_visualization(self):
        """Clear existing visualization"""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            plt.close(self.figure)
        if self.toolbar:
            self.toolbar.destroy()

    def generate_visualizations(self):
        """Generate all visualizations in multi-view mode"""
        if not self.analysis_results:
            messagebox.showwarning("No Results", "Please run analyses first")
            return

        try:
            self.clear_visualization()
            self.current_single_viz = None
            self.figure = plt.figure(figsize=(10, 8), dpi=100)  # Higher DPI for better quality

            # Turnout by region visualization
            if 'turnout_by_region' in self.analysis_results:
                ax1 = self.figure.add_subplot(2, 2, 1)
                self.analysis_results['turnout_by_region'].plot(kind='bar', color='skyblue', ax=ax1)
                ax1.set_title('Voter Turnout by Region', fontsize=10)
                ax1.set_ylabel('Total Votes', fontsize=9)
                ax1.tick_params(axis='x', rotation=45, labelsize=8)
                ax1.tick_params(axis='y', labelsize=8)

            # Party performance visualization
            if 'party_performance' in self.analysis_results:
                ax2 = self.figure.add_subplot(2, 2, 2)
                self.analysis_results['party_performance'].plot(kind='pie', autopct='%1.1f%%',
                    textprops={'fontsize': 8}, ax=ax2)
                ax2.set_title('Vote Share by Party', fontsize=10)
                ax2.set_ylabel('')

            # Candidate performance visualization
            if 'candidate_performance' in self.analysis_results:
                ax3 = self.figure.add_subplot(2, 1, 2)
                self.analysis_results['candidate_performance'].head(10).plot(
                    kind='barh', color='lightgreen', ax=ax3)
                ax3.set_title('Top 10 Performing Candidates', fontsize=10)
                ax3.set_xlabel('Total Votes', fontsize=9)
                ax3.tick_params(axis='both', labelsize=8)

            self.figure.tight_layout(pad=3.0)  # Add padding between subplots

            # Create canvas and toolbar
            self.canvas = FigureCanvasTkAgg(self.figure, master=self.viz_container)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.viz_container)
            self.toolbar.update()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # Switch to visualization tab
            self.notebook.select(self.viz_tab)

            # Save visualization with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"election_analysis_{timestamp}.png"
            self.figure.savefig(output_file, dpi=300, bbox_inches='tight')  # Higher quality save
            self.status_var.set(f"Visualizations generated and saved as {output_file}")

        except Exception as e:
            messagebox.showerror("Visualization Error", str(e))
            self.status_var.set("Error generating visualizations")

    def show_single_viz(self, viz_type):
        """Show a single maximized visualization"""
        if not self.analysis_results:
            messagebox.showwarning("No Results", "Please run analyses first")
            return

        try:
            self.clear_visualization()
            self.current_single_viz = viz_type
            self.figure = plt.figure(figsize=(10, 6), dpi=100)
            ax = self.figure.add_subplot(111)

            if viz_type == 'turnout' and 'turnout_by_region' in self.analysis_results:
                self.analysis_results['turnout_by_region'].plot(kind='bar', color='skyblue', ax=ax)
                ax.set_title('Voter Turnout by Region', fontsize=12)
                ax.set_ylabel('Total Votes', fontsize=11)
                ax.tick_params(axis='x', rotation=45, labelsize=10)
                ax.tick_params(axis='y', labelsize=10)
            elif viz_type == 'party' and 'party_performance' in self.analysis_results:
                self.analysis_results['party_performance'].plot(kind='pie', autopct='%1.1f%%',
                    textprops={'fontsize': 10}, ax=ax)
                ax.set_title('Vote Share by Party', fontsize=12)
                ax.set_ylabel('')
            elif viz_type == 'candidates' and 'candidate_performance' in self.analysis_results:
                self.analysis_results['candidate_performance'].head(10).plot(
                    kind='barh', color='lightgreen', ax=ax)
                ax.set_title('Top 10 Performing Candidates', fontsize=12)
                ax.set_xlabel('Total Votes', fontsize=11)
                ax.tick_params(axis='both', labelsize=10)

            self.figure.tight_layout()

            # Create canvas and toolbar
            self.canvas = FigureCanvasTkAgg(self.figure, master=self.viz_container)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.viz_container)
            self.toolbar.update()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # Switch to visualization tab
            self.notebook.select(self.viz_tab)
            self.status_var.set(f"Showing maximized {viz_type} visualization")

        except Exception as e:
            messagebox.showerror("Visualization Error", str(e))
            self.status_var.set(f"Error showing {viz_type} visualization")

    def show_multi_viz(self):
        """Return to multi-view visualization mode"""
        if self.current_single_viz is None:
            return
        self.generate_visualizations()

    def generate_report(self):
        """Generate a text report of the analysis"""
        if not self.analysis_results:
            messagebox.showwarning("No Results", "Please run analyses first")
            return
            
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")],
                title="Save Report As")
            
            if not file_path:
                return
                
            with open(file_path, 'w') as f:
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
                    f.write("CANDIDATE PERFORMANCE (TOP 10):\n")
                    f.write(self.analysis_results['candidate_performance'].head(10).to_string())
                    f.write("\n\n")
            
            self.status_var.set(f"Report saved to {file_path}")
            messagebox.showinfo("Report Generated", f"Report successfully saved to:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Report Error", str(e))
            self.status_var.set("Error generating report")
    
    def update_results(self, text):
        """Update the results display area"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, text)
        self.results_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = ElectionAnalyzerApp(root)
    root.mainloop()