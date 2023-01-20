function PAM_start(L2processor, dataRoot, Backup_Root, ZipFolder)
currpath=pwd;
ref_outpath = [Backup_Root '\PAM_Output\'];
if ~exist(ref_outpath,'dir')
    mkdir(ref_outpath);
end
switch L2processor
    case 'L1_B'
        disp('L1b')
        Orchestrator_L1b_PAM(ref_outpath,dataRoot,Backup_Root, ZipFolder);
    case  'L2_FB'
        disp('L2 BIOMASS')
        Orchestrator_L2FB_PAM(ref_outpath,dataRoot,Backup_Root, ZipFolder);
    case  'L2_SI'
        disp('L2 INUNDATION')
        Orchestrator_L2SI_PAM(ref_outpath,dataRoot,Backup_Root, ZipFolder);
    case  'L2_SM'
        disp('L2 SOIL MOISTURE')
        Orchestrator_L2SM_PAM(ref_outpath,dataRoot,Backup_Root, ZipFolder);
    case  'L2_FT'
        disp('L2 FROZEN/THAW')
        Orchestrator_L2FT_PAM(ref_outpath,dataRoot,Backup_Root, ZipFolder);
    otherwise
        disp('error')
end

all_fig = findall(0, 'type', 'figure');
close(all_fig)
clear all

