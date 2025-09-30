#!/usr/bin/env python3
"""
Script to analyze and visualize Serial Recall experiment results.
Creates plots specifically for serial recall experiments.
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

def load_serial_recall_data():
    """Load all serial recall experiment data."""
    project_root = get_project_root()
    combined_dir = project_root / "combined_data"
    
    all_data = []
    csv_files = glob.glob(str(combined_dir / "Serial_recall_experiment_*.csv"))
    
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

def create_working_memory_capacity_plot(data, images_dir):
    """Create plot showing working memory capacity (list length vs performance)."""
    # Filter for Length experiment data
    length_data = data[data['experiment_name'] == 'Length'].copy()
    
    if length_data.empty:
        print("No Length experiment data found")
        return
    
    # Calculate mean performance by list length
    performance_by_length = length_data.groupby('list_length')['proportion_correct_in_position'].agg(['mean', 'std']).reset_index()
    
    plt.figure(figsize=(10, 6))
    
    # Create the line plot
    plt.plot(performance_by_length['list_length'], performance_by_length['mean'], 
             'o-', linewidth=2, markersize=8, color='steelblue', label='Mean Performance')
    
    # Add error bars
    plt.errorbar(performance_by_length['list_length'], performance_by_length['mean'], 
                yerr=performance_by_length['std'], fmt='none', color='steelblue', alpha=0.7)
    
    # Add grid
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Customize plot
    plt.xlabel('List Length', fontsize=12, fontweight='bold')
    plt.ylabel('Proportion Correct', fontsize=12, fontweight='bold')
    plt.title('Working Memory Capacity', fontsize=14, fontweight='bold', pad=20)
    
    # Set axis limits and ticks
    plt.xlim(performance_by_length['list_length'].min() - 0.5, performance_by_length['list_length'].max() + 0.5)
    plt.ylim(0, 1.1)
    plt.xticks(range(int(performance_by_length['list_length'].min()), int(performance_by_length['list_length'].max()) + 1))
    plt.yticks([0, 0.25, 0.5, 0.75, 1.0])
    
    # Add horizontal line at 0.5 for reference
    plt.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='50% Performance')
    
    plt.legend()
    plt.tight_layout()
    plt.savefig(images_dir / 'working_memory_capacity.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return performance_by_length

def create_serial_recall_comparison_plot(data, images_dir):
    """Create plot showing articulatory suppression effects."""
    # Get baseline (Tapping) and suppression data
    tapping_data = data[data['experiment_name'] == 'Tapping']
    suppression_data = data[data['experiment_name'] == 'Suppression']
    chunking_data = data[data['experiment_name'] == 'Chunking']
    
    # Calculate mean performance for each condition
    conditions = []
    means = []
    stds = []
    
    if not tapping_data.empty:
        tapping_mean = tapping_data['proportion_correct_in_position'].mean()
        tapping_std = tapping_data['proportion_correct_in_position'].std()
        conditions.append('Tapping')
        means.append(tapping_mean)
        stds.append(tapping_std)
    
    if not suppression_data.empty:
        suppression_mean = suppression_data['proportion_correct_in_position'].mean()
        suppression_std = suppression_data['proportion_correct_in_position'].std()
        conditions.append('Suppression')
        means.append(suppression_mean)
        stds.append(suppression_std)
    
    if not chunking_data.empty:
        chunking_mean = chunking_data['proportion_correct_in_position'].mean()
        chunking_std = chunking_data['proportion_correct_in_position'].std()
        conditions.append('Chunking')
        means.append(chunking_mean)
        stds.append(chunking_std)
    
    if not conditions:
        print("No articulatory suppression data found")
        return
    
    plt.figure(figsize=(10, 6))
    
    # Create bar plot with colors for each condition
    colors = ['steelblue', 'coral', 'lightgreen']
    bars = plt.bar(conditions, means, color=colors[:len(conditions)], 
                   alpha=0.8, edgecolor='black', linewidth=1)
    
    # Add error bars
    plt.errorbar(conditions, means, yerr=stds, fmt='none', color='black', capsize=5)
    
    # Add value labels on bars
    for i, (bar, mean) in enumerate(zip(bars, means)):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f'{mean:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # Customize plot
    plt.xlabel('Condition', fontsize=12, fontweight='bold')
    plt.ylabel('Proportion Correct', fontsize=12, fontweight='bold')
    plt.title('Serial Recall Effects', fontsize=14, fontweight='bold', pad=20)
    
    plt.ylim(0, max(means) * 1.2)
    plt.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(images_dir / 'serial_recall_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return pd.DataFrame({'Condition': conditions, 'Mean': means, 'Std': stds})

def create_serial_recall_individual_plots(data, images_dir):
    """Create individual plots for each serial recall experiment."""
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
        plt.hist(exp_data['proportion_correct_in_position'], bins=15, alpha=0.7, color='steelblue', edgecolor='black')
        
        # Add mean line
        mean_perf = exp_data['proportion_correct_in_position'].mean()
        plt.axvline(mean_perf, color='red', linestyle='--', linewidth=2, 
                   label=f'Mean: {mean_perf:.3f}')
        
        plt.xlabel('Proportion Correct', fontsize=12, fontweight='bold')
        plt.ylabel('Frequency', fontsize=12, fontweight='bold')
        plt.title(f'Serial Recall - {exp_name} Performance Distribution', fontsize=14, fontweight='bold', pad=20)
        
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(exp_dir / f'{exp_name.lower()}_distribution.png', dpi=300, bbox_inches='tight')
        plt.show()

def create_serial_recall_statistics_table(data):
    """Create detailed statistics table for serial recall experiments."""
    stats = []
    
    for exp_name in data['experiment_name'].unique():
        exp_data = data[data['experiment_name'] == exp_name]
        
        if not exp_data.empty:
            mean_perf = exp_data['proportion_correct_in_position'].mean()
            std_perf = exp_data['proportion_correct_in_position'].std()
            n_trials = len(exp_data)
            
            stats.append({
                'Experiment': exp_name,
                'Mean Performance': f'{mean_perf:.3f}',
                'Std Performance': f'{std_perf:.3f}',
                'N Trials': n_trials
            })
    
    return pd.DataFrame(stats)

def main():
    """Main function to run serial recall analyses."""
    # Create images directory
    project_root = get_project_root()
    images_dir = project_root / "images" / "serial_recall_plots"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading Serial Recall experiment data...")
    data = load_serial_recall_data()
    
    if data.empty:
        print("No Serial Recall data found. Please run the combine_experiment_data.py script first.")
        return
    
    print(f"Loaded {len(data)} Serial Recall records")
    print(f"Experiments: {data['experiment_name'].unique()}")
    print("-" * 50)
    
    # Create plots
    print("\nCreating Working Memory Capacity plot...")
    wm_data = create_working_memory_capacity_plot(data, images_dir)
    
    print("\nCreating Articulatory Suppression plot...")
    as_data = create_serial_recall_comparison_plot(data, images_dir)
    
    print("\nCreating individual experiment plots...")
    create_serial_recall_individual_plots(data, images_dir)
    
    # Create statistics table
    print("\nCreating statistics table...")
    stats_table = create_serial_recall_statistics_table(data)
    print("\nSerial Recall Statistics:")
    print("=" * 60)
    print(stats_table.to_string(index=False))
    
    # Save statistics to CSV
    stats_table.to_csv(images_dir / 'serial_recall_statistics.csv', index=False)
    
    print(f"\nSerial Recall analysis complete!")
    print(f"Plots saved to: {images_dir}")
    print(f"Statistics saved to: {images_dir / 'serial_recall_statistics.csv'}")

if __name__ == "__main__":
    main()
