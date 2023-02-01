# iexpress.exe is love is life. https://www.youtube.com/watch?v=_WvIpaYcjaU
# Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted
# To run from cmd.exe powershell -file orchestrator.ps1

# TODO: support high DPI screens.
# TODO: use Windows Forms Layouts
# TODO: we could log the variuous steps of the processor with colors using
#       Write-Host.

Set-StrictMode -Version 3.0
# $ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

[Windows.Forms.Application]::EnableVisualStyles()

enum ExplorerKind {
    File
    Dir
}

enum Processor {
    L1A
    L1B
    L2FB
    L2FT
    L2SI
    L2SM
}

# TODO: put a try catch here.
$Config = Get-Content "config.json" | Out-String | ConvertFrom-Json

################################################################################
# Orchestrator                                                                 #
################################################################################

function Do-Orchestration {
    param (
        # Which processors to run.
        [parameter(Mandatory=$true)]  [Processor]$Start,
        [parameter(Mandatory=$true)]  [Processor]$End,
        [parameter(Mandatory=$true)]  [bool]$usePAM,
        [parameter(Mandatory=$false)] [string]$ArchivedBackup,
        # I/O directories.
        [parameter(Mandatory=$true)]  [string]$BackupDir,
        [parameter(Mandatory=$true)]  [string]$DataDir,
        # HSAVERS
        [parameter(Mandatory=$true)]  [string]$L1_Awd,
        [parameter(Mandatory=$true)]  [string]$L1_Aexe,
        # ???
        [parameter(Mandatory=$true)]  [string]$L1_Bwd,
        [parameter(Mandatory=$true)]  [string]$L1_Bexe,
        # merge module
        [parameter(Mandatory=$true)]  [string]$L1_B_MMwd,
        [parameter(Mandatory=$true)]  [string]$L1_B_MMexe,
        # forest biomass
        [parameter(Mandatory=$true)]  [string]$L2_FBwd,
        [parameter(Mandatory=$true)]  [string]$L2_FBexe,
        # freeze/thaw state
        [parameter(Mandatory=$true)]  [string]$L2_FTwd,
        [parameter(Mandatory=$true)]  [string]$L2_FTexe,
        # surface inundation
        [parameter(Mandatory=$true)]  [string]$L2_SIwd,
        [parameter(Mandatory=$true)]  [string]$L2_SIexe,
        # soil moisture
        [parameter(Mandatory=$true)]  [string]$L2_SMwd,
        [parameter(Mandatory=$true)]  [string]$L2_SMexe,
        # performance assesment module
        [parameter(Mandatory=$true)]  [string]$PAMwd,
        [parameter(Mandatory=$true)]  [string]$PAMexe

    )
    # This function is "vulnerable" to "time-of-check to time-of-use" i.e. it
    # expects to be the only one operating on the various files.

    if ($Start -gt $End) {
        Write-Error "the start processor ${Start} can't run before ${End}"
        return
    }
    if ($End -eq [Processor]::L1A -and $usePAM) {
        Write-Error "You cannot run just L1_A and use the PAM"
        return
    }
    if ($Start -eq [Processor]::L1A -and $ArchivedBackup) {
        Write-Error "You cannot load a backup and start from L1_A"
        return
    }
    # TODO: test that all paths are valid
    # TODO: check all invariants

    [string]$DataReleaseDir = Join-Path -Path $DataDir -ChildPath "DataRelease"

    # This is used later to create the backup name and to give input to the PAM
    # and it is set either when loading a backup or when running HSAVERS.
    [string]$ExperimentName = $null

    function Run-Processor {
        param (
            [string]$FilePath,
            [string[]]$ArgumentList, # This is the only optional argument.
            [string]$WorkingDirectory
        )

        Set-Location -Path $WorkingDirectory
        if ($FilePath -imatch ".exe$") {
            Invoke-Expression -Command "${FilePath} ${ArgumentList}"
        } elseif ($FilePath -imatch ".py$") {
            Invoke-Expression -Command "py ${FilePath} ${ArgumentList}"
        } else {
            Write-Error "Only python and exe files are supported, ${FilePath} is not supported"
            return
        }

        # NOTE: Invoke-Expression should throw an exception when the program
        # fails so this could be useless.
        if ($LASTEXITCODE -ne 0) {
            Write-Error "${FilePath} exited with a non zero exit code"
            return
        }
    }

    function Do-BackupAndPAM {
        # The backup is created has either the name of the HSAVERS run or the
        # name of the previous one always with a new timestamp.
        # The zeros at the end are just to reach the same lenght of 10 that is
        # necesary for PAM.
        [string]$Timestamp = "$(Get-Date -Format "fffffff")000"
        [string]$BackupName = "${ExperimentName}_${Timestamp}.zip"
        Write-Output "Doing the backup."
        Compress-Archive -Path $(Join-Path -Path $DataReleaseDir -ChildPath "*") `
            -DestinationPath $(Join-Path -Path $BackupDir -ChildPath $BackupName)

        if ($usePAM) {
            # TODO: check that the run ends with an L2 processor or L1B is fine too?
            Write-Output "Running PAM."
            Run-Processor -FilePath $PAMexe -ArgumentList $End.ToString(), `
                (Join-Path -Path $DataDir -ChildPath "Auxiliary_Data"), `
                $BackupDir, ($BackupName -replace "\.zip$") `
                -WorkingDirectory $PAMwd
        }
    }

    Write-Output "Cleaning up from previous execution."
    if (Test-Path $DataReleaseDir) {
        Remove-Item -Path $DataReleaseDir -Recurse
    }
    New-Item -ItemType "directory" -Path `
        $(Join-Path -Path $DataReleaseDir -ChildPath "L1A_L1B"), `
        $(Join-Path -Path $DataReleaseDir -ChildPath "L2OP-FB"), `
        $(Join-Path -Path $DataReleaseDir -ChildPath "L2OP-FT"), `
        $(Join-Path -Path $DataReleaseDir -ChildPath "L2OP-SI"), `
        $(Join-Path -Path $DataReleaseDir -ChildPath "L2OP-SM"), `
        $(Join-Path -Path $DataReleaseDir -ChildPath "L1A-SW-RX"), `
        $(Join-Path -Path $DataReleaseDir -ChildPath "L2-FDI") | Out-Null

    if ($ArchivedBackup) {
        # TODO: verify the name of the backup file
        [string]$ExperimentName = (
            # We remove the timestamp and the extension.
            [string[]]($ArchivedBackup -replace "_..........\.zip$" -split "\\")
        )[-1]
        Write-Output "Loading the selected backup."
        Expand-Archive -Path $ArchivedBackup -DestinationPath $DataReleaseDir
    }

    # We start the varius processes from this point.

    if ($Start -eq [Processor]::L1A) {
        Write-Output "Running L1_A."
        Run-Processor -FilePath $L1_Aexe -WorkingDirectory $L1_Awd `
            | Out-String -Stream # To avoid the pesky cls
        # TODO: Verify "..\conf\AbsoluteFilePath.txt" content
        [string]$L1_Aout = Get-Content -Path "..\conf\AbsoluteFilePath.txt"
        Copy-Item -Recurse -Force `
            -Path $(Join-Path -Path $L1_Aout -ChildPath "DataRelease\L1A_L1B") `
            -Destination $DataReleaseDir
        [string]$L1FileForPAM = Join-Path -Path $L1_Aout -ChildPath "*.mat"
        $ExperimentName = ($L1_Aout -split "\\" | Where-Object { $_ } )[-1]
        [string]$NameForPAM = "${ExperimentName}.mat"
        Copy-Item -Path $L1FileForPAM `
            -Destination $(Join-Path -Path $BackupDir -ChildPath "PAM\${NameForPAM}")
        Copy-Item -Path $L1FileForPAM -Destination $DataReleaseDir
        if ($End -eq [Processor]::L1A) {
            Do-BackupAndPAM
            return
        }
    }

    Write-Output "Detecting dates of the simulation."
    [string]$L1AL1BDir = Join-Path -Path $DataReleaseDir -ChildPath "L1A_L1B"
    [string[]]$YearMonthList = Get-ChildItem $L1AL1BDir `
        | Select-Object -Expand "Name" | Sort-Object
    [string]$StartYearMonth = $YearMonthList[0]
    [string]$EndYearMonth = $YearMonthList[-1]
    [string]$StartDay = ([string[]](
        Get-ChildItem $(Join-Path -Path $L1AL1BDir -ChildPath $StartYearMonth) `
        | Select-Object -Expand "Name" | Sort-Object))[0]
    [string]$EndDay = ([string[]](
        Get-ChildItem $(Join-Path -Path $L1AL1BDir -ChildPath $EndYearMonth) `
        | Select-Object -Expand "Name" | Sort-Object))[-1]
    [string]$StartDate = "${StartYearMonth}-${StartDay}"
    [string]$EndDate = "${EndYearMonth}-${EndDay}"

    # Removing QGIS from the path (or put it in the last position) seems to not be
    # necessary anymore.
    if ($Start -eq [Processor]::L1A -or $Start -eq [Processor]::L1B) {
        Write-Output "Running L1_B."
        Run-Processor -FilePath $L1_Bexe -ArgumentList $StartDate, $EndDate `
            -WorkingDirectory $L1_Bwd
        if ($LASTEXITCODE -ne 0) {
            Write-Error "L1_B exited with a non zero exit code"
            return
        }
        Write-Output "Running L1_B_MM."
        Run-Processor -FilePath $L1_B_MMexe -ArgumentList $StartDate, $EndDate `
            -WorkingDirectory $L1_B_MMwd
        if ($End -eq [Processor]::L1B) {
            Do-BackupAndPAM
            return
        }
    }

    switch ($End) {
        L2FT {
            # TODO: check this.
            Write-Output "Running L2_FT."
            Run-Processor -FilePath $L2_FTexe -ArgumentList $StartDate, $EndDate `
                -WorkingDirectory $L2_FTwd
            Do-BackupAndPAM
            return
        }
        L2FB {
            Write-Output "Running L2_FB."
            Run-Processor $L2_FBexe -ArgumentList $StartDate, $EndDate, $DataDir, "yes" `
                -WorkingDirectory $L2_FBwd
            Do-BackupAndPAM
            return
        }
        L2SM {
            # TODO: implements this.
            # argsTemplate = '-input {dataDir} {startDate} {endDate} 1 25 L1 L'
            Do-BackupAndPAM
            return
        }
        # Questo deve usare L1_B diviso in due parti, ma L1 cosa deve fare?
        L2SI {
            # TODO: implements this.
            # the special one
            # argsTemplate = '-P {DataRelease_folder} -M {modelfolder}'
            Do-BackupAndPAM
            return
        }
    }

    Write-Error "This should never happen"
}

################################################################################
# Common definitions for forms                                                 #
################################################################################

$DirectoryBrowser = New-Object System.Windows.Forms.FolderBrowserDialog `
    -Property @{
        RootFolder = [System.Environment+SpecialFolder]::MyComputer
        ShowNewFolderButton = $false
    }
$ExeBrowser = New-Object System.Windows.Forms.OpenFileDialog `
    -Property @{
        InitialDirectory = $Env:HOMEDRIVE
        Filter = "Portable Executable |*.exe|Python |*.py"
    }
$ZipBrowser = New-Object System.Windows.Forms.OpenFileDialog `
    -Property @{
        InitialDirectory = $Env:HOMEDRIVE
        Filter = "Zip Archive |*.zip"
    }

$DefaultFont = New-Object System.Drawing.Font('Ariel', 10, [System.Drawing.FontStyle]::Regular)

function Make-Label {
    param (
        [parameter(Mandatory=$true)]
        [string]$Text,
        [parameter(Mandatory=$true)]
        [System.Drawing.Point]$Location
    )

    $Label = New-Object System.Windows.Forms.Label
    $Label.Text = $Text
    $Label.AutoSize = $true
    $Label.Font = $DefaultFont
    $Label.Location = $Location

    return $Label
}

function Make-TextBox {
    param (
        [parameter(Mandatory=$true)]
        [System.Drawing.Point]$Location
    )

    $TextBox = New-Object System.Windows.Forms.TextBox
    $TextBox.Width = 250
    $TextBox.Font = $DefaultFont
    $TextBox.Location = $Location
    $TextBox.ReadOnly = $true

    return $TextBox
}

function Make-Button {
    param (
        [parameter(Mandatory=$true)] [string]$Text,
        [parameter(Mandatory=$true)] [System.Drawing.Point]$Location
    )

    $Button = New-Object System.Windows.Forms.Button
    $Button.Text = $Text
    $Button.Font = $DefaultFont
    $Button.Location = $Location
    $Button.AutoSize = $true

    return $Button
}

function Make-ExeBrowseButton {
    param (
        [parameter(Mandatory=$true)]
        [System.Drawing.Point]$Location,
        [parameter(Mandatory=$true)]
        [ExplorerKind]$Kind,
        [parameter(Mandatory=$true)]
        [System.Windows.Forms.TextBox]$TextBox
    )

    $Button = Make-Button -Text "Browse" -Location $Location

    switch ($Kind) {
        File {
            $ExeBrowser = $script:ExeBrowser
            $ScriptBlock = {
                $Result = $ExeBrowser.ShowDialog()
                if ($Result -eq [System.Windows.Forms.DialogResult]::Cancel) {
                    return
                }
                $TextBox.Text = ""
                $TextBox.AppendText($ExeBrowser.FileName)
            }.GetNewClosure()
        }
        Dir {
            $DirectoryBrowser = $script:DirectoryBrowser
            $ScriptBlock = {
                $Result = $DirectoryBrowser.ShowDialog()
                if ($Result -eq [System.Windows.Forms.DialogResult]::Cancel) {
                    return
                }
                $TextBox.Text = ""
                $TextBox.AppendText($DirectoryBrowser.SelectedPath)
            }.GetNewClosure()
        }
    }

    $Button.Add_Click($ScriptBlock)

    return $Button
}

################################################################################
# Settings Form                                                                #
################################################################################

$DataDirLabel      = Make-Label -Text "Data Directory"     -Location (New-object System.Drawing.Point(20, 30))
$BackupDirLabel    = Make-Label -Text "Backup Directory"   -Location (New-object System.Drawing.Point(20, 60))
$L1AExeLabel       = Make-Label -Text "L1A Executable"     -Location (New-object System.Drawing.Point(20, 90))
$L1AWorkDirLabel   = Make-Label -Text "L1A Working Dir."   -Location (New-object System.Drawing.Point(20, 120))
$L1BExeLabel       = Make-Label -Text "L1B Executable"     -Location (New-object System.Drawing.Point(20, 150))
$L1BWorkDirLabel   = Make-Label -Text "L1B Working Dir."   -Location (New-object System.Drawing.Point(20, 180))
$L1BMMExeLabel     = Make-Label -Text "L1BMM Executable"   -Location (New-object System.Drawing.Point(20, 210))
$L1BMMWorkDirLabel = Make-Label -Text "L1BMM Working Dir." -Location (New-object System.Drawing.Point(20, 240))
$L2FBExeLabel      = Make-Label -Text "L2FB Executable"    -Location (New-object System.Drawing.Point(20, 270))
$L2FBWorkDirLabel  = Make-Label -Text "L2FB Working Dir."  -Location (New-object System.Drawing.Point(20, 300))
$L2FTExeLabel      = Make-Label -Text "L2FT Executable"    -Location (New-object System.Drawing.Point(20, 330))
$L2FTWorkDirLabel  = Make-Label -Text "L2FT Working Dir."  -Location (New-object System.Drawing.Point(20, 360))
$L2SIExeLabel      = Make-Label -Text "L2SI Executable"    -Location (New-object System.Drawing.Point(20, 390))
$L2SIWorkDirLabel  = Make-Label -Text "L2SI Working Dir."  -Location (New-object System.Drawing.Point(20, 420))
$L2SMExeLabel      = Make-Label -Text "L2SM Executable"    -Location (New-object System.Drawing.Point(20, 450))
$L2SMWorkDirLabel  = Make-Label -Text "L2SM Working Dir."  -Location (New-object System.Drawing.Point(20, 480))
$PAMExeLabel       = Make-Label -Text "PAM Executable"     -Location (New-object System.Drawing.Point(20, 510))
$PAMWorkDirLabel   = Make-Label -Text "PAM Working Dir."   -Location (New-object System.Drawing.Point(20, 540))

$DataDirTextBox      = Make-TextBox -Location (New-object System.Drawing.Point(160, 30))
$DataDirTextBox.AppendText($Config.DataDir)
$BackupDirTextBox    = Make-TextBox -Location (New-object System.Drawing.Point(160, 60))
$BackupDirTextBox.AppendText($Config.BackupDir)
$L1AExeTextBox       = Make-TextBox -Location (New-object System.Drawing.Point(160, 90))
$L1AExeTextBox.AppendText($Config.L1AExe)
$L1AWorkDirTextBox   = Make-TextBox -Location (New-object System.Drawing.Point(160, 120))
$L1AWorkDirTextBox.AppendText($Config.L1AWorkDir)
$L1BExeTextBox       = Make-TextBox -Location (New-object System.Drawing.Point(160, 150))
$L1BExeTextBox.AppendText($Config.L1BExe)
$L1BWorkDirTextBox   = Make-TextBox -Location (New-object System.Drawing.Point(160, 180))
$L1BWorkDirTextBox.AppendText($Config.L1BWorkDir)
$L1BMMExeTextBox     = Make-TextBox -Location (New-object System.Drawing.Point(160, 210))
$L1BMMExeTextBox.AppendText($Config.L1BMMExe)
$L1BMMWorkDirTextBox = Make-TextBox -Location (New-object System.Drawing.Point(160, 240))
$L1BMMWorkDirTextBox.AppendText($Config.L1BMMWorkDir)
$L2FBExeTextBox      = Make-TextBox -Location (New-object System.Drawing.Point(160, 270))
$L2FBExeTextBox.AppendText($Config.L2FBExe)
$L2FBWorkDirTextBox  = Make-TextBox -Location (New-object System.Drawing.Point(160, 300))
$L2FBWorkDirTextBox.AppendText($Config.L2FBWorkDir)
$L2FTExeTextBox      = Make-TextBox -Location (New-object System.Drawing.Point(160, 330))
$L2FTExeTextBox.AppendText($Config.L2FTExe)
$L2FTWorkDirTextBox  = Make-TextBox -Location (New-object System.Drawing.Point(160, 360))
$L2FTWorkDirTextBox.AppendText($Config.L2FTWorkDir)
$L2SIExeTextBox      = Make-TextBox -Location (New-object System.Drawing.Point(160, 390))
$L2SIExeTextBox.AppendText($Config.L2SIExe)
$L2SIWorkDirTextBox  = Make-TextBox -Location (New-object System.Drawing.Point(160, 420))
$L2SIWorkDirTextBox.AppendText($Config.L2SIWorkDir)
$L2SMExeTextBox      = Make-TextBox -Location (New-object System.Drawing.Point(160, 450))
$L2SMExeTextBox.AppendText($Config.L2SMExe)
$L2SMWorkDirTextBox  = Make-TextBox -Location (New-object System.Drawing.Point(160, 480))
$L2SMWorkDirTextBox.AppendText($Config.L2SMWorkDir)
$PAMExeTextBox       = Make-TextBox -Location (New-object System.Drawing.Point(160, 510))
$PAMExeTextBox.AppendText($Config.PAMExe)
$PAMWorkDirTextBox   = Make-TextBox -Location (New-object System.Drawing.Point(160, 540))
$PAMWorkDirTextBox.AppendText($Config.PAMWorkDir)

$DataDirBrowseButton      = Make-ExeBrowseButton -Location (New-object System.Drawing.Point(430, 30)) `
    -Kind ([ExplorerKind]::Dir)  -TextBox $DataDirTextBox;
$BackupDirBrowseButton    = Make-ExeBrowseButton -Location (New-object System.Drawing.Point(430, 60)) `
    -Kind ([ExplorerKind]::Dir)  -TextBox $BackupDirTextBox
$L1AExeBrowseButton       = Make-ExeBrowseButton -Location (New-object System.Drawing.Point(430, 90)) `
    -Kind ([ExplorerKind]::File) -TextBox $L1AExeTextBox
$L1AWorkDirBrowseButton   = Make-ExeBrowseButton -Location (New-object System.Drawing.Point(430, 120)) `
    -Kind ([ExplorerKind]::Dir)  -TextBox $L1AWorkDirTextBox
$L1BExeBrowseButton       = Make-ExeBrowseButton -Location (New-object System.Drawing.Point(430, 150)) `
    -Kind ([ExplorerKind]::File) -TextBox $L1BExeTextBox
$L1BWorkDirBrowseButton   = Make-ExeBrowseButton -Location (New-object System.Drawing.Point(430, 180)) `
    -Kind ([ExplorerKind]::Dir)  -TextBox $L1BWorkDirTextBox
$L1BMMExeBrowseButton     = Make-ExeBrowseButton -Location (New-object System.Drawing.Point(430, 210)) `
    -Kind ([ExplorerKind]::File) -TextBox $L1BMMExeTextBox
$L1BMMWorkDirBrowseButton = Make-ExeBrowseButton -Location (New-object System.Drawing.Point(430, 240)) `
    -Kind ([ExplorerKind]::Dir)  -TextBox $L1BMMWorkDirTextBox
$L2FBExeBrowseButton      = Make-ExeBrowseButton -Location (New-object System.Drawing.Point(430, 270)) `
    -Kind ([ExplorerKind]::File) -TextBox $L2FBExeTextBox
$L2FBWorkDirBrowseButton  = Make-ExeBrowseButton -Location (New-object System.Drawing.Point(430, 300)) `
    -Kind ([ExplorerKind]::Dir)  -TextBox $L2FBWorkDirTextBox
$L2FTExeBrowseButton      = Make-ExeBrowseButton -Location (New-object System.Drawing.Point(430, 330)) `
    -Kind ([ExplorerKind]::File) -TextBox $L2FTExeTextBox
$L2FTWorkDirBrowseButton  = Make-ExeBrowseButton -Location (New-object System.Drawing.Point(430, 360)) `
    -Kind ([ExplorerKind]::Dir)  -TextBox $L2FTWorkDirTextBox
$L2SIExeBrowseButton      = Make-ExeBrowseButton -Location (New-object System.Drawing.Point(430, 390)) `
    -Kind ([ExplorerKind]::File) -TextBox $L2SIExeTextBox
$L2SIWorkDirBrowseButton  = Make-ExeBrowseButton -Location (New-object System.Drawing.Point(430, 420)) `
    -Kind ([ExplorerKind]::Dir)  -TextBox $L2SIWorkDirTextBox
$L2SMExeBrowseButton      = Make-ExeBrowseButton -Location (New-object System.Drawing.Point(430, 450)) `
    -Kind ([ExplorerKind]::File) -TextBox $L2SMExeTextBox
$L2SMWorkDirBrowseButton  = Make-ExeBrowseButton -Location (New-object System.Drawing.Point(430, 480)) `
    -Kind ([ExplorerKind]::Dir)  -TextBox $L2SMWorkDirTextBox
$PAMExeBrowseButton       = Make-ExeBrowseButton -Location (New-object System.Drawing.Point(430, 510)) `
    -Kind ([ExplorerKind]::File) -TextBox $PAMExeTextBox
$PAMWorkDirBrowseButton   = Make-ExeBrowseButton -Location (New-object System.Drawing.Point(430, 540)) `
    -Kind ([ExplorerKind]::Dir)  -TextBox $PAMWorkDirTextBox

$SaveSettingsButton = Make-Button -Text "Save" -Location (New-object System.Drawing.Point(350, 580))
$SaveSettingsButton.Add_Click({
@"
{
`t"DataDir":      "$($BackupDirTextBox.Text)",
`t"BackupDir":    "$($DataDirTextBox.Text)",
`t"L1AExe":       "$($L1AExeTextBox.Text)",
`t"L1AWorkDir":   "$($L1AWorkDirTextBox.Text)",
`t"L1BExe":       "$($L1BExeTextBox.Text)",
`t"L1BWorkDir":   "$($L1BWorkDirTextBox.Text)",
`t"L1BMMExe":     "$($L1BMMExeTextBox.Text)",
`t"L1BMMWorkDir": "$($L1BMMWorkDirTextBox.Text)",
`t"L2FBExe":      "$($L2FBExeTextBox.Text)",
`t"L2FBWorkDir":  "$($L2FBWorkDirTextBox.Text)",
`t"L2FTExe":      "$($L2FTExeTextBox.Text)",
`t"L2FTWorkDir":  "$($L2FTWorkDirTextBox.Text)",
`t"L2SIExe":      "$($L2SIExeTextBox.Text)",
`t"L2SIWorkDir":  "$($L2SIWorkDirTextBox.Text)",
`t"L2SMExe":      "$($L2SMExeTextBox.Text)",
`t"L2SMWorkDir":  "$($L2SMWorkDirTextBox.Text)",
`t"PAMExe":       "$($PAMExeTextBox.Text)",
`t"PAMWorkDir":   "$($PAMWorkDirTextBox.Text)"
}
"@ | Out-File -FilePath "config.json"
})

# TODO: we need a button to save the new configuration.
$SettingsForm = New-Object System.Windows.Forms.Form
$SettingsForm.ClientSize = "550, 650"
$SettingsForm.Text = "Orchestrator - Settings"
$SettingsForm.BackColor = "#ffffff"
$SettingsForm.FormBorderStyle = 'Fixed3D'
$SettingsForm.MaximizeBox = $false
$SettingsForm.Controls.AddRange(@(
        $DataDirLabel,     $DataDirTextBox,     $DataDirBrowseButton,
        $BackupDirLabel,   $BackupDirTextBox,   $BackupDirBrowseButton,
        $L1AExeLabel,      $L1AExeTextBox,      $L1AExeBrowseButton,
        $L1AWorkDirLabel,  $L1AWorkDirTextBox,  $L1AWorkDirBrowseButton,
        $L1BExeLabel,      $L1BExeTextBox,      $L1BExeBrowseButton,
        $L1BWorkDirLabel,  $L1BWorkDirTextBox,  $L1BWorkDirBrowseButton,
        $L1BMMExeLabel,    $L1BMMExeTextBox,    $L1BMMExeBrowseButton,
        $L1BMMWorkDirLabel,$L1BMMWorkDirTextBox,$L1BMMWorkDirBrowseButton,
        $L2FBExeLabel,     $L2FBExeTextBox,     $L2FBExeBrowseButton,
        $L2FBWorkDirLabel, $L2FBWorkDirTextBox, $L2FBWorkDirBrowseButton,
        $L2FTExeLabel,     $L2FTExeTextBox,     $L2FTExeBrowseButton,
        $L2FTWorkDirLabel, $L2FTWorkDirTextBox, $L2FTWorkDirBrowseButton,
        $L2SIExeLabel,     $L2SIExeTextBox,     $L2SIExeBrowseButton,
        $L2SIWorkDirLabel, $L2SIWorkDirTextBox, $L2SIWorkDirBrowseButton,
        $L2SMExeLabel,     $L2SMExeTextBox,     $L2SMExeBrowseButton,
        $L2SMWorkDirLabel, $L2SMWorkDirTextBox, $L2SMWorkDirBrowseButton,
        $PAMExeLabel,      $PAMExeTextBox,      $PAMExeBrowseButton,
        $PAMWorkDirLabel,  $PAMWorkDirTextBox,  $PAMWorkDirBrowseButton,
        $SaveSettingsButton
    )
)

################################################################################
# Main Form                                                                    #
################################################################################

function Make-ProcessorsComboBox {
    param (
        [parameter(Mandatory=$true)]
        [System.Drawing.Point]$Location
    )

    $ComboBox = New-Object System.Windows.Forms.ComboBox
    $ComboBox.Location = $Location
    $ComboBox.width = 60
    $ComboBox.Items.AddRange(@([enum]::GetValues([Processor])))
    $ComboBox.SelectedIndex = 0
    $ComboBox.Font = $DefaultFont
    $ComboBox.DropDownStyle = [System.Windows.Forms.ComboBoxStyle]::DropDownList

    return $ComboBox
}

$StartLabel      = Make-Label -Text "Start" -Location (New-object System.Drawing.Point(20, 20))
$StartComboBox = Make-ProcessorsComboBox    -Location (New-object System.Drawing.Point(60, 20))
$EndLabel        = Make-Label -Text "End"   -Location (New-object System.Drawing.Point(130, 20))
$EndComboBox   = Make-ProcessorsComboBox    -Location (New-object System.Drawing.Point(170, 20))
$PAMLabel        = Make-Label -Text "PAM"   -Location (New-object System.Drawing.Point(240, 20))
$PAMCheckBox = New-Object System.Windows.Forms.CheckBox
$PAMCheckBox.Location = New-Object System.Drawing.Point(280, 20)
$PAMCheckBox.Enabled = $false # Since we always start from L1A

$BackupFileTextBox = Make-TextBox -Location (New-object System.Drawing.Point(140, 100))
$BackupFileTextBox.Enabled = $false # Since we always start from L1A
$BackupFileButton = Make-Button -Text "Choose Backup" `
    -Location (New-object System.Drawing.Point(20, 100))
$BackupFileButton.Add_Click({
    $Result = $ZipBrowser.ShowDialog()
    if ($Result -eq [System.Windows.Forms.DialogResult]::Cancel) {
        return
    }
    $BackupFileTextBox.Text = ""
    $BackupFileTextBox.AppendText($ZipBrowser.FileName)
})
$BackupFileButton.Enabled = $false # Since we always start from L1A

$RunButton = Make-Button -Text "Run!" -Location (New-object System.Drawing.Point(50, 150))
$RunButton.Add_Click({
    # TODO: should this be logged to a file like the previous orchestrator does?
    try {
        Do-Orchestration `
            -Start ([Processor]$StartComboBox.SelectedIndex) -End ([Processor]$EndComboBox.SelectedIndex) `
            -usePAM $PAMCheckBox.Checked `
            -BackupDir $BackupDirTextBox.Text -DataDir $DataDirTextBox.Text `
            -L1_Awd $L1AWorkDirTextBox.Text -L1_Aexe $L1AExeTextBox.Text `
            -L1_Bwd $L1BWorkDirTextBox.Text -L1_Bexe $L1BExeTextBox.Text `
            -L1_B_MMwd $L1BMMWorkDirTextBox.Text -L1_B_MMexe $L1BMMExeTextBox.Text `
            -L2_FBwd $L2FBWorkDirTextBox.Text -L2_FBexe $L2FBExeTextBox.Text `
            -L2_FTwd $L2FTWorkDirTextBox.Text -L2_FTexe $L2FTExeTextBox.Text `
            -L2_SIwd $L2SIWorkDirTextBox.Text -L2_SIexe $L2SIExeTextBox.Text `
            -L2_SMwd $L2SMWorkDirTextBox.Text -L2_SMexe $L2SMExeTextBox.Text `
            -PAMwd $PAMWorkDirTextBox.Text -PAMexe $PAMExeTextBox.Text `
        | Out-Host
    } catch {
        # NOTE: Here we could show a dialog.
        Write-Error "The Orchestrator incurred in an error."
    }
})

$SettingsButton = Make-Button -Text "Settings" -Location (New-object System.Drawing.Point(130, 150))
$SettingsButton.Add_Click({
    $SettingsForm.ShowDialog() | Out-Null
})

$StartComboBox.Add_SelectedIndexChanged({
    if ($this.SelectedIndex -lt 2) {
        if ($this.SelectedIndex -gt $EndComboBox.SelectedIndex) {
            $EndComboBox.SelectedIndex = $this.SelectedIndex
        }
    }

    if ($this.SelectedIndex -gt 1) {
              if ($this.SelectedItem -eq "L2FB") {
            $EndComboBox.SelectedItem = "L2FB"
        } elseif ($this.SelectedItem -eq "L2FT") {
            $EndComboBox.SelectedItem = "L2FT"
        } elseif ($this.SelectedItem -eq "L2SM") {
            $EndComboBox.SelectedItem = "L2SM"
        } elseif ($this.SelectedItem -eq "L2SI") {
            $EndComboBox.SelectedItem = "L2SI"
        }
    }

    if ($this.SelectedItem -eq "L1A" -and $EndComboBox.SelectedItem -eq "L1A") {
        $PAMCheckBox.Checked = $false
        $PAMCheckBox.Enabled = $false
    } else {
        $PAMCheckBox.Enabled = $true
    }

    if ($this.SelectedItem -eq "L1A") {
        $BackupFileButton.Enabled = $false
        $BackupFileTextBox.Text = ""
        $BackupFileTextBox.Enabled = $false
    } else {
        $BackupFileButton.Enabled = $true
        $BackupFileTextBox.Enabled = $true
    }
})

$EndComboBox.Add_SelectedIndexChanged({
    if ($this.SelectedIndex -lt 2) {
        if ($this.SelectedIndex -lt $StartComboBox.SelectedIndex) {
            $StartComboBox.SelectedIndex = $this.SelectedIndex
        }
    }

    if ($StartComboBox.SelectedIndex -gt 1) {
              if ($this.SelectedItem -eq "L2FB") {
            $StartComboBox.SelectedItem = "L2FB"
        } elseif ($this.SelectedItem -eq "L2FT") {
            $StartComboBox.SelectedItem = "L2FT"
        } elseif ($this.SelectedItem -eq "L2SM") {
            $StartComboBox.SelectedItem = "L2SM"
        } elseif ($this.SelectedItem -eq "L2SI") {
            $StartComboBox.SelectedItem = "L2SI"
        }
    }

    if ($this.SelectedItem -eq "L1A" -and $StartComboBox.SelectedItem -eq "L1A") {
        $PAMCheckBox.Checked = $false
        $PAMCheckBox.Enabled = $false
    } else {
        $PAMCheckBox.Enabled = $true
    }
})

$MainForm = New-Object System.Windows.Forms.Form
$MainForm.ClientSize = "400, 300"
$MainForm.Text = "Orchestrator"
$MainForm.BackColor = "#ffffff"
$MainForm.FormBorderStyle = "Fixed3D"
$MainForm.MaximizeBox = $false
$MainForm.Controls.AddRange(@(
        $StartLabel, $StartComboBox, $EndLabel, $EndComboBox, $PAMLabel, $PAMCheckBox,
        $BackupFileButton, $BackupFileTextBox,
        $RunButton, $SettingsButton
    )
)
$MainForm.Add_Closing({
    param(
        $sender,
        $e
    )
    if ($false) {
        $Result = [System.Windows.Forms.MessageBox]::Show(
            "Are you sure you want to exit?",
            "Close",
            [System.Windows.Forms.MessageBoxButtons]::YesNoCancel
        )
        if ($Result -ne [System.Windows.Forms.DialogResult]::Yes) {
            $e.Cancel= $true
        }
    }
})
$MainForm.ShowDialog() | Out-Null
