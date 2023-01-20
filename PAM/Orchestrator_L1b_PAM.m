function Orchestrator_L1b_PAM(ref_outpath,dataRoot,Backup_Root, ZipFolder)
format long g;
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

    filename = 'metadata_L1_merged.nc';

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

%Metadata L1 merged final variables
L_RC_TOT=[];
R_RC_TOT=[];
TidOrbit_TOT=[];
spLAT_TOT=[];
spLON_TOT=[];
IntMidPTime_TOT=[];
L_SNR_TOT=[];
R_SNR_TOT=[];
L_AGSP_TOT=[];
R_AGSP_TOT=[];
L_LowSNR_TOT=[];
R_LowSNR_TOT=[];
L_VLowSNR_TOT=[];
R_VLowSNR_TOT=[];
L_DDM_TOT=[];
R_DDM_TOT=[];
L_EIRP_TOT=[];
R_EIRP_TOT=[];

for k = 1:numberOfFiles

    fprintf('Processing file %s\n', Metadatalist{k});

    %% Get NC metadata L1B files contained in the zip file.

    info(k)=ncinfo(Metadatalist{k});

    ncid = netcdf.open(Metadatalist{k}, 'NC_NOWRITE'); %Read-only access (Default)
    trackNcids = netcdf.inqGrps(ncid); %Retrieve array of child group IDs
    Ntrack_in_metadata=length(trackNcids);

    for track = 1:Ntrack_in_metadata

        %         [ndim, nvar, natt, unlim] = netcdf.inq(trackNcids(track));

        channelNcids(track,:) = netcdf.inqGrps(trackNcids(track));
        TrackID_att_name(track,:) = netcdf.inqAttName(trackNcids(track),netcdf.getConstant('NC_GLOBAL'),0);
        TrackID_att_value{track,:} = netcdf.getAtt(trackNcids(track),netcdf.getConstant('NC_GLOBAL'),TrackID_att_name(track,:));
        TrackIDOrbit_att_name(track,:) = netcdf.inqAttName(trackNcids(track),netcdf.getConstant('NC_GLOBAL'),1);
        TrackIDOrbit_att_value{track,:} = netcdf.getAtt(trackNcids(track),netcdf.getConstant('NC_GLOBAL'),TrackIDOrbit_att_name(track,:));
        PNR_att_name(track,:) = netcdf.inqAttName(trackNcids(track),netcdf.getConstant('NC_GLOBAL'),8);
        PNR_att_value{track,:} = netcdf.getAtt(trackNcids(track),netcdf.getConstant('NC_GLOBAL'),PNR_att_name(track,:));

        for chan = 1:length(channelNcids(track,:))
            %             [ndim, nvar, natt, unlim] = netcdf.inq(channelNcids(track,chan));

            coinNcids{track}(chan,:) = netcdf.inqGrps(channelNcids(track,chan));
            Freq_att_name(track,:)= netcdf.inqAttName(channelNcids(track,chan),netcdf.getConstant('NC_GLOBAL'),2); %'SignalFrequency'
            Pol_att_name(track,:) = netcdf.inqAttName(channelNcids(track,chan),netcdf.getConstant('NC_GLOBAL'),3); %'SignalPolarisation'
            Freq_att_value{track,chan} = netcdf.getAtt(channelNcids(track,chan),netcdf.getConstant('NC_GLOBAL'), Freq_att_name(track,:));
            Pol_att_value{track,chan} = netcdf.getAtt(channelNcids(track,chan),netcdf.getConstant('NC_GLOBAL'), Pol_att_name(track,:));
            varAGSP=netcdf.inqVarID(channelNcids(track,chan),'LowAGSP');
            LowAGSP{track,chan}=netcdf.getVar(channelNcids(track,chan), varAGSP, 'uint8');
            varLSNR=netcdf.inqVarID(channelNcids(track,chan),'LowSNR');
            LowSNR{track,chan}=netcdf.getVar(channelNcids(track,chan), varLSNR, 'uint8');
            varVLSNR=netcdf.inqVarID(channelNcids(track,chan),'VeryLowSNR');
            VeryLowSNR{track,chan}=netcdf.getVar(channelNcids(track,chan), varVLSNR, 'uint8');
        end
    end

    for kk = 1:Ntrack_in_metadata
        TrackIDL1B=TrackID_att_value{kk};
        TrackIDOrbitL1B=TrackIDOrbit_att_value{kk};
        PNRL1B=PNR_att_value{kk};
%         varIdSPLat = netcdf.inqVarID(trackNcids(kk), 'SpecularPointLat');
%         SpecularPointLat = netcdf.getVar(trackNcids(kk), varIdSPLat, 'single');
%         varIdSPLon = netcdf.inqVarID(trackNcids(kk), 'SpecularPointLon');
%         SpecularPointLon = netcdf.getVar(trackNcids(kk), varIdSPLon, 'single');
        varIdSPLat = netcdf.inqVarID(trackNcids(kk), 'OnBoardSpecularPointLat');
        SpecularPointLat = netcdf.getVar(trackNcids(kk), varIdSPLat, 'single');
        varIdSPLon = netcdf.inqVarID(trackNcids(kk), 'OnBoardSpecularPointLon');
        SpecularPointLon = netcdf.getVar(trackNcids(kk), varIdSPLon, 'single');

        varIntegrationMidPointTime = netcdf.inqVarID(trackNcids(kk), 'IntegrationMidPointTime');
        IntegrationMidPointTime = netcdf.getVar(trackNcids(kk), varIntegrationMidPointTime, 'double');

        % Coherent data is in column (chanIdx,2)
        for chanIdx = 1:chan
            varRefCoeffAtSP = netcdf.inqVarID(coinNcids{kk}(chanIdx,1), 'ReflectionCoefficientAtSP');
            ReflectionCoefficientAtSP(chanIdx,:) = netcdf.getVar(coinNcids{kk}(chanIdx,1), varRefCoeffAtSP, 'double');
            varSNR= netcdf.inqVarID(coinNcids{kk}(chanIdx,1),'DDMSNRAtPeakSingleDDM');
            DDMSNRAtSP(chanIdx,:) = netcdf.getVar(coinNcids{kk}(chanIdx,1), varSNR, 'double');
            FreqL1B(chanIdx,:)=Freq_att_value{kk,chanIdx};
            PolL1B(chanIdx,:)= Pol_att_value{kk,chanIdx};
            varEIRP= netcdf.inqVarID(coinNcids{kk}(chanIdx,1), 'EIRP');
            EIRP(chanIdx,:) = netcdf.getVar(coinNcids{kk}(chanIdx,1), varEIRP, 'double');
            varDDM= netcdf.inqVarID(coinNcids{kk}(chanIdx,1), 'DDMOutputNumericalScaling');
            DDM(chanIdx,:) = netcdf.getVar(coinNcids{kk}(chanIdx,1), varDDM, 'double');
        end

        RC_spLR(:)=ReflectionCoefficientAtSP(1,:);
        RC_spRR(:)=ReflectionCoefficientAtSP(2,:);
        SNR_spLR(:)=DDMSNRAtSP(1,:);
        SNR_spRR(:)=DDMSNRAtSP(2,:);
        AGSP_LR(:)=LowAGSP{kk,1}(:);
        AGSP_RR(:)=LowAGSP{kk,2}(:);
        LSNR_LR(:)=LowSNR{kk,1}(:);
        LSNR_RR(:)=LowSNR{kk,2}(:);
        VLSNR_LR(:)=VeryLowSNR{kk,1}(:);
        VLSNR_RR(:)=VeryLowSNR{kk,2}(:);

        DDM_L(:)=DDM(1,:);
        DDM_R(:)=DDM(2,:);
        EIRP_L(:)=EIRP(1,:);
        EIRP_R(:)=EIRP(2,:);

        clear DDM_NumScal ReflectionCoefficientAtSP DDM EIRP DDMSNRAtSP

        nPS=size(RC_spLR,2);
        for k=1:nPS
            L_RC_TOT=[L_RC_TOT;RC_spLR(:,k)];
            R_RC_TOT=[R_RC_TOT;RC_spRR(:,k)];
            L_SNR_TOT=[L_SNR_TOT;SNR_spLR(:,k)];
            R_SNR_TOT=[R_SNR_TOT;SNR_spRR(:,k)];
            TidOrbit_TOT=[TidOrbit_TOT;TrackIDOrbitL1B];
            spLAT_TOT=[spLAT_TOT;SpecularPointLat(k,:)];
            spLON_TOT=[spLON_TOT;SpecularPointLon(k,:)];
            IntMidPTime_TOT=[IntMidPTime_TOT;IntegrationMidPointTime(k,:)];
            L_AGSP_TOT=[L_AGSP_TOT;AGSP_LR(:,k)];
            R_AGSP_TOT=[R_AGSP_TOT;AGSP_RR(:,k)];
            L_LowSNR_TOT=[L_LowSNR_TOT;LSNR_LR(:,k)];
            R_LowSNR_TOT=[R_LowSNR_TOT;LSNR_RR(:,k)];
            L_VLowSNR_TOT=[L_VLowSNR_TOT;VLSNR_LR(:,k)];
            R_VLowSNR_TOT=[R_VLowSNR_TOT;VLSNR_RR(:,k)];

            L_DDM_TOT=[L_DDM_TOT;DDM_L(:,k)];
            R_DDM_TOT=[R_DDM_TOT;DDM_R(:,k)];
            L_EIRP_TOT=[L_EIRP_TOT;EIRP_L(:,k)];
            R_EIRP_TOT=[R_EIRP_TOT;EIRP_R(:,k)];
        end
        clear RC_spLR RC_spRR TrackIDL1B TrackIDOrbitL1B SpecularPointLat ...
            SpecularPointLon IntegrationMidPointTime DDM_L DDM_R EIRP_L EIRP_R ...
            AGSP_LR AGSP_RR LSNR_LR LSNR_RR VLSNR_LR VLSNR_RR SNR_spLR SNR_spRR
    end

    netcdf.close(ncid)
    clear   LowAGSP LowSNR VeryLowSNR
end

fclose('all');

%% HSAVERS SIMULATIONS

SPLat=inOutReferenceFile(1).geoSYSp.SPlat_series;
SPLon=inOutReferenceFile(1).geoSYSp.SPlon_series;

for irun=1:Nrun
    gamma_LR(irun,:)=inOutReferenceFile(irun).max_reflectivity_noNoise_LR_dB;
    gamma_RR(irun,:)=inOutReferenceFile(irun).max_reflectivity_noNoise_RR_dB;
    Tid(irun,:)=inOutReferenceFile(irun).TrackID;
end

%%
% %% LANDCOVER MAP
sizeInputMapWindow=inOutReferenceFile(1).DEMinfo.sizeInputMapWindow;
SP_lla_onEllipsoid(:,1)=SPLat;
SP_lla_onEllipsoid(:,2)=SPLon;

coverMapFilename= [dataRoot '\AuxiliaryFiles\LandCoverMap\ESACCI-LC-L4-LCCS-Map-300m-P1Y-2015-v2.0.7b.nc'];
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

%% HSAVERS DATA & L1B PROCESSOR OUTPUT
count_comp=0;
for irun=1:Nrun
    for ips=1:length(SPLat)
        for imeta=1:length(TidOrbit_TOT)
            %             if Tid(irun,ips)==TidOrbit_TOT(imeta) && SPLat(ips)<=IMPTime_TOT(imeta)
            if Tid(irun,ips)==TidOrbit_TOT(imeta) && SPLat(ips)<=spLAT_TOT(imeta)+0.00005 && SPLat(ips)>=spLAT_TOT(imeta)-0.00005 && SPLon(ips)<=spLON_TOT(imeta)+0.00005  && SPLon(ips)>=spLON_TOT(imeta)-0.00005
                count_comp=count_comp+1;
                Tracknumb(count_comp,1)=Tid(irun,ips);
                Tracknumb(count_comp,2)=TidOrbit_TOT(imeta);
                compL(count_comp,1)=gamma_LR(irun,ips);
                compL(count_comp,2)=L_RC_TOT(imeta);
                compL(count_comp,3)=L_AGSP_TOT(imeta);
                compL(count_comp,4)=L_LowSNR_TOT(imeta);
                compL(count_comp,5)=L_VLowSNR_TOT(imeta);
                compL(count_comp,6)=L_SNR_TOT(imeta);
                compR(count_comp,1)=gamma_RR(irun,ips);
                compR(count_comp,2)=R_RC_TOT(imeta);
                compR(count_comp,3)=R_AGSP_TOT(imeta);
                compR(count_comp,4)=R_LowSNR_TOT(imeta);
                compR(count_comp,5)=R_VLowSNR_TOT(imeta);
                compR(count_comp,6)=R_SNR_TOT(imeta);

                LAT(count_comp,1)=SPLat(ips);
                LAT(count_comp,2)=spLAT_TOT(imeta);
                LON(count_comp,1)=SPLon(ips);
                LON(count_comp,2)=spLON_TOT(imeta);

                %                 compL(imeta,3)=L_DDM_TOT(imeta);
            end
        end
    end
end

%LR
R_matrixL = corrcoef(compL(:,1),compL(:,2));
RL=R_matrixL(1,2);
RMSEL = sqrt(mean((compL(:,1)-compL(:,2)).^2));
BIAS_L = mean(compL(:,1)-compL(:,2));
UB_RMSEL=sqrt(RMSEL^2-BIAS_L^2);

[PL SL]  = polyfit(compL(:,1),compL(:,2),1);
[y_fitL,deltaL] = polyval(PL,compL(:,1),SL);
slopeL = PL(1);
[~, index]=sort(y_fitL,'ascend');

%RR
R_matrixR = corrcoef(compR(:,1),compR(:,2));
RR=R_matrixR(1,2);
RMSER = sqrt(mean((compR(:,1)-compR(:,2)).^2));
BIAS_R = mean(compR(:,1)-compR(:,2));
UB_RMSER=sqrt(RMSER^2-BIAS_R^2);
[PR SR]  = polyfit(compR(:,1),compR(:,2),1);
[y_fitR,deltaR] = polyval(PR,compR(:,1),SR);
slopeR = PR(1);
[~, indexR]=sort(y_fitR,'ascend');

runDate=datestr(now);
runDate([12,15,18])='_';

fig2=figure;
plot(compL(:,1),compL(:,2),'o','MarkerEdgeColor','#0072BD','MarkerFaceColor','#0072BD')
hold on
ax=gca;
h3=plot([ax.XLim(1) ax.XLim(2)],[ax.XLim(1) ax.XLim(2)],'k');
grid on
xlabel('Simulated Reflectivity [dB]')
ylabel('L1b Calibrated Reflectivity [dB]')
hold on
h1=plot(compL(index,1),y_fitL(index),'r');
hold on
h2=plot(compL(index,1),y_fitL(index)+2*deltaL(index),'b') ;
hold on
plot(compL(index,1),y_fitL(index)-2*deltaL(index),'b');
legend([h1 h2 h3],{'linear fit','95% confidence','1:1 line'},'Location','best')
title({[FreqL1B(1,1:3) ' ' FreqL1B(1,5:6) ' ' PolL1B(1,:)];  ['R=',num2str(round(RL,2)), '  RMSE=' num2str(round(RMSEL,2)) 'dB,  UnB RMSE= ' num2str(round(UB_RMSEL,2))  'dB,  slope=' num2str(round(slopeL,2))]})

compLnoAGSP=compL;
compLAGSP=[];
ind=find(compLnoAGSP(:,3) == 1);
compLnoAGSP(ind,:)=[];
compLAGSP=compL(ind,:);

fig20=figure;
plot(compLnoAGSP(:,1),compLnoAGSP(:,2),'bo','MarkerFaceColor','b');
hold on, L= plot(compLAGSP(:,1),compLAGSP(:,2),'ko','MarkerFaceColor','k');
if isempty(L)
    hold on, L= plot(nan, nan, 'ko','MarkerFaceColor','k');
end
hold on
ax=gca;
h3=plot([ax.XLim(1) ax.XLim(2)],[ax.XLim(1) ax.XLim(2)],'k');
grid on
xlabel('Simulated Reflectivity [dB]')
ylabel('L1b Calibrated Reflectivity [dB]')

R_matrix = corrcoef(compLnoAGSP(:,1),compLnoAGSP(:,2));
RAGSP=R_matrix(1,2);
RMSE = sqrt(mean((compLnoAGSP(:,1)-compLnoAGSP(:,2)).^2));
BIAS = mean(compLnoAGSP(:,1)-compLnoAGSP(:,2));
UB_RMSE=sqrt(RMSE^2-BIAS^2);
[P S]  = polyfit(compLnoAGSP(:,1),compLnoAGSP(:,2),1);
[y_fit,delta] = polyval(P,compLnoAGSP(:,1),S);
slope = P(1);
[~, index]=sort(y_fit,'ascend');
hold on
hold on
h1=plot(compLnoAGSP(index,1),y_fit(index),'r');
hold on
h2=plot(compLnoAGSP(index,1),y_fit(index)+2*delta(index),'b') ;
hold on
plot(compLnoAGSP(index,1),y_fit(index)-2*delta(index),'b');
legend([L h3 h1 h2],{'LowAGSP','1:1 line','linear fit','95% confidence'},'Location','best')
title({[FreqL1B(1,1:3) ' ' FreqL1B(1,5:6) ' ' PolL1B(1,:)];  ['R=',num2str(round(RAGSP,2)), '  RMSE=' num2str(round(RMSE,2)) 'dB,  UnB RMSE= ' num2str(round(UB_RMSE,2))  'dB,  slope=' num2str(round(slope,2))]})

compNoLowSNR=compL;
compLowSNR=[];
ind=find(compNoLowSNR(:,4) == 1);
compNoLowSNR(ind,:)=[];
compLowSNR=compL(ind,:);

fig21=figure;
plot(compNoLowSNR(:,1),compNoLowSNR(:,2),'bo','MarkerFaceColor','b')
hold on, L= plot(compLowSNR(:,1),compLowSNR(:,2),'ko','MarkerFaceColor','k');
if isempty(L)
    hold on, L= plot(nan, nan, 'ko','MarkerFaceColor','k');
end
hold on
ax=gca;
h3=plot([ax.XLim(1) ax.XLim(2)],[ax.XLim(1) ax.XLim(2)],'k');
grid on
xlabel('Simulated Reflectivity [dB]')
ylabel('L1b Calibrated Reflectivity [dB]')
R_matrix = corrcoef(compNoLowSNR(:,1),compNoLowSNR(:,2));
RLowSNR=R_matrix(1,2);
RMSE = sqrt(mean((compNoLowSNR(:,1)-compNoLowSNR(:,2)).^2));
BIAS = mean(compNoLowSNR(:,1)-compNoLowSNR(:,2));
UB_RMSE=sqrt(RMSE^2-BIAS^2);
[P S]  = polyfit(compNoLowSNR(:,1),compNoLowSNR(:,2),1);
[y_fit,delta] = polyval(P,compNoLowSNR(:,1),S);
slope = P(1);
[~, index]=sort(y_fit,'ascend');
hold on
h1=plot(compNoLowSNR(index,1),y_fit(index),'r');
hold on
h2=plot(compNoLowSNR(index,1),y_fit(index)+2*delta(index),'b') ;
hold on
plot(compNoLowSNR(index,1),y_fit(index)-2*delta(index),'b');
legend([L h3 h1 h2],{'LowSNR','1:1 line','linear fit','95% confidence'},'Location','best')
title({[FreqL1B(1,1:3) ' ' FreqL1B(1,5:6) ' ' PolL1B(1,:)];  ['R=',num2str(round(RLowSNR,2)), '  RMSE=' num2str(round(RMSE,2)) 'dB,  UnB RMSE= ' num2str(round(UB_RMSE,2))  'dB,  slope=' num2str(round(slope,2))]})

compNoVLowSNR=compL;
compVLowSNR=[];
ind=find(compNoVLowSNR(:,5) == 1);
compNoVLowSNR(ind,:)=[];
compVLowSNR=compL(ind,:);

fig22=figure;
plot(compNoVLowSNR(:,1),compNoVLowSNR(:,2),'bo','MarkerFaceColor','b')
hold on, L= plot(compVLowSNR(:,1),compVLowSNR(:,2),'ko','MarkerFaceColor','k');
if isempty(L)
    hold on, L= plot(nan, nan, 'ko','MarkerFaceColor','k');
end
hold on
ax=gca;
h3=plot([ax.XLim(1) ax.XLim(2)],[ax.XLim(1) ax.XLim(2)],'k');
grid on
xlabel('Simulated Reflectivity [dB]')
ylabel('L1b Calibrated Reflectivity [dB]')

R_matrix = corrcoef(compNoVLowSNR(:,1),compNoVLowSNR(:,2));
RVLowSNR=R_matrix(1,2);
RMSE = sqrt(mean((compNoVLowSNR(:,1)-compNoVLowSNR(:,2)).^2));
BIAS = mean(compNoVLowSNR(:,1)-compNoVLowSNR(:,2));
UB_RMSE=sqrt(RMSE^2-BIAS^2);
[P S]  = polyfit(compNoVLowSNR(:,1),compNoVLowSNR(:,2),1);
[y_fit,delta] = polyval(P,compNoVLowSNR(:,1),S);
slope = P(1);
[~, index]=sort(y_fit,'ascend');
hold on
h1=plot(compNoVLowSNR(index,1),y_fit(index),'r');
hold on
h2=plot(compNoVLowSNR(index,1),y_fit(index)+2*delta(index),'b') ;
hold on
plot(compNoVLowSNR(index,1),y_fit(index)-2*delta(index),'b');
legend([L h3 h1 h2],{'VeryLowSNR','1:1 line','linear fit','95% confidence'},'Location','best')
title({[FreqL1B(1,1:3) ' ' FreqL1B(1,5:6) ' ' PolL1B(1,:)];  ['R=',num2str(round(RVLowSNR,2)), '  RMSE=' num2str(round(RMSE,2)) 'dB,  UnB RMSE= ' num2str(round(UB_RMSE,2))  'dB,  slope=' num2str(round(slope,2))]})

fig23=figure;
scatter(compL(:,1),compL(:,2),[],compL(:,6),'filled'),colorbar;
hold on
ax=gca;
h3=plot([ax.XLim(1) ax.XLim(2)],[ax.XLim(1) ax.XLim(2)],'k');
grid on
xlabel('Simulated Reflectivity [dB]')
ylabel('L1b Calibrated Reflectivity [dB]')
hcb = colorbar;
hcb.Title.String = "SNR [dB]";
title([FreqL1B(1,1:3) ' ' FreqL1B(1,5:6) ' ' PolL1B(1,:)])

fig3=figure;
plot(compR(:,1),compR(:,2),'o','MarkerEdgeColor','#0072BD','MarkerFaceColor','#0072BD')
grid on
hold on
ax=gca;
h3=plot([ax.XLim(1) ax.XLim(2)],[ax.XLim(1) ax.XLim(2)],'k');
xlabel('Simulated Reflectivity [dB]')
ylabel('L1b Calibrated Reflectivity [dB]')
hold on

h1=plot(compR(indexR,1),y_fitR(indexR),'r');
hold on
h2=plot(compR(indexR,1),y_fitR(indexR)+2*deltaR(indexR),'b');
hold on
plot(compR(indexR,1),y_fitR(indexR)-2*deltaR(indexR),'b');
legend([h1 h2 h3],{'linear fit','95% confidence','1:1 line'},'Location','best')
title({[FreqL1B(2,1:3) ' ' FreqL1B(2,5:6) ' ' PolL1B(2,:)];  ['R=',num2str(round(RR,2)), '  RMSE=' num2str(round(RMSER,2)) 'dB,  UnB RMSE=' num2str(round(UB_RMSER,2))  'dB,  slope=' num2str(round(slopeR,2))]})

saveas(fig20,[ref_outpath referenceFile(1:end-4) '_' runDate '_L1B_LR_AGSP.jpg'])
saveas(fig20,[ref_outpath referenceFile(1:end-4) '_' runDate '_L1B_LR_AGSP.fig'])
saveas(fig21,[ref_outpath referenceFile(1:end-4) '_' runDate '_L1B_LR_LowSNR.jpg'])
saveas(fig21,[ref_outpath referenceFile(1:end-4) '_' runDate '_L1B_LR_LowSNR.fig'])
saveas(fig22,[ref_outpath referenceFile(1:end-4) '_' runDate '_L1B_LR_VeryLowSNR.jpg'])
saveas(fig22,[ref_outpath referenceFile(1:end-4) '_' runDate '_L1B_LR_VeryLowSNR.fig'])
saveas(fig23,[ref_outpath referenceFile(1:end-4) '_' runDate '_L1B_LR_SNR.jpg'])
saveas(fig23,[ref_outpath referenceFile(1:end-4) '_' runDate '_L1B_LR_SNR.fig'])
saveas(fig2,[ref_outpath referenceFile(1:end-4) '_' runDate '_L1B_LR.jpg'])
saveas(fig2,[ref_outpath referenceFile(1:end-4) '_' runDate '_L1B_LR.fig'])
saveas(fig3,[ref_outpath referenceFile(1:end-4) '_' runDate '_L1B_RR.jpg'])
saveas(fig3,[ref_outpath referenceFile(1:end-4) '_' runDate '_L1B_RR.fig'])
saveas(fig1,[ref_outpath referenceFile(1:end-4) '_' runDate '_cover_map.jpg'])
saveas(fig1,[ref_outpath referenceFile(1:end-4) '_' runDate '_cover_map.fig'])

fid1 = fopen([ref_outpath referenceFile(1:end-4) '_' runDate '_L1B.txt'],'wt');
fprintf(fid1,'%s\n',[FreqL1B(1,:) ' ' PolL1B(1,:) ' R=',num2str(round(RL,2)), '  RMSE=' num2str(round(RMSEL,2)) 'dB,  UnB RMSE=' num2str(round(UB_RMSEL,2))  'dB,  slope=' num2str(round(slopeL,2))]);
fprintf(fid1,'%s\n',[FreqL1B(2,:) ' ' PolL1B(2,:) ' R=',num2str(round(RR,2)), '  RMSE=' num2str(round(RMSER,2)) 'dB,  UnB RMSE=' num2str(round(UB_RMSER,2))  'dB,  slope=' num2str(round(slopeR,2))]);
fclose(fid1);

rmdir(temppath,'s')
end