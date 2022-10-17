Invoke-Expression -Command C:\ProgramData\Miniconda3\shell\condabin\conda-hook.ps1

conda activate e2es-orchestrator

$ContextFolder = 'C:\orchestrator\context'
$SnakemakeFolder = 'C:\orchestrator\.snakemake'
$CacheFolder = 'C:\orchestrator\__pycache__'
if (Test-Path $ContextFolder) {
    Remove-Item $ContextFolder -Recurse -Force
}
if (Test-Path $SnakemakeFolder) {
    Remove-Item $SnakemakeFolder -Recurse -Force
}
if (Test-Path $CacheFolder) {
    Remove-Item $CacheFolder -Recurse -Force
}


cd C:\orchestrator; snakemake --cores 1 TARGET