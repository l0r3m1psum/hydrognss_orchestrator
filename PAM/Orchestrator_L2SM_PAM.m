function Orchestrator_L2SM(ref_outpath,dataRoot,Backup_Root, ZipFolder)
format long;
format compact;

found=false;

%% DATA FROM L1B Processor
while(found==false)

    currpath=pwd;
    temppath = [currpath '\temp\'];

    if ~exist(temppath,'dir')
        mkdir(temppath)
    end

    file=unzip([Backup_Root '\' ZipFolder],temppath);

    filename = 'L2OP-SSM.nc';
    len_f=length(filename);

    %% DATA FROM HSAVERS SIMULATIONS
    referenceFile=[ZipFolder(1:end-11) '.mat'];
    load([Backup_Root '\PAM\' referenceFile ]);

    Nrun=size(inOutReferenceFile,2);

    %%
    Metadatalist = {};

    j=0;
    for i=1:length(file)
        if file{i}(end-len_f+1:end)==filename
            j=j+1;
            Metadatalist{j}=file{i};
            found=true;

        end
    end
    %
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
SM_TOT=[];
TidOrbit_TOT=[];
spLAT_TOT=[];
spLON_TOT=[];
Ref_chan_tot=[];
SM_TOT2=[];

for k = 1:numberOfFiles

    fprintf('Processing file %s\n', Metadatalist{k});

    % Get NC files.

    info(k)=ncinfo(Metadatalist{k});

    ncid = netcdf.open(Metadatalist{k}, 'NC_NOWRITE'); %Read-only access (Default)
    trackNcids = netcdf.inqGrps(ncid); %Retrieve array of child group IDs
    Ntrack_in_metadata=length(trackNcids);

    for track = 1:Ntrack_in_metadata
        TrackIDOrbit_att_name(track,:) = netcdf.inqAttName(trackNcids(track),netcdf.getConstant('NC_GLOBAL'),2);
        TrackIDOrbit_att_value{track,:} = netcdf.getAtt(trackNcids(track),netcdf.getConstant('NC_GLOBAL'),TrackIDOrbit_att_name(track,:));
    end

    for kk = 1:Ntrack_in_metadata
        TrackIDOrbit=TrackIDOrbit_att_value{kk};

        varSM = netcdf.inqVarID(trackNcids(kk), 'SoilMoisture');
        SoilMoisture = netcdf.getVar(trackNcids(kk), varSM, 'double');
        varLatitudes = netcdf.inqVarID(trackNcids(kk), 'DataMeanLatitude');
        Latitudes= netcdf.getVar(trackNcids(kk), varLatitudes, 'double');
        varLongitudes = netcdf.inqVarID(trackNcids(kk), 'DataMeanLongitude');
        Longitudes= netcdf.getVar(trackNcids(kk), varLongitudes, 'double');
        varQuality_Flag = netcdf.inqVarID(trackNcids(kk), 'QualityFlag');
        Quality_Flag= netcdf.getVar(trackNcids(kk), varQuality_Flag, 'double');
        varUncertainty_Flag = netcdf.inqVarID(trackNcids(kk), 'Uncertainty');
        Uncertainty_Flag = netcdf.getVar(trackNcids(kk), varUncertainty_Flag, 'double');

        nPS=size(Latitudes,1);

        for k=1:nPS
            TidOrbit_TOT=[TidOrbit_TOT;TrackIDOrbit'];
            SM_TOT2=[SM_TOT2;SoilMoisture(k,:)];
            spLAT_TOT=[spLAT_TOT;Latitudes(k,:)];
            spLON_TOT=[spLON_TOT;Longitudes(k,:)];
        end
        clear('SoilMoisture','Latitudes','Longitudes','QualityFlag','Uncertainty','TrackIDOrbit')
    end

    netcdf.close(ncid)

end

fclose('all');

%%

SPLat=inOutReferenceFile(1).geoSYSp.SPlat_series;
SPLon=inOutReferenceFile(1).geoSYSp.SPlon_series;

for irun=1:Nrun

    Tid(irun,:)=inOutReferenceFile(irun).TrackID;
    CoverAtSp(irun,:)=inOutReferenceFile(irun).bioGeoParametersAtSP.classOfSPinCoverMap; % tutta la simulazione ha la stessa sm
    SMrun(irun,:)=inOutReferenceFile(irun).bioGeoParametersAtSP.soilMoistureAtSP; % tutta la simulazione ha la stessa sm
end
SM=unique(SMrun);

% %% LANDCOVER MAP
sizeInputMapWindow=inOutReferenceFile(1).DEMinfo.sizeInputMapWindow;
SP_lla_onEllipsoid(:,1)=SPLat;
SP_lla_onEllipsoid(:,2)=SPLon;

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
hold on
plot(spLON_TOT,spLAT_TOT,'b*','MarkerSize',12)
%%
compL=[];
for imeta=1:size(TidOrbit_TOT,1)
    indSM=TidOrbit_TOT(imeta)/1000000;
    compL(imeta,1)=SM(indSM);
    compL(imeta,2)=SM_TOT2(imeta);
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
h3=plot([ax.XLim(1) ax.XLim(2)],[ax.XLim(1) ax.XLim(2)],'k');
grid on
xlabel('HSAVERS SM [%] ')
ylabel('L2 SM [%]')
grid on
hold on
[~, index]=sort(y_fitL,'ascend');
%  plot(compL(:,1),y_fitL,'r')
h1=plot(compL(index,1),y_fitL(index),'r');
hold on
h2=plot(compL(index,1),y_fitL(index)+2*deltaL(index),'b') ;
hold on
plot(compL(index,1),y_fitL(index)-2*deltaL(index),'b');
box on
legend([h1 h2 h3],{'linear fit','95% confidence','1:1 line'},'Location','Northwest')
title({['R=',num2str(round(RL,2)), '  RMSE=' num2str(round(RMSEL,2)) '%,  UnB RMSE= ' num2str(round(UB_RMSEL,2))  '%,  slope=' num2str(round(slopeL,2))]})

runDate=datestr(now);
runDate([12,15,18])='_';

saveas(fig1,[ref_outpath referenceFile(1:end-4) '_' runDate '_cover_map.jpg'])
saveas(fig1,[ref_outpath referenceFile(1:end-4) '_' runDate '_cover_map.fig'])
saveas(fig2,[ref_outpath referenceFile(1:end-4) '_' runDate '_SM.jpg'])
saveas(fig2,[ref_outpath referenceFile(1:end-4) '_' runDate '_SM.fig'])

fid1 = fopen([ref_outpath referenceFile(1:end-4) '_' runDate '_SM.txt'],'wt');
fprintf(fid1,'%s\n',['R=',num2str(round(RL,2)), '  RMSE=' num2str(round(RMSEL,2)) '%,  UnB RMSE=' num2str(round(UB_RMSEL,2))  '%,  slope=' num2str(round(slopeL,2))]);
fclose(fid1);

rmdir(temppath,'s')
end