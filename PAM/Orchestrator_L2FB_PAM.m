function Orchestrator_L2FB_PAM(ref_outpath,dataRoot,Backup_Root, ZipFolder)
format long;
format compact;

found=false;

%% DATA FROM L2 BIOMASS Processor
while(found==false)

    currpath=pwd;
    temppath = [currpath '\temp\'];

    if ~exist(temppath,'dir')
        mkdir(temppath)
    end

    file=unzip([Backup_Root '\' ZipFolder],temppath);

    filename = '\L2L3OP-FB.nc';
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

%Metadata L2 final variables
AGB_TOT=[];
TidOrbit_TOT=[];
spLAT_TOT=[];
spLON_TOT=[];
Ref_chan_tot=[];

for k = 1:numberOfFiles

    fprintf('Processing file %s\n', Metadatalist{k});

    % Get NC files.

    info(k)=ncinfo(Metadatalist{k});

    ncid = netcdf.open(Metadatalist{k}, 'NC_NOWRITE'); %Read-only access (Default)
    trackNcids = netcdf.inqGrps(ncid); %Retrieve array of child group IDs
    Ntrack_in_metadata=length(trackNcids);

    for track = 1:1 %Group L2 (1st group) read L2 only, not L3
        TrackID_att_name(track,:) = netcdf.inqAttName(trackNcids(track),netcdf.getConstant('NC_GLOBAL'),0);
        TrackID_att_value{track,:} = netcdf.getAtt(trackNcids(track),netcdf.getConstant('NC_GLOBAL'),TrackID_att_name(track,:));
        TrackIDOrbit_att_name(track,:) = netcdf.inqAttName(trackNcids(track),netcdf.getConstant('NC_GLOBAL'),1);
        TrackIDOrbit_att_value{track,:} = netcdf.getAtt(trackNcids(track),netcdf.getConstant('NC_GLOBAL'),TrackIDOrbit_att_name(track,:));
    end

    for kk = 1:1%Ntrack_in_metadata %we read L2 only, not L3 (1st group)

        TrackID(:)=TrackID_att_value{:};
        TrackIDOrbit(:)=TrackIDOrbit_att_value{:};

        varAGB = netcdf.inqVarID(trackNcids(kk), 'AGB');
        AGB(:) = netcdf.getVar(trackNcids(kk), varAGB, 'double');
        varLatitudes = netcdf.inqVarID(trackNcids(kk), 'OnBoardLatitudes');
        Latitudes(:)= netcdf.getVar(trackNcids(kk), varLatitudes, 'double');
        varLongitudes = netcdf.inqVarID(trackNcids(kk), 'OnBoardLongitudes');
        Longitudes(:)= netcdf.getVar(trackNcids(kk), varLongitudes, 'double');
        varQuality_Flag = netcdf.inqVarID(trackNcids(kk), 'Quality_Flag');
        Quality_Flag(:)= netcdf.getVar(trackNcids(kk), varQuality_Flag, 'double');
        varUncertainty_Flag = netcdf.inqVarID(trackNcids(kk), 'Uncertainty_Flag');
        Uncertainty_Flag(:) = netcdf.getVar(trackNcids(kk), varUncertainty_Flag, 'double');

        AGB_TOT=[AGB_TOT;AGB'];
        TidOrbit_TOT=[TidOrbit_TOT;TrackIDOrbit'];
        spLAT_TOT=[spLAT_TOT;Latitudes'];
        spLON_TOT=[spLON_TOT;Longitudes'];

        clear('AGB','Latitudes','Longitudes','Quality_Flag','Uncertainty_Flag','TrackID','TrackIDOrbit')

    end

    netcdf.close(ncid)

end

fclose('all');

%% HSAVERS SIMULATIONS

SPLat=inOutReferenceFile(1).geoSYSp.SPlat_series;
SPLon=inOutReferenceFile(1).geoSYSp.SPlon_series;

for irun=1:Nrun
    gamma_LR(irun,:)=inOutReferenceFile(irun).max_reflectivity_noNoise_LR_dB;
    gamma_RR(irun,:)=inOutReferenceFile(irun).max_reflectivity_noNoise_RR_dB;

    Tid(irun,:)=inOutReferenceFile(irun).TrackID;
    SP_LCM(irun,:)=inOutReferenceFile(irun).bioGeoParametersAtSP.classOfSPinCoverMap; % tutta la simulazione ha la stessa sm
    BioValid(irun,:)=inOutReferenceFile(irun).bioGeoParametersAtSP.BioAtSP; % tutta la simulazione ha la stessa sm
end

%%
% %% LANDCOVER MAP
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
plot(spLON_TOT,spLAT_TOT,'b*','MarkerSize',12)

%% HSAVERS DATA & L2 PROCESSOR OUTPUT
count_comp=0;
for irun=1:Nrun
    for ips=1:length(SPLat)
        for imeta=1:size(TidOrbit_TOT,1)
            %
            if Tid(irun,ips)==TidOrbit_TOT(imeta) && SPLat(ips)<=spLAT_TOT(imeta)+0.00005 && SPLat(ips)>=spLAT_TOT(imeta)-0.00005 && SPLon(ips)<=spLON_TOT(imeta)+0.00005  && SPLon(ips)>=spLON_TOT(imeta)-0.00005
                count_comp=count_comp+1;

                compL(count_comp,1)=BioValid(irun,ips);

                compL(count_comp,2)=AGB_TOT(imeta);

                LAT(count_comp,1)=SPLat(ips);
                LAT(count_comp,2)=spLAT_TOT(imeta);

            end
        end
    end
end

ind_nan=isnan(compL(:,2));
compL(ind_nan,:)=[];

R_matrixL = corrcoef(compL(:,1),compL(:,2));
RL=R_matrixL(1,2);
% RL=R_matrixL;
RMSEL = sqrt(mean((compL(:,1)-compL(:,2)).^2));
BIAS_L = mean(compL(:,1)-compL(:,2));
UB_RMSEL=sqrt(RMSEL^2-BIAS_L^2);

[PL SL]  = polyfit(compL(:,1),compL(:,2),1);
[y_fitL,deltaL] = polyval(PL,compL(:,1),SL);
slopeL = PL(1);

fig2=figure;
plot(compL(:,1),compL(:,2),'o','MarkerEdgeColor','#0072BD','MarkerFaceColor','#0072BD')
hold on
ax=gca;
plot([ax.XLim(1) ax.XLim(2)],[ax.XLim(1) ax.XLim(2)],'-k')
grid on
xlabel('HSAVERS AGB [t/ha] ')
ylabel('L2 AGB [t/ha]')
grid on
hold on
[~, index]=sort(y_fitL,'ascend');
%  plot(compL(:,1),y_fitL,'r')
h1=plot(compL(index,1),y_fitL(index),'r');
hold on
h2=plot(compL(index,1),y_fitL(index)+2*deltaL(index),'b') ;
hold on
plot(compL(index,1),y_fitL(index)-2*deltaL(index),'b');
hold on
h3=plot([ax.XLim(1) ax.XLim(2)],[ax.XLim(1) ax.XLim(2)],'k');
box on
legend([h1 h2 h3],{'linear fit','95% confidence','1:1 line'},'Location','best')
title({['R=',num2str(round(RL,2)), '  RMSE=' num2str(round(RMSEL,2)) 't/ha,  UnB RMSE= ' num2str(round(UB_RMSEL,2))  't/ha,  slope=' num2str(round(slopeL,2))]})

runDate=datestr(now);
runDate([12,15,18])='_';

saveas(fig1,[ref_outpath referenceFile(1:end-4) '_' runDate '_cover_map.jpg'])
saveas(fig1,[ref_outpath referenceFile(1:end-4) '_' runDate '_cover_map.fig'])
saveas(fig2,[ref_outpath referenceFile(1:end-4) '_' runDate '_Biomass.jpg'])
saveas(fig2,[ref_outpath referenceFile(1:end-4) '_' runDate '_Biomass.fig'])

fid1 = fopen([ref_outpath referenceFile(1:end-4) '_' runDate '_Biomass.txt'],'wt');
fprintf(fid1,'%s\n',['R=',num2str(round(RL,2)), '  RMSE=' num2str(round(RMSEL,2)) 't/ha,  UnB RMSE=' num2str(round(UB_RMSEL,2))  't/ha,  slope=' num2str(round(slopeL,2))]);
fclose(fid1);
rmdir(temppath,'s')
end