Invoke-Expression -Command C:\ProgramData\Miniconda3\shell\condabin\conda-hook.ps1

$PSScriptRoot = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

$ContextFolder = $PSScriptRoot + '\context'
$SnakemakeFolder = $PSScriptRoot + '\.snakemake'
$CacheFolder = $PSScriptRoot + '\__pycache__'
if (Test-Path $ContextFolder) {
    Remove-Item $ContextFolder -Recurse -Force
}
if (Test-Path $SnakemakeFolder) {
    Remove-Item $SnakemakeFolder -Recurse -Force
}
if (Test-Path $CacheFolder) {
    Remove-Item $CacheFolder -Recurse -Force
}

conda activate e2es-orchestrator
cd $PSScriptRoot; snakemake --cores 1 RUN