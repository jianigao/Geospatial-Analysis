import pandas as pd
import geopandas as gpd

import folium
from folium import Choropleth, Circle, Marker
from folium.plugins import HeatMap, MarkerCluster

# Ensure that the maps are visible in all web browsers
def embed_map(m, file_name):
    from IPython.display import IFrame
    m.save(file_name)
    return IFrame(file_name, width='100%', height='500px')


# Do earthquakes coincide with plate boundaries?
plate_boundaries = gpd.read_file("../input/geospatial-learn-course-data/Plate_Boundaries/Plate_Boundaries/Plate_Boundaries.shp")
plate_boundaries['coordinates'] = plate_boundaries.apply(lambda x: [(b,a) for (a,b) in list(x.geometry.coords)], axis='columns')
plate_boundaries.drop('geometry', axis=1, inplace=True)
plate_boundaries.head()

# Load the data and print the first 5 rows
earthquakes = pd.read_csv("../input/geospatial-learn-course-data/earthquakes1970-2014.csv", parse_dates=["DateTime"])
earthquakes.head()

# Create a base map with plate boundaries
m_1 = folium.Map(location=[35,136], tiles='cartodbpositron', zoom_start=5)
for i in range(len(plate_boundaries)):
    folium.PolyLine(locations=plate_boundaries.coordinates.iloc[i], weight=2, color='black').add_to(m_1)

# Add a heatmap to the map
HeatMap(data=earthquakes[['Latitude', 'Longitude']], radius=15).add_to(m_1)

# Show the map
embed_map(m_1, 'q_1.html')


# Is there a relationship between earthquake depth and proximity to a plate boundary in Japan?
# Create a base map with plate boundaries
m_2 = folium.Map(location=[35,136], tiles='cartodbpositron', zoom_start=5)
for i in range(len(plate_boundaries)):
    folium.PolyLine(locations=plate_boundaries.coordinates.iloc[i], weight=2, color='black').add_to(m_2)
    
# Add a map to visualize earthquake depth
# Custom function to assign a color to each circle
def color_producer(val):
    if val < 50:
        return 'forestgreen'
    elif val < 100:
        return 'darkorange'
    else:
        return 'darkred'

# Add a map to visualize earthquake depth
for i in range(0,len(earthquakes)):
    folium.Circle(
        location=[earthquakes.iloc[i]['Latitude'], earthquakes.iloc[i]['Longitude']],
        radius=2000,
        color=color_producer(earthquakes.iloc[i]['Depth'])).add_to(m_2)

# View the map
embed_map(m_2, 'q_2.html')


# Which prefectures have high population density?
# GeoDataFrame with prefecture boundaries
prefectures = gpd.read_file("../input/geospatial-learn-course-data/japan-prefecture-boundaries/japan-prefecture-boundaries/japan-prefecture-boundaries.shp")
prefectures.set_index('prefecture', inplace=True)
prefectures.head()

# DataFrame containing population of each prefecture
population = pd.read_csv("../input/geospatial-learn-course-data/japan-prefecture-population.csv")
population.set_index('prefecture', inplace=True)

# Calculate area (in square kilometers) of each prefecture
area_sqkm = pd.Series(prefectures.geometry.to_crs(epsg=32654).area / 10**6, name='area_sqkm')
stats = population.join(area_sqkm)

# Add density (per square kilometer) of each prefecture
stats['density'] = stats["population"] / stats["area_sqkm"]
stats.head()

# Create a base map
m_3 = folium.Map(location=[35,136], tiles='cartodbpositron', zoom_start=5)

# Create a choropleth map to visualize population density
Choropleth(geo_data=prefectures['geometry'].__geo_interface__,
           data=stats['density'],
           key_on="feature.id",
           fill_color='YlGnBu',
           legend_name='Population density (per square kilometer)'
          ).add_to(m_3)

# View the map
embed_map(m_3, 'q_3.html')


# Which high-density prefecture is prone to high-magnitude earthquakes?
# Create a base map
m_4 = folium.Map(location=[35,136], tiles='cartodbpositron', zoom_start=5)

# Create a map
def color_producer(magnitude):
    if magnitude > 6.5:
        return 'red'
    else:
        return 'green'

Choropleth(
    geo_data=prefectures['geometry'].__geo_interface__,
    data=stats['density'],
    key_on="feature.id",
    fill_color='BuPu',
    legend_name='Population density (per square kilometer)').add_to(m_4)

for i in range(0,len(earthquakes)):
    folium.Circle(
        location=[earthquakes.iloc[i]['Latitude'], earthquakes.iloc[i]['Longitude']],
        popup=("{} ({})").format(
            earthquakes.iloc[i]['Magnitude'],
            earthquakes.iloc[i]['DateTime'].year),
        radius=earthquakes.iloc[i]['Magnitude']**5.5,
        color=color_producer(earthquakes.iloc[i]['Magnitude'])).add_to(m_4)

# View the map
embed_map(m_4, 'q_4.html')

################################################################################

# Create a map
m_1 = folium.Map(location=[42.32,-71.0589], tiles='openstreetmap', zoom_start=10)
# latitude (42.32° N) and longitude (-71.0589° E)

# Display the map
m_1


daytime_robberies = crimes[((crimes.OFFENSE_CODE_GROUP == 'Robbery') & \
                            (crimes.HOUR.isin(range(9,18))))]

# Create a map
m_2 = folium.Map(location=[42.32,-71.0589], tiles='cartodbpositron', zoom_start=13)

# Add points to the map
for idx, row in daytime_robberies.iterrows():
    Marker([row['Lat'], row['Long']]).add_to(m_2)

# Display the map
m_2


# Create the map
m_3 = folium.Map(location=[42.32,-71.0589], tiles='cartodbpositron', zoom_start=13)

# Add points to the map
mc = MarkerCluster() # if we have a lot of markers to add
for idx, row in daytime_robberies.iterrows():
    if not math.isnan(row['Long']) and not math.isnan(row['Lat']):
        mc.add_child(Marker([row['Lat'], row['Long']]))
m_3.add_child(mc)

# Display the map
m_3


# Create a base map
m_4 = folium.Map(location=[42.32,-71.0589], tiles='cartodbpositron', zoom_start=13)

def color_producer(val):
    if val <= 12:
        return 'forestgreen'
    else:
        return 'darkred'

# Add a bubble map to the base map # uses circles instead of markers
for i in range(0,len(daytime_robberies)):
    Circle(
        location=[daytime_robberies.iloc[i]['Lat'], daytime_robberies.iloc[i]['Long']],
        radius=20,
        color=color_producer(daytime_robberies.iloc[i]['HOUR'])).add_to(m_4)

# Display the map
m_4


# Create a base map
m_5 = folium.Map(location=[42.32,-71.0589], tiles='cartodbpositron', zoom_start=12)

# Add a heatmap to the base map
# shows the density of crime in different areas of the city,
# where red areas have relatively more criminal incidents.
HeatMap(data=crimes[['Lat', 'Long']], radius=10).add_to(m_5)

# Display the map
m_5


# GeoDataFrame with geographical boundaries of Boston police districts
districts_full = gpd.read_file('../input/geospatial-learn-course-data/Police_Districts/Police_Districts/Police_Districts.shp')
districts = districts_full[["DISTRICT", "geometry"]].set_index("DISTRICT")
districts.head()

# Number of crimes in each police district
plot_dict = crimes.DISTRICT.value_counts()
plot_dict.head()

# Create a base map
m_6 = folium.Map(location=[42.32,-71.0589], tiles='cartodbpositron', zoom_start=12)

# Add a choropleth map to the base map # to understand how crime varies by police district
Choropleth(geo_data=districts.__geo_interface__, 
           data=plot_dict, 
           key_on="feature.id", 
           fill_color='YlGnBu', 
           legend_name='Major criminal incidents (Jan-Aug 2018)'
          ).add_to(m_6)

# Display the map
m_6
