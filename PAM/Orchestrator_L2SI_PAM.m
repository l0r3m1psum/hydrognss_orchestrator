function Orchestrator_L2SI_PAM(ref_outpath,dataRoot,Backup_Root, ZipFolder)
format long g;
format compact;

found=false;

%% DATA FROM L2 SI Processor
while(found==false)

    currpath=pwd;
    temppath = [currpath '\temp\'];

    if ~exist(temppath,'dir')
        mkdir(temppath)
    end

    file=unzip([Backup_Root '\' ZipFolder],temppath);

    filename = '\L2OP_SI.nc';
    numch=length(filename);

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

%Metadata L2SI final variables
WF_TOT_L=[];
WF_TOT_R=[];
TidOrbit_TOT=[];
spLAT_TOT=[];
spLON_TOT=[];

for k = 1:numberOfFiles

    fprintf('Processing file %s\n', Metadatalist{k});

    %% Get NC metadata L2 SI files contained in the zip file.

    info(k)=ncinfo(Metadatalist{k});

    ncid = netcdf.open(Metadatalist{k}, 'NC_NOWRITE'); %Read-only access (Default)
    trackNcids = netcdf.inqGrps(ncid); %Retrieve array of child group IDs
    Ntrack_in_metadata=length(trackNcids);

    for track = 1:Ntrack_in_metadata

        %         [ndim, nvar, natt, unlim] = netcdf.inq(trackNcids(track));

        channelNcids(track,:) = netcdf.inqGrps(trackNcids(track));
        TrackIDOrbit_att_name(track,:) = netcdf.inqAttName(trackNcids(track),netcdf.getConstant('NC_GLOBAL'),1);
        TrackIDOrbit_att_value{track,:} = netcdf.getAtt(trackNcids(track),netcdf.getConstant('NC_GLOBAL'),TrackIDOrbit_att_name(track,:));

        for chan = 1:length(channelNcids(track,:))

            coinNcids{track}(chan,:) = netcdf.inqGrps(channelNcids(track,chan));
        end
    end

    for kk = 1:Ntrack_in_metadata

%         varIdSPLat = netcdf.inqVarID(trackNcids(kk), 'SpecularPointLat');
%         SpecularPointLat = netcdf.getVar(trackNcids(kk), varIdSPLat, 'single');
%         varIdSPLon = netcdf.inqVarID(trackNcids(kk), 'SpecularPointLon');
%         SpecularPointLon = netcdf.getVar(trackNcids(kk), varIdSPLon, 'single');
        varIdSPLat = netcdf.inqVarID(trackNcids(kk), 'OnBoardSpecularPointLat');
        SpecularPointLat = netcdf.getVar(trackNcids(kk), varIdSPLat, 'single');
        varIdSPLon = netcdf.inqVarID(trackNcids(kk), 'OnBoardSpecularPointLon');
        SpecularPointLon = netcdf.getVar(trackNcids(kk), varIdSPLon, 'single');

        TrackIDOrbit=TrackIDOrbit_att_value{kk};

        for chanIdx = 1:chan
            varWF = netcdf.inqVarID(coinNcids{kk}(chanIdx,1), 'WaterFlag');
            WaterFlag(chanIdx,:) = netcdf.getVar(coinNcids{kk}(chanIdx,1), varWF, 'uint16');

        end

        %
        WF_LR(:)=WaterFlag(1,:);
        WF_RR(:)=WaterFlag(2,:);

        clear WaterFlag

        nPS=size(WF_LR,2);

        for k=1:nPS
            WF_TOT_L=[WF_TOT_L;WF_LR(:,k)];
            WF_TOT_R=[WF_TOT_R;WF_RR(:,k)];
            spLAT_TOT=[spLAT_TOT;SpecularPointLat(k,:)];
            spLON_TOT=[spLON_TOT;SpecularPointLon(k,:)];
            TidOrbit_TOT=[TidOrbit_TOT;TrackIDOrbit];

        end
        clear WF_LR WF_RR SpecularPointLat SpecularPointLon TrackIDOrbitL1B
    end

    netcdf.close(ncid)

end

fclose('all');

%% HSAVERS SIMULATIONS

SPLat=inOutReferenceFile(1).geoSYSp.SPlat_series;
SPLon=inOutReferenceFile(1).geoSYSp.SPlon_series;

for irun=1:Nrun
    Tid(irun,:)=inOutReferenceFile(irun).TrackID;
    SP_LCM(irun,:)=inOutReferenceFile(irun).bioGeoParametersAtSP.classOfSPinCoverMap; % tutta la simulazione ha la stessa sm
    flagValid(irun,:)=inOutReferenceFile(irun).bioGeoParametersAtSP.soilStatusAtSP; % tutta la simulazione ha la stessa sm
end
indwater=find(flagValid ==2);
flagValid(indwater)=1;

%% LANDCOVER MAP
sizeInputMapWindow=inOutReferenceFile(1).DEMinfo.sizeInputMapWindow;
SP_lla_onEllipsoid(:,1)=SPLat;
SP_lla_onEllipsoid(:,2)=SPLon;

coverMapFilename=[dataRoot '\AuxiliaryFiles\LandCoverMap\ESACCI-LC-L4-LCCS-Map-300m-P1Y-2015-v2.0.7b.nc'];
[landCoverMap,dominantClass_ID]=readCoverMapCCI(coverMapFilename, SP_lla_onEllipsoid,sizeInputMapWindow);

%plot the SPs over the land cover
mapOfColorCover=[0 0 1;0 1 0;1 0 1;0 1 1;1 0 0;1 1 0;0 0 0];

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
hold on
plot(spLON_TOT,spLAT_TOT,'r*','MarkerSize',12)

%% HSAVERS DATA & L2 PROCESSOR OUTPUT
count_comp=0;
for irun=1:Nrun
    for ips=1:length(SPLat)
        for imeta=1:length(TidOrbit_TOT)
            if Tid(irun,ips)==TidOrbit_TOT(imeta) && SPLat(ips)<=spLAT_TOT(imeta)+0.00005 && SPLat(ips)>=spLAT_TOT(imeta)-0.00005 && SPLon(ips)<=spLON_TOT(imeta)+0.00005  && SPLon(ips)>=spLON_TOT(imeta)-0.00005
                count_comp=count_comp+1;
                compL(count_comp,1)=flagValid(irun,ips);
                compL(count_comp,2)=WF_TOT_L(imeta);
            end
        end
    end
end

hold off

n_class_0_ref=nnz(compL(:,1)==0);
n_class_1_ref=size(compL(:,1),1)-n_class_0_ref;
n_class_0_metadata=nnz(compL(:,2)==0);
n_class_1_metadata=size(compL(:,2),1)-n_class_0_metadata;

runDate=datestr(now);
runDate([12,15,18])='_';


if n_class_0_ref>0 && n_class_1_ref>0 || n_class_0_metadata>0 && n_class_1_metadata>0

    fig2=figure;
    C = confusionmat(compL(:,1),compL(:,2));
    labels_inund=["NonInund.";"Inund."];

    cm=confusionchart(C,labels_inund,'RowSummary','row-normalized','ColumnSummary','column-normalized');
    cm.OffDiagonalColor = [0.2 0.1 0.3];
    sortClasses(cm,labels_inund);
    cm.FontColor = 'black';


    %% Confusion matrics Metrics
    stats = statsOfMeasure(C, 0);

    acc_perc=table2array(stats(8,2))*100;

    cm.Title=['Confusion matrix    Total accuracy ' num2str(acc_perc(1,1)) '%'];

    saveas(fig1,[ref_outpath referenceFile(1:end-4) '_' runDate '_cover_map.jpg'])
    saveas(fig1,[ref_outpath referenceFile(1:end-4) '_' runDate '_cover_map.fig'])
    saveas(fig2,[ref_outpath referenceFile(1:end-4) '_' runDate '_SI.jpg'])
    saveas(fig2,[ref_outpath referenceFile(1:end-4) '_' runDate '_SI.fig'])

else

    % fid1 = fopen([ref_outpath referenceFile(1:end-4) '_' runDate '_SI_alert.txt'],'wt');
    % fprintf(fid1,'%s\n', 'The confusion matrix contains one class only.');
    % fclose(fid1);
    fig2=figure;
    plot([0 1],[0 1],'w')
    text(0.2,0.5,'The L2 processor finds only one class.','FontSize',12)

    saveas(fig1,[ref_outpath referenceFile(1:end-4) '_' runDate '_cover_map.jpg'])
    saveas(fig1,[ref_outpath referenceFile(1:end-4) '_' runDate '_cover_map.fig'])
    saveas(fig2,[ref_outpath referenceFile(1:end-4) '_' runDate '_SI.jpg'])
    saveas(fig2,[ref_outpath referenceFile(1:end-4) '_' runDate '_SI.fig'])
end

rmdir(temppath,'s')
end
