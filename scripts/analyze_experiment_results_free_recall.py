#!/usr/bin/env python3
"""
Script to analyze and visualize Free Recall experiment results.
Creates plots specifically for free recall experiments.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import glob
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent

def load_free_recall_data():
    """Load all free recall experiment data."""
    project_root = get_project_root()
    combined_dir = project_root / "combined_data"
    
    all_data = []
    csv_files = glob.glob(str(combined_dir / "Free_recall_experiment_*.csv"))
    
    for file_path in csv_files:
        try:
            df = pd.read_csv(file_path)
            all_data.append(df)
            print(f"Loaded: {Path(file_path).name}")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()

def create_free_recall_comparison_plot(data, images_dir):
    """Create plot comparing different free recall conditions."""
    if data.empty:
        print("No Free Recall data found")
        return
    
    # Calculate mean performance by experiment
    performance_by_experiment = data.groupby('experiment_name')['proportion_correct'].agg(['mean', 'std']).reset_index()
    
    plt.figure(figsize=(12, 6))
    
    # Create bar plot
    bars = plt.bar(performance_by_experiment['experiment_name'], performance_by_experiment['mean'], 
                   color=['steelblue', 'coral', 'lightgreen', 'gold'], alpha=0.8, 
                   edgecolor='black', linewidth=1)
    
    # Add error bars
    plt.errorbar(performance_by_experiment['experiment_name'], performance_by_experiment['mean'], 
                yerr=performance_by_experiment['std'], fmt='none', color='black', capsize=5)
    
    # Add value labels
    for bar, mean in zip(bars, performance_by_experiment['mean']):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f'{mean:.3f}', ha='center', va='bottom', fontweight='bold')
    
    plt.xlabel('Condition', fontsize=12, fontweight='bold')
    plt.ylabel('Proportion Correct', fontsize=12, fontweight='bold')
    plt.title('Free Recall Effects', fontsize=14, fontweight='bold', pad=20)
    
    plt.ylim(0, max(performance_by_experiment['mean']) * 1.2)
    plt.grid(True, alpha=0.3, axis='y')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(images_dir / 'free_recall_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return performance_by_experiment

def create_free_recall_individual_plots(data, images_dir):
    """Create individual plots for each free recall experiment."""
    experiments = data['experiment_name'].unique()
    
    for exp_name in experiments:
        exp_data = data[data['experiment_name'] == exp_name]
        
        if exp_data.empty:
            continue
        
        # Create subfolder for this experiment
        exp_dir = images_dir / exp_name.lower()
        exp_dir.mkdir(exist_ok=True)
        
        plt.figure(figsize=(10, 6))
        
        # Create histogram of performance
        plt.hist(exp_data['proportion_correct'], bins=15, alpha=0.7, color='steelblue', edgecolor='black')
        
        # Add mean line
        mean_perf = exp_data['proportion_correct'].mean()
        plt.axvline(mean_perf, color='red', linestyle='--', linewidth=2, 
                   label=f'Mean: {mean_perf:.3f}')
        
        plt.xlabel('Proportion Correct', fontsize=12, fontweight='bold')
        plt.ylabel('Frequency', fontsize=12, fontweight='bold')
        plt.title(f'Free Recall - {exp_name} Performance Distribution', fontsize=14, fontweight='bold', pad=20)
        
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(exp_dir / f'{exp_name.lower()}_distribution.png', dpi=300, bbox_inches='tight')
        plt.show()

def create_free_recall_statistics_table(data):
    """Create detailed statistics table for free recall experiments."""
    stats = []
    
    for exp_name in data['experiment_name'].unique():
        exp_data = data[data['experiment_name'] == exp_name]
        
        if not exp_data.empty:
            mean_perf = exp_data['proportion_correct'].mean()
            std_perf = exp_data['proportion_correct'].std()
            n_trials = len(exp_data)
            
            stats.append({
                'Experiment': exp_name,
                'Mean Performance': f'{mean_perf:.3f}',
                'Std Performance': f'{std_perf:.3f}',
                'N Trials': n_trials
            })
    
    return pd.DataFrame(stats)

def main():
    """Main function to run free recall analyses."""
    # Create images directory
    project_root = get_project_root()
    images_dir = project_root / "images" / "free_recall_plots"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading Free Recall experiment data...")
    data = load_free_recall_data()
    
    if data.empty:
        print("No Free Recall data found. Please run the combine_experiment_data.py script first.")
        return
    
    print(f"Loaded {len(data)} Free Recall records")
    print(f"Experiments: {data['experiment_name'].unique()}")
    print("-" * 50)
    
    # Create plots
    print("\nCreating Free Recall comparison plot...")
    comparison_data = create_free_recall_comparison_plot(data, images_dir)
    
    print("\nCreating individual experiment plots...")
    create_free_recall_individual_plots(data, images_dir)
    
    # Create statistics table
    print("\nCreating statistics table...")
    stats_table = create_free_recall_statistics_table(data)
    print("\nFree Recall Statistics:")
    print("=" * 60)
    print(stats_table.to_string(index=False))
    
    # Save statistics to CSV
    stats_table.to_csv(images_dir / 'free_recall_statistics.csv', index=False)
    
    print(f"\nFree Recall analysis complete!")
    print(f"Plots saved to: {images_dir}")
    print(f"Statistics saved to: {images_dir / 'free_recall_statistics.csv'}")

if __name__ == "__main__":
    main()
