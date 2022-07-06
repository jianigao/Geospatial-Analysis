import pandas as pd
import geopandas as gpd

from shapely.geometry import LineString

# Load a DataFrame and print the first 5 rows
birds_df = pd.read_csv("../input/geospatial-learn-course-data/purple_martin.csv", parse_dates=['timestamp'])
print("There are {} different birds in the dataset.".format(birds_df["tag-local-identifier"].nunique()))
birds_df.head()

# Convert the DataFrame to a GeoDataFrame
birds = gpd.GeoDataFrame(birds_df, geometry=gpd.points_from_xy(birds_df["location-long"], birds_df["location-lat"]))

# When creating a GeoDataFrame from a CSV file,
# coordinate reference system (CRS) to EPSG 4326
birds.crs = {'init': 'epsg:4326'}

# Load a GeoDataFrame with country boundaries in North/South America, print the first 5 rows
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
americas = world.loc[world['continent'].isin(['North America', 'South America'])]
americas.head()
print(americas.crs)
# show epsg of americas

# Create a map
ax = americas.plot(figsize=(10,10), color='white', linestyle=':', edgecolor='gray')
birds.plot(ax=ax, markersize=10)
# birds.to_crs(epsg=4326).plot(ax=ax, markersize=10)
# birds.to_crs(epsg=32630).plot(ax=ax, markersize=10)
# When plotting multiple GeoDataFrames,it's important that they all use the same CRS.

# In case the EPSG code is not available in GeoPandas
# Change the CRS to EPSG 4326 in this way
birds.to_crs("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")

# Zoom in
ax.set_xlim([-110, -30])
ax.set_ylim([-30, 60])

# Where does each bird start and end its journey? 
# GeoDataFrame showing path for each bird
path_df = birds.groupby("tag-local-identifier")['geometry'].apply(list).apply(lambda x: LineString(x)).reset_index()
path_gdf = gpd.GeoDataFrame(path_df, geometry=path_df.geometry)
path_gdf.crs = {'init' :'epsg:4326'}

# GeoDataFrame showing starting point for each bird
start_df = birds.groupby("tag-local-identifier")['geometry'].apply(list).apply(lambda x: x[0]).reset_index()
start_gdf = gpd.GeoDataFrame(start_df, geometry=start_df.geometry)
start_gdf.crs = {'init' :'epsg:4326'}

# Show first five rows of GeoDataFrame
start_gdf.head()

# GeoDataFrame showing path for each bird
end_df = birds.groupby("tag-local-identifier")['geometry'].apply(list).apply(lambda x: x[-1]).reset_index()
end_gdf = gpd.GeoDataFrame(end_df, geometry=end_df.geometry)
end_gdf.crs = {'init' :'epsg:4326'}

ax = americas.plot(figsize=(10, 10), color='white', linestyle=':', edgecolor='gray')

start_gdf.plot(ax=ax, color='red',  markersize=30)
path_gdf.plot(ax=ax, cmap='tab20b', linestyle='-', linewidth=1, zorder=1)
end_gdf.plot(ax=ax, color='black', markersize=30)

# Where are the protected areas in South America?
# Path of the shapefile to load
protected_filepath = "../input/geospatial-learn-course-data/SAPA_Aug2019-shapefile/SAPA_Aug2019-shapefile/SAPA_Aug2019-shapefile-polygons.shp"

protected_areas = gpd.read_file(protected_filepath)

# Country boundaries in South America
south_america = americas.loc[americas['continent']=='South America']

# Plot protected areas in South America
ax = south_america.plot(figsize=(10,10), color='white', edgecolor='gray')
protected_areas.plot(ax=ax, alpha=0.4)

# What percentage of South America is protected?
P_Area = sum(protected_areas['REP_AREA']-protected_areas['REP_M_AREA'])
print("South America has {} square kilometers of protected areas.".format(P_Area))

south_america.head()

# Types in "geometry" column
##a Point for the epicenter of an earthquake,
##a LineString for a street, or
##a Polygon to show country boundaries.

# Get the x-coordinate of each point
south_america.geometry.head().x

# Calculate the area (in square meters) of each polygon in the GeoDataFrame 
south_america.loc[:, "AREA"] = south_america.geometry.to_crs(epsg=3035).area / 10**6
print('Total area is {}.'.format(south_america.AREA.sum()))

# Calculate the total area of South America (in square kilometers)
totalArea = sum(south_america.geometry.to_crs(epsg=3035).area) / 10**6

# What percentage of South America is protected?
percentage_protected = P_Area/totalArea
print('Approximately {}% of South America is protected.'.format(round(percentage_protected*100, 2)))

# Where are the birds in South America?
ax = south_america.plot(figsize=(10,10), color='white', edgecolor='gray')
protected_areas[protected_areas['MARINE']!='2'].plot(ax=ax, alpha=0.4, zorder=1)
birds[birds.geometry.y < 0].plot(ax=ax, color='red', alpha=0.6, markersize=10, zorder=2)
