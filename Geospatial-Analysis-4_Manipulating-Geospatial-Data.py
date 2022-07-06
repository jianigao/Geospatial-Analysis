import math
import pandas as pd
import geopandas as gpd
from geopy.geocoders import Nominatim

import folium 
from folium import Marker
from folium.plugins import MarkerCluster

def embed_map(m, file_name):
    from IPython.display import IFrame
    m.save(file_name)
    return IFrame(file_name, width='100%', height='500px')


# Geocoding: convert the name of a place or an address to a location on a map.
# Geocode the missing locations
# Load and preview Starbucks locations in California
starbucks = pd.read_csv("../input/geospatial-learn-course-data/starbucks_locations.csv")
starbucks.head()

# How many rows in each column have missing values?
print(starbucks.isnull().sum())

# View rows with missing locations
rows_with_missing = starbucks[starbucks["City"]=="Berkeley"]
rows_with_missing

# Create the geocoder
geolocator = Nominatim(user_agent="kaggle_learn")

def my_geocoder(row):
    try:
        point = geolocator.geocode(row).point
        return pd.Series({'Latitude': point.latitude, 'Longitude': point.longitude})
    except:
        return None

berkeley_locations = rows_with_missing.apply(lambda x: my_geocoder(x['Address']), axis=1)
starbucks.update(berkeley_locations)

# View Berkeley locations
# Create a base map
m_2 = folium.Map(location=[37.88,-122.26], zoom_start=13)

# Add a marker for each Berkeley location
for idx, row in starbucks[starbucks["City"]=='Berkeley'].iterrows():
    Marker([row['Latitude'], row['Longitude']]).add_to(m_2)

# Show the map
embed_map(m_2, 'q_2.html')


# Consolidate your data
CA_counties = gpd.read_file("../input/geospatial-learn-course-data/CA_county_boundaries/CA_county_boundaries/CA_county_boundaries.shp")
CA_counties.head() # GeoDataFrame

# DataFrame
CA_pop = pd.read_csv("../input/geospatial-learn-course-data/CA_county_population.csv", index_col="GEOID")
CA_high_earners = pd.read_csv("../input/geospatial-learn-course-data/CA_county_high_earners.csv", index_col="GEOID")
CA_median_age = pd.read_csv("../input/geospatial-learn-course-data/CA_county_median_age.csv", index_col="GEOID")

cols_to_add = CA_pop.join([CA_high_earners, CA_median_age]).reset_index()
CA_stats = CA_counties.merge(cols_to_add, on="GEOID") # Attribute join merge()
CA_stats.crs = {'init': 'epsg:4326'}

CA_stats["density"] = CA_stats["population"] / CA_stats["area_sqkm"]

# Which counties look promising?
sel_counties = CA_stats[((CA_stats.high_earners > 100000) &
                         (CA_stats.median_age < 38.5) &
                         (CA_stats.density > 285) &
                         ((CA_stats.median_age < 35.5) |
                         (CA_stats.density > 1400) |
                         (CA_stats.high_earners > 500000)))]

# How many stores did you identify?
starbucks_gdf = gpd.GeoDataFrame(starbucks, geometry=gpd.points_from_xy(starbucks.Longitude, starbucks.Latitude))
starbucks_gdf.crs = {'init': 'epsg:4326'}

# Spatial join sjoin() to match locations
locations_of_interest = gpd.sjoin(starbucks_gdf, sel_counties) 
num_stores = len(locations_of_interest)

# Visualize the store locations
# Create a base map
m_6 = folium.Map(location=[37,-120], zoom_start=6)

# Show selected store locations
mc = MarkerCluster()

locations_of_interest = gpd.sjoin(starbucks_gdf, sel_counties)
for idx, row in locations_of_interest.iterrows():
    if not math.isnan(row['Longitude']) and not math.isnan(row['Latitude']):
        mc.add_child(folium.Marker([row['Latitude'], row['Longitude']]))

m_6.add_child(mc)

# Show the map
embed_map(m_6, 'q_6.html')

#################################################################################

universities[['Latitude', 'Longitude']] = universities.apply(lambda x: my_geocoder(x['Name']), axis=1)

print("{}% of addresses were geocoded!".format(
    (1 - sum(np.isnan(universities["Latitude"])) / len(universities)) * 100))

# Drop universities that were not successfully geocoded
universities = universities.loc[~np.isnan(universities["Latitude"])]
