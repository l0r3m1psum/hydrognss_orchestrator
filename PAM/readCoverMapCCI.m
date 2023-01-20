%% Name: readCoverMapCCI
%% Author: L. Dente, Tor Vergata University of Rome
%% Last update: Dec 2021
%%
%% This function allows to open the ESA CCI land cover map, in netcdf format,
%% and to read only a specific area of the image defined
%% by the min and max coordinates of the SPs plus 3.5°.
%% The size of area to cover the complete track of SP  and to be larger than that
%% The area should cover the integration area of all the SPs.
%% The land cover is simplified to include only a limited number of classes.
%%
%% Input:
%% ESA CCI land cover map filename (file format netcdf)
%% SP_lla_onEllipsoid (3,n): lat,lon,elev for all n SPs of the track
%%
%% Output:
%% landCoverMap: (:,:,1)=latitude; (:,:,2)=longitude; (:,:,3)=land cover index
%%
%% Subroutines: 
%% ------------------------------------------------------------------------


function [landCoverMap,dominantClass_ID]=readCoverMapCCI(coverMapFilename, SP_lla_onEllipsoid,sizeInputMapWindow)

%define the area to be read in the file
maxLatArea=max(SP_lla_onEllipsoid(:,1))+sizeInputMapWindow;
minLatArea=min(SP_lla_onEllipsoid(:,1))-sizeInputMapWindow;
maxLonArea=max(SP_lla_onEllipsoid(:,2))+sizeInputMapWindow;
minLonArea=min(SP_lla_onEllipsoid(:,2))-sizeInputMapWindow;
%look for the indexes in the file,, corresponding to the area to be read
latLandCoverMap=ncread(coverMapFilename, 'lat');
lonLandCoverMap=ncread(coverMapFilename, 'lon');
indexLatstartLC = find(latLandCoverMap<=maxLatArea,1, 'first');
indexLatendLC = find(latLandCoverMap<=minLatArea,1, 'first');
indexLonstartLC = find(lonLandCoverMap>=minLonArea,1, 'first');
indexLonendLC = find(lonLandCoverMap>=maxLonArea,1, 'first');
countLatLC=indexLatendLC-indexLatstartLC+1;
countLonLC=indexLonendLC-indexLonstartLC+1;
latLandCover_res=latLandCoverMap(indexLatstartLC:indexLatendLC);
lonLandCover_res=lonLandCoverMap(indexLonstartLC:indexLonendLC);
%define the coordinate matrixes of the land cover map
landCoverMap(:,:,1)=repmat(latLandCover_res,1,length(lonLandCover_res)); %lat matrix
landCoverMap(:,:,2)=repmat(lonLandCover_res',length(latLandCover_res),1); %lon matrix
%read the land cover map of the selected region
coverMapOrig = ncread(coverMapFilename,'lccs_class',[indexLonstartLC indexLatstartLC],[countLonLC countLatLC])';

%% simplify the land cover map to a limited number of classes
% 0 water bodies
% 1 broadleaved forest
% 2 needleleaved forest
% 3 cropland/grassland/shrubland
% 4 bare soils
% 5 flooded forest
% 6 flooded shurbland
% 7 permanent ice (not included in the map, ice is conseidere bare soil)

coverMapOrig(coverMapOrig==0)=4;
coverMapOrig(coverMapOrig==10)=3;
coverMapOrig(coverMapOrig==11)=3;
coverMapOrig(coverMapOrig==12)=3;
coverMapOrig(coverMapOrig==20)=3;
coverMapOrig(coverMapOrig==30)=3;
coverMapOrig(coverMapOrig==40)=3;
coverMapOrig(coverMapOrig==50)=1;
coverMapOrig(coverMapOrig==60)=1;
coverMapOrig(coverMapOrig==61)=1;
coverMapOrig(coverMapOrig==62)=1;
coverMapOrig(coverMapOrig==70)=2;
coverMapOrig(coverMapOrig==71)=2;
coverMapOrig(coverMapOrig==72)=2;
coverMapOrig(coverMapOrig==80)=2;
coverMapOrig(coverMapOrig==81)=2;
coverMapOrig(coverMapOrig==82)=2;
coverMapOrig(coverMapOrig==90)=1;
coverMapOrig(coverMapOrig==100)=1;
coverMapOrig(coverMapOrig==110)=3;
coverMapOrig(coverMapOrig==120)=3;
coverMapOrig(coverMapOrig==121)=3;
coverMapOrig(coverMapOrig==122)=3;
coverMapOrig(coverMapOrig==-126)=3;
coverMapOrig(coverMapOrig==-116)=4;
coverMapOrig(coverMapOrig==-106)=4;
coverMapOrig(coverMapOrig==-105)=4;
coverMapOrig(coverMapOrig==-104)=4;
coverMapOrig(coverMapOrig==-103)=4;
coverMapOrig(coverMapOrig==-96)=5;
coverMapOrig(coverMapOrig==-86)=5;
coverMapOrig(coverMapOrig==-76)=6;
coverMapOrig(coverMapOrig==-66)=4;
coverMapOrig(coverMapOrig==-56)=4;
coverMapOrig(coverMapOrig==-55)=4;
coverMapOrig(coverMapOrig==-54)=4;
coverMapOrig(coverMapOrig==-46)=0;
coverMapOrig(coverMapOrig==-36)=4;

%number of classes in the study area
coverMap_IDs=unique(coverMapOrig);
totNumOfCoverages=size(coverMap_IDs,1);
for l=1:totNumOfCoverages
    percentCoverageOfAclass(l)=length(coverMapOrig(coverMapOrig==coverMap_IDs(l)))/numel(coverMapOrig)*100;
end
maxPercentCoverageOfAclass=max(percentCoverageOfAclass);
dominantClass_ID=coverMap_IDs(percentCoverageOfAclass==maxPercentCoverageOfAclass);
for l=1:totNumOfCoverages
    if coverMap_IDs(l)~=0 && percentCoverageOfAclass(l)<0.1
        coverMapOrig(coverMapOrig==coverMap_IDs(l))=dominantClass_ID;
    end
    if coverMap_IDs(l)==0 && percentCoverageOfAclass(l)<0.01
        coverMapOrig(coverMapOrig==coverMap_IDs(l))=dominantClass_ID;
    end    
end

landCoverMap(:,:,3)=coverMapOrig;

%show land cover map in lat-lon

% mapOfColorCover=[0 0 1;0 1 0;1 0 1;0 1 1;1 0 0;1 1 0;0 0 0];

% %show land cover map in lat-lon
% 
% %plot the SPs over the land cover
% 
% figure('Name', 'Land cover map', 'NumberTitle','off','OuterPosition', [50 50 700 510]);
% subplot('Position', [0.1 0.12 0.65 0.82]);
% mapshow(landCoverMap(:,:,2),landCoverMap(:,:,1),landCoverMap(:,:,3), 'DisplayType', 'texturemap')
% % axis([minLonArea maxLonArea minLatArea maxLatArea])
% colormap(mapOfColorCover)
% colorbar('Ticks',[0,1,2,3,4,5,6],'TickLabels',{'0 water bodies','1 broadleaved forest','2 needleleaved forest','3 cropland/grassland/shrubland','4 bare areas','5 flooded forest','6 flooded shrubland'})
% caxis([0 6])
% title('Land cover map')
% xlabel('Longitude (deg)')
% ylabel('Latitude (deg)')

end