#!/usr/bin/env python3
"""
Script to combine all experiment CSV data into unified datasets.
This script processes both Free Recall and Serial Recall experiments,
combining data from all participants into single CSV files for each experiment type.
"""

import pandas as pd
import os
import glob
from pathlib import Path

def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent

def find_csv_files(experiment_type, experiment_name):
    """
    Find all CSV files for a specific experiment type and name.
    
    Args:
        experiment_type (str): 'Free recall experiment' or 'Serial recall experiment'
        experiment_name (str): Name of the specific experiment (e.g., 'Baseline', 'Chunking')
    
    Returns:
        list: List of CSV file paths
    """
    project_root = get_project_root()
    pattern = f"experiments/{experiment_type}/{experiment_name}/*.csv"
    return glob.glob(str(project_root / pattern))

def process_free_recall_data(csv_files, experiment_name):
    """
    Process and combine free recall experiment data.
    
    Args:
        csv_files (list): List of CSV file paths
        experiment_name (str): Name of the experiment
    
    Returns:
        pd.DataFrame: Combined dataframe
    """
    combined_data = []
    
    for file_path in csv_files:
        try:
            df = pd.read_csv(file_path)
            
            # Remove unwanted columns
            columns_to_remove = ['participant', 'trial_index', 'timestamp', 'condition', 'similarity', 'rate', 'post_phase', 'chunking', 'chunked']
            df = df.drop(columns=[col for col in columns_to_remove if col in df.columns])
            
            # Add experiment metadata
            df['experiment_type'] = 'Free Recall'
            df['experiment_name'] = experiment_name
            
            combined_data.append(df)
            print(f"Processed: {file_path}")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    if combined_data:
        return pd.concat(combined_data, ignore_index=True)
    else:
        return pd.DataFrame()

def process_serial_recall_data(csv_files, experiment_name):
    """
    Process and combine serial recall experiment data.
    
    Args:
        csv_files (list): List of CSV file paths
        experiment_name (str): Name of the experiment
    
    Returns:
        pd.DataFrame: Combined dataframe
    """
    combined_data = []
    
    for file_path in csv_files:
        try:
            df = pd.read_csv(file_path)
            
            # Remove unwanted columns
            columns_to_remove = ['participant', 'trial_index', 'timestamp', 'condition', 'similarity', 'rate', 'post_phase', 'chunking', 'chunked']
            df = df.drop(columns=[col for col in columns_to_remove if col in df.columns])
            
            # Add experiment metadata
            df['experiment_type'] = 'Serial Recall'
            df['experiment_name'] = experiment_name
            
            combined_data.append(df)
            print(f"Processed: {file_path}")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    if combined_data:
        return pd.concat(combined_data, ignore_index=True)
    else:
        return pd.DataFrame()

def main():
    """Main function to combine all experiment data."""
    project_root = get_project_root()
    output_dir = project_root / "combined_data"
    output_dir.mkdir(exist_ok=True)
    
    print("Starting data combination process...")
    print(f"Project root: {project_root}")
    print(f"Output directory: {output_dir}")
    print("-" * 50)
    
    # Define experiment configurations
    experiments = {
        'Free recall experiment': ['Baseline', 'Pause', 'Speed', 'Suppression'],
        'Serial recall experiment': ['Chunking', 'Length', 'Suppression', 'Tapping']
    }
    
    # Process each experiment type
    for experiment_type, experiment_names in experiments.items():
        print(f"\nProcessing {experiment_type}...")
        print("-" * 30)
        
        for experiment_name in experiment_names:
            print(f"\nProcessing {experiment_name}...")
            
            # Find CSV files for this experiment
            csv_files = find_csv_files(experiment_type, experiment_name)
            
            if not csv_files:
                print(f"No CSV files found for {experiment_type}/{experiment_name}")
                continue
            
            print(f"Found {len(csv_files)} CSV files:")
            for file in csv_files:
                print(f"  - {os.path.basename(file)}")
            
            # Process the data based on experiment type
            if 'Free recall' in experiment_type:
                combined_df = process_free_recall_data(csv_files, experiment_name)
            else:
                combined_df = process_serial_recall_data(csv_files, experiment_name)
            
            if not combined_df.empty:
                # Save individual experiment data
                output_file = output_dir / f"{experiment_type.replace(' ', '_')}_{experiment_name}_combined.csv"
                combined_df.to_csv(output_file, index=False)
                print(f"Saved: {output_file}")
                print(f"Records: {len(combined_df)}")
            else:
                print(f"No data to save for {experiment_name}")
    
    print(f"\nData combination complete!")
    print(f"All files saved to: {output_dir}")

if __name__ == "__main__":
    main()
