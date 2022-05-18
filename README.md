# e2es-orchestrator

## Prerequisites

- Every processor prerequisites must be fulfilled prior to execution
- Every processor specific configuration must be done prior to exectuion
- Other requirements are scpecified in the ICD 

## Installation

- Install [miniconda](https://docs.conda.io/en/latest/miniconda.html)
- Open anaconda powershell prompt ( find it using the Windows search bar )
- `conda update conda`
- `cd /path/to/e2es-orchestrator`
- `conda env create -f environment.yml`
- `cp configurations.sample.yaml configurations.yaml`

## Configuration

- `start`: identify the workflow starting processor; possible values are listed in 'processors' fields (keys)
- `end`: identify the workflow ending processor; possible values are listed in 'processors' fields (keys); this ending processor cannot sit before the one in 'start' field  (following the order of the list in 'processors' field)
- `logLevel`: only for debugging purposes
- `dataRoot`: absolute path to data/storage folder ( e.g. PDGS_NAS_folder ) folder; internal folder structure must mimic ICD structure
- `backupRoot`: absolute path to a backup folder; this is used for storing runs backups and PAM related files. In this folder must exist a folder named "PAM" in order to work properly
- `backupFile`: relative path to a backup file generated in a previous run; if present, the orchestrator will load data from this backup before starting the workflow
- `backupPrefix`: textual fragment which will be prepended to backup file names
- `dryMode`: only for debugging purposes; will be removed in future releases
- `workingDirectory`: absolute path to processor delivery folder; internal folder structure must mimic ICD structure 
- `executable` or `script`: relative path to processor executable or python script

### Example
```yaml
start: L1_A 
end: L2_FB
logLevel: DEBUG
dataRoot: 'C:\Users\HydroGNSS\Desktop\PDGS_NAS_folder' 
backupRoot: 'C:\Users\HydroGNSS\Desktop\DataRelease_backups' 
backupFile: 
backupPrefix: 'run'
dryMode: false
processors:
  L1_A: 
    workingDirectory: 'C:\Users\HydroGNSS\Desktop\L1APP\' 
    executable: '.\bin\HSAVERS.exe' 
  L1_B:
    workingDirectory: 'C:\Users\HydroGNSS\Desktop\L1BPP\'
    script: '.\scripts\Run_L1b_Processor_with_dates.py'
  L2_FB: 
    workingDirectory: 'C:\Users\HydroGNSS\Desktop\L2PPFB\'
    executable: '.\bin\L2PP_FB.exe'
  L2_SM:
    workingDirectory: 'C:\Users\HydroGNSS\Desktop\L2PPSSM\'
    executable: '.\bin\SML2PP_start.exe'
    resolution: '25'
    signal: 'L1'
    polarization: 'L'
  L2_FT:
    workingDirectory: 'C:\Users\HydroGNSS\Desktop\L2PPFT\'
    executable: '.\bin\L2PPFT.exe'
  L2_SI:
    workingDirectory: 'C:\Users\HydroGNSS\Desktop\L2PPSI\'
    script: '.\scripts\Run_PSR.py'
```

## Usage 
- Open anaconda powershell prompt ( find it using the Windows search bar )
- `cd /path/to/e2es-orchestrator`
- `conda activate e2es-orchestrator`
- `snakemake --cores 1 TARGET`


