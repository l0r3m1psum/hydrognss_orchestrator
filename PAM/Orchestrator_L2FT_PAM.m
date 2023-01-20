function Orchestrator_L2FT_PAM(ref_outpath,dataRoot,Backup_Root, ZipFolder)
format long g;
format compact;

found=false;

%% DATA FROM L2 FT Processor
while(found==false)

    currpath=pwd;
    temppath = [currpath '\temp\'];

    if ~exist(temppath,'dir')
        mkdir(temppath)
    end

    file=unzip([Backup_Root '\' ZipFolder],temppath);
    %
    filename = '\FTstate';

    %% DATA FROM HSAVERS SIMULATIONS
    referenceFile=[ZipFolder(1:end-11) '.mat'];
    load([Backup_Root '\PAM\' referenceFile ]);

    Nrun=size(inOutReferenceFile,2);

    %%
    Metadatalist = {};

    j=0;
    for i=1:length(file)
        if contains(file{i},filename)
            j=j+1;
            Metadatalist{j}=file{i};
            found=true;
        end
    end
    if found==false
        mh=msgbox('Metadata not found. PAM execution will stop.');
        th = findall(mh, 'Type', 'Text');                   %get handle to text within msgbox
        th.FontSize = 10;
        deltaWidth = sum(th.Extent([1,3]))-mh.Position(3) + th.Extent(1) + 10;
        deltaHeight = sum(th.Extent([2,4]))-mh.Position(4) + 10;
        mh.Position([3,4]) = mh.Position([3,4]) + [deltaWidth, deltaHeight];
        % mh.Resize = 'on';
        uiwait(mh);
        error('Metadata not found. PAM execution will stop.');
    end
end

numberOfFiles = length( Metadatalist);

%Metadata L2 final variables
F_TOT=[];
True_TOT=[];

for k = 1:numberOfFiles

    fprintf('Processing file %s\n', Metadatalist{k});

    %% Get NC metadata L2 FT files contained in the zip file.

    info(k)=ncinfo(Metadatalist{k});
    FT_truth(k)=str2num(Metadatalist{k}(end-4:end-4));
    if FT_truth(k)==2, FT_truth(k)=3; end;
    ncid = netcdf.open(Metadatalist{k}, 'NC_NOWRITE'); %Read-only access (Default)
    trackNcids = netcdf.inqGrps(ncid); %Retrieve array of child group IDs

    varIdFT = netcdf.inqVarID(ncid, 'Freeze Thaw');
    Freeze_Thaw = netcdf.getVar(ncid, varIdFT, 'uint8');
    FT=reshape(Freeze_Thaw,size(Freeze_Thaw,1)*size(Freeze_Thaw,2),1);
    ind=find(FT==255);
    FT(ind)=[];
    True=FT_truth(k)*ones(length(FT),1);
    F_TOT=[F_TOT;FT];
    True_TOT=[True_TOT;True];

    clear Freeze_Thaw  FT True

    netcdf.close(ncid)

end
fclose('all');

SPLat=inOutReferenceFile(1).geoSYSp.SPlat_series;
SPLon=inOutReferenceFile(1).geoSYSp.SPlon_series;

sizeInputMapWindow=inOutReferenceFile(1).DEMinfo.sizeInputMapWindow;
SP_lla_onEllipsoid(:,1)=SPLat;
SP_lla_onEllipsoid(:,2)=SPLon;

%%
% %% LANDCOVER MAP
coverMapFilename=[dataRoot '\AuxiliaryFiles\LandCoverMap\ESACCI-LC-L4-LCCS-Map-300m-P1Y-2015-v2.0.7b.nc'];
[landCoverMap,dominantClass_ID]=readCoverMapCCI(coverMapFilename, SP_lla_onEllipsoid,sizeInputMapWindow);
% show land cover map in lat-lon

%plot the SPs over the land cover
mapOfColorCover=[0 0 1;0 1 0;1 0 1;0 1 1;1 0 0;1 1 0;0 0 0];

%plot the SPs over the land cover

fig1=figure('Name', 'Land cover map', 'NumberTitle','off','OuterPosition', [50 50 700 510]);
subplot('Position', [0.1 0.12 0.65 0.82]);
mapshow(landCoverMap(:,:,2),landCoverMap(:,:,1),landCoverMap(:,:,3), 'DisplayType', 'texturemap')
colormap(mapOfColorCover)
colorbar('Ticks',[0,1,2,3,4,5,6],'TickLabels',{'0 water bodies','1 broadleaved forest','2 needleleaved forest','3 cropland/grassland/shrubland','4 bare areas','5 flooded forest','6 flooded shrubland'})
caxis([0 6])
title('Land cover map')
xlabel('Longitude [°]')
ylabel('Latitude [°]')
hold on
plot(SPLon,SPLat,'ko','MarkerSize',12)
% hold on
% plot(spLON_TOT,spLAT_TOT,'b*','MarkerSize',12)
% grid on

%% HSAVERS DATA & L2 PROCESSOR OUTPUT
compL(:,1)=True_TOT;
compL(:,2)=F_TOT;

hold off

n_class_1_ref=nnz(compL(:,1)==1);
n_class_3_ref=size(compL(:,1),1)-n_class_1_ref;
n_class_1_metadata=nnz(compL(:,2)==1);
n_class_3_metadata=size(compL(:,2),1)-n_class_1_metadata;

runDate=datestr(now);
runDate([12,15,18])='_';

if n_class_1_ref>0 && n_class_3_ref>0 || n_class_1_metadata>0 && n_class_3_metadata>0

    fig2=figure;
    C = confusionmat(compL(:,1),compL(:,2));

    labels=["Frozen";"Thaw"];
    cm=confusionchart(C,labels,'RowSummary','row-normalized','ColumnSummary','column-normalized');
    cm.OffDiagonalColor = [0.2 0.1 0.3];
    sortClasses(cm,labels);
    cm.FontColor = 'black';

    %% Confusion matrics Metrics
    stats = statsOfMeasure(C, 0);

    acc_perc=table2array(stats(8,2))*100;

    cm.Title=['Confusion matrix    Total accuracy ' num2str(acc_perc(1,1)) '%'];

    saveas(fig1,[ref_outpath referenceFile(1:end-4) '_' runDate '_cover_map.jpg'])
    saveas(fig1,[ref_outpath referenceFile(1:end-4) '_' runDate '_cover_map.fig'])
    saveas(fig2,[ref_outpath referenceFile(1:end-4) '_' runDate '_FT.jpg'])
    saveas(fig2,[ref_outpath referenceFile(1:end-4) '_' runDate '_FT.fig'])

else

    % fid1 = fopen([ref_outpath referenceFile(1:end-4) '_' runDate '_SI_alert.txt'],'wt');
    % fprintf(fid1,'%s\n', 'The confusion matrix contains one class only.');
    % fclose(fid1);
    fig2=figure;
    plot([0 1],[0 1],'w')
    text(0.2,0.5,'The L2 processor finds only one class.','FontSize',12)

    saveas(fig1,[ref_outpath referenceFile(1:end-4) '_' runDate '_cover_map.jpg'])
    saveas(fig1,[ref_outpath referenceFile(1:end-4) '_' runDate '_cover_map.fig'])
    saveas(fig2,[ref_outpath referenceFile(1:end-4) '_' runDate '_FT.jpg'])
    saveas(fig2,[ref_outpath referenceFile(1:end-4) '_' runDate '_FT.fig'])
end

rmdir(temppath,'s')
end