#!/usr/bin/env python
# coding: utf-8

# In[11]:


# Dependencies and File Imports
import pandas as pd

listings = pd.read_csv("listings.csv")
reviews = pd.read_csv("reviews.csv")


# In[12]:


# Merging Data Sources
review_listing = pd.merge(left=listings, right=reviews, how='left', left_on='id', right_on='listing_id')
review_listing.rename(columns={'id_x':'id', 'id_y':"review_id"}, inplace=True)
airbnb = review_listing


# In[13]:


# Filling NaN reviews
airbnb.fillna({'reviews_per_month':0})

# Dropping unnecessary columns
airbnb.drop(["reviewer_name", "last_review", "name", "neighbourhood_group", "reviews_per_month", "calculated_host_listings_count"], axis=1, inplace=True)


# In[ ]:


# Isolating districts and room types
print(airbnb["neighbourhood"].unique())
print(airbnb["room_type"].unique())


# In[29]:


# Conditions for being "bookable":
### A room with a "reasonable" price (under 100 EUR)
### either an entire appartment or home
### the reviews must be over 5 (to avoid the chances of getting a new host - we want a smooth process)
price_reasonable = airbnb["price"] < 100
appt = airbnb["room_type"] == "Entire home/apt"
reviews = airbnb["number_of_reviews"] > 5

### Creating our new data frame
bookable_price = airbnb[price_reasonable & appt & reviews]


# In[31]:


# Initial graph
# Which Neighbourhoods are generally the most expensive / most cheap?
import seaborn as sns
import matplotlib.pyplot as plt
sns.set_style("darkgrid")
sns.set_context("poster")
plt.figure(figsize=(10, 50))
plot2=sns.violinplot(data=bookable_price, y='neighbourhood', x='price', cut=2, linewidth=0.1, 
                    saturation=0.6, dodge=True)
plot2.set_title('Density and distribution of prices for each Neighberhood Group')
plot2.set_xticklabels(plot2.get_xticklabels(), rotation=90)


# In[34]:


# Price density of the airbnb's which we defined as "bookable"
# Cartographically illustrated

plt.figure(figsize=(16.0,13.34))
munich_map=plt.imread("index.png")

plt.imshow(munich_map,zorder=0, aspect="auto", extent = [11.378370, 11.712010, 
                                                         48.070270, 48.222970])
ax=plt.gca()
ax.grid(False)

bookable_price.plot(kind='scatter', x='longitude', y='latitude', label='availability_365', c='price', ax=ax, 
           cmap=plt.get_cmap('OrRd'), colorbar=True, alpha=0.4, zorder=5)

plt.show()


# In[37]:


# Creating a data frame for transportation stations to the Allianz Arena (including the stadium itself)

# Alianz Arena 48.218964, 11.624686
# U-Bahn Stations
# 48.177713, 11.601565
# 48.173279, 11.596791
# 48.172909, 11.597049
# 48.166628, 11.590362
# 48.162051, 11.586709
# 48.156941, 11.586095
# 48.149616, 11.582374
# 48.143174, 11.581172
# 48.137962, 11.578683
# 48.133866, 11.568856
# 48.129539, 11.558127
# 48.126128, 11.552081
# 48.120888, 11.550358
# 48.117068, 11.538083
# 48.117489, 11.526338
# 48.116943, 11.526087
# 48.118243, 11.516352

d= {'latitude': [48.218964, 48.177713,48.173279,48.172909,48.166628,48.162051,48.156941,48.149616,
                 48.143174,48.137962,48.133866,48.129539,48.126128,48.120888,48.117068,
                 48.117489,48.116943,48.118243], 
    'longitude': [11.624686, 11.601565,11.596791,11.597049,11.590362,11.586709,11.586095,11.582374,11.581172,
                  11.578683,11.568856,11.558127,11.552081,11.550358,11.538083,11.526338,11.526087,
                  11.516352]}
transport_links = pd.DataFrame(d)


# In[46]:


# Creating a dataset of "bookable" airbnbs which are also close to transport links to the stadium

### airbnbs close in latitude
near_lats = []
for lat in transport_links["latitude"]:
        condition1 = lat - 0.0006 < bookable_price["latitude"]
        condition2 = lat + 0.0006 > bookable_price["latitude"]   
        near_lat = bookable_price[(condition1 & condition2)]
        near_lats.append(near_lat)
near_lats = pd.concat(near_lats)

### airbnbs close in longitude
near_longs=[]
for long in transport_links["longitude"]:
        condition3 = long - 0.0006 < bookable_price["longitude"]
        condition4 = long + 0.0006 > bookable_price["longitude"]
        near_long = bookable_price[(condition3 & condition4)]
        near_longs.append(near_long)
near_longs = pd.concat(near_longs)    

### Merging the dataframes to provide locations which are near in both lat and long
dfa = near_longs.drop_duplicates(subset=['id'])
dfb = near_lats.drop_duplicates(subset=['id'])

near_locations = pd.merge(dfa, dfb, how='inner', on=['id', 'host_id', 'host_name', 'neighbourhood', 'latitude', 'longitude',
       'room_type', 'price', 'minimum_nights', 'number_of_reviews',
       'availability_365', 'listing_id', 'review_id', 'date', 'reviewer_id',
       'comments'])


# In[52]:


readable_near_locations = near_locations.drop(["host_id", "host_id", "latitude", 
                "longitude", "room_type", "number_of_reviews","listing_id",
                            "review_id", "date", "reviewer_id", "comments"], axis=1)
readable_near_locations


# In[63]:


# Creating a map of all "bookable" airbnbs, the darker the colour, the more expensive the appartment
# HINT: you can hover and zoom!

### Data
bookable_lat = bookable_price["latitude"]
bookable_long = bookable_price["longitude"]
name = bookable_price["id"]
price = bookable_price["price"]

### Creating the map
fig2 = go.Figure()

### Adding data to the map
fig2.add_trace(go.Scattermapbox(
        lat=bookable_lat,
        lon=bookable_long,
        mode="markers",
        marker=go.scattermapbox.Marker(size=6, colorscale=[[0, 'rgb(255,255,0)'], 
                                        [1, 'rgb(255,0,0)']], color=price, opacity=0.5),
        text= price
))

### Styling the map
fig2.update_layout(mapbox_style="mapbox://styles/oliverbains/ck76dcbey1r201imzpj563bs3")
fig2.update_layout(
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=go.layout.mapbox.Center(lat=48.14,lon=11.58),
        pitch=0,
        zoom=11))

fig2.show()


# In[61]:


# Creating a map of near and bookable airbnbs with an overlay of the transport stations
# Hovering shows you the id of the airbnb

### Importing plotly to create more graphs
import plotly.graph_objects as go

### Data
transport_lat = transport_links["latitude"].to_list()
transport_long = transport_links["longitude"].to_list()
area = ["Allianz","U-Bahn","U-Bahn","U-Bahn","U-Bahn","U-Bahn","U-Bahn","U-Bahn","U-Bahn","U-Bahn","U-Bahn","U-Bahn","U-Bahn","U-Bahn","U-Bahn",
             "U-Bahn","U-Bahn","U-Bahn"]

near_lat = near_locations["latitude"]
near_long = near_locations["longitude"]
name = near_locations["id"]

### Creating the map
mapbox_access_token = "pk.eyJ1Ijoib2xpdmVyYmFpbnMiLCJhIjoiY2s3NjNqOG16MDBhZDNubWs5NTh5ZzV6diJ9.FilhBHaINRJRvA9G7F0z4A"

fig = go.Figure()

### Adding data to the map
fig.add_trace(go.Scattermapbox(
        lat=transport_lat,
        lon=transport_long,
        name="transport",
        mode="markers",
        marker=go.scattermapbox.Marker(size=14, color="blue", opacity=0.75),
        text=area))

fig.add_trace(go.Scattermapbox(
        lat=near_lat,
        lon=near_long,
        mode="markers",
        name="airbnbs",
        marker=go.scattermapbox.Marker(size=5, color="red", opacity=1),
        text=name))

### Styling the map
fig.update_layout(mapbox_style="mapbox://styles/oliverbains/ck76dcbey1r201imzpj563bs3")
fig.update_layout(
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=go.layout.mapbox.Center(lat=48.14,lon=11.58),
        pitch=0,
        zoom=11))

fig.show()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[39]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




