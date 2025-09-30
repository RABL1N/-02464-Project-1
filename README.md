# 02464 Project 1:

### Free Recall Experiments

Located in `Free recall experiment/` directory:

- **Baseline/**: Standard free recall experiment
- **Pause/**: Free recall with pause after sequence
- **Speed/**: Free recall with faster presentation rate
- **Suppression/**: Free recall with articulatory suppression

### Serial Recall Experiments

Located in `Serial recall experiment/` directory:

- **Baseline/**: Standard serial recall experiment (baseline condition)
- **Chunking/**: Serial recall with chunked presentation
- **Length/**: Serial recall with varying list lengths
- **Suppression/**: Serial recall with articulatory suppression
- **Tapping/**: Serial recall with finger tapping

## Experiment Recording Guidelines

### Participant Information

- **Participant ID Format**: Use consistent format (e.g., Poul, Selma, Rasmus...)

#### Minimum Requirements

- **Exactly 20 trials per participant** per experiment condition
- **Multiple participants** - all group members must perform every experiment. Every experiment is run using a different python file, found in the corresponding subfolder.

### File Organization

#### Data Storage

- Store CSV files in the appropriate experiment directory
- Use consistent naming conventions
- Keep backup copies of all data files, but **don't commit them to main branch**
- Document any experimental modifications or issues

#### Directory Structure

```
Project/
├── Free recall experiment/
│   ├── Baseline/
│   │   ├── free_recall_experiment.py
│   │   └── [CSV files]
│   ├── Pause/
│   ├── Speed/
│   └── Suppression/
├── Serial recall experiment/
│   ├── Baseline/
│   │   ├── serial_recall_experiment.py
│   │   └── [CSV files]
│   ├── Chunking/
│   ├── Length/
│   ├── Suppression/
│   └── Tapping/
└── README.md
```

### CSV File Naming Conventions

#### Free Recall Experiments

Format: `free_recall_[ExperimentType]_[ParticipantID]_[Date].csv`

Examples:

- `free_recall_baseline_Rasmus_18_09.csv`
- `free_recall_pause_Poul_21_09.csv`
- `free_recall_speed_Selma_18_09.csv`
- `free_recall_suppression_Poul_21_09.csv`

#### Serial Recall Experiments

Format: `serial_recall_[ExperimentType]_[ParticipantID]_[Date].csv`

Examples:

- `serial_recall_baseline_Rasmus_18_09.csv`
- `serial_recall_chunking_Rasmus_18_09.csv`
- `serial_recall_length_Poul_21_09.csv`
- `serial_recall_suppression_Selma_18_09.csv`
- `serial_recall_tapping_Poul_21_09.csv`

### CSV Data Fields

#### Free Recall CSV Fields

- `timestamp`: Date and time of trial
- `participant`: Participant identifier
- `trial_index`: Trial number within session
- `condition`: Experimental condition (e.g., "silent", "suppression", "tapping")
- `similarity`: Phonological similarity condition
- `chunked`: Whether list was chunked (1/0)
- `list_items`: The sequence of letters presented
- `response`: Participant's recall response
- `n_correct`: Number of correctly recalled items
- `proportion_correct`: Proportion of items correctly recalled
- `phonological_confusions`: Count of phonological confusion errors

#### Serial Recall CSV Fields

- `timestamp`: Date and time of trial
- `participant`: Participant identifier
- `trial_index`: Trial number within session
- `rate`: Presentation rate ("slow" or "fast")
- `post_phase`: Post-list phase type ("immediate", "pause", "wm")
- `chunking`: Whether chunking was used (True/False)
- `list_length`: Number of items in the sequence
- `list_items`: The sequence of letters presented
- `response`: Participant's recall response
- `proportion_correct_in_position`: Proportion correct in correct positions
- `per_position_binary`: Binary string showing correct/incorrect for each position
