---
title: 'forest_plot_data: a coordinate-based geospatial package for data acquisition from Google Earth Engine'
tags:
    - Python
    - forestry
    - natural resources
    - Google Earth Engine
authors:
    - name: Tara Skiba
        orcid: 0009-0002-5354-3319
        equal-contrib: true
        affiliation: 1
    - name: Qiusheng Wu
        orcid: 0000-0001-5437-4073
        equal-contrib: false
        affiliation: 2
    - name: Tyler Gifford
        orcid: 0000-0002-2547-3547
        equal-contrib: false
        affiliation: 1

affiliations:
    - name: University of Tennessee, School of Natural Resources, USA
        index: 1
    - name: University of Tennessee, Department of Geography, USA
        index: 2

date: 18 April 2025
bibliography: paper.bib
---

# Summary
`forest_plot_data` is a python package deployed on hugging face to allow natural resource professionals such as foresters or wildlife professionals to access and retrieve data from Google Earth Engine. This purpose of this package is designed to extract values for a list of provided coordinate points.

# Introduction

In recent decades, remote sensing has become an invaluable tool in a multitude of fields, due to the versatility of data collected and potential applications`[@Chi:2016]`. Such information can be revolutionary in the field of forestry, particularly for inventory and research purposes where large-scale or intense monitoring is difficult or impossible to conduct. However, the uptake of remote sensing in forestry has been slow due to a multitude of reasons, as outlined in `[@Fassnacht:2024]`. In addition, several major issues need to be overcome before remote sensing can be fully integrated into standard forestry practices, such as determining forest type, identifying individual trees and species, particularly in mixed-species, uneven aged stands `[@Burkhart:2019; @Jeronimo:2018]`.

Despite this, foresters and forest biometricians can still utilize publicly available remote sensing data for information that is not standard in a traditional forest inventory. This data can still be difficult for the average forester to access due to various technological barriers, as hosting platforms, like Google Earth Engine (GEE), require proficiency in programming skills and a general understanding of how geospatial data is formatted in order to retrieve the desired information.

Under large-area forest sampling inventories, such as the national-level forest inventory survey conducted by the USDA Forest Service’s Forest Inventory and Analysis, often times plots (or subplots or other groupings levels within the larger plot, as described in `@Yang:2022`) are treated as point observations within the survey. The spatial distribution of trees within the plot is not considered when inventories are conducted. Therefore, when incorporating remotely sensed data into these inventories, only the values for the plot's center is needed. This matches the standard forest inventory practice where variables like elevation, slope, and aspect are only measured at plot center. Plot sizes are also often smaller than the resolution of remotely sensed data, and there is a general assumption that variables such as temperature or precipitation do not differ significantly across a plot. Lastly, often times inventories only record the coordinates of plot center, and the spatial distribution of subplots or other grouping levels are not mapped across the plot, therefore extracting values from remotely sensed data for the entire area is not needed.

While python tools and packages currently exist to help users streamline this point-specific acquisition process, such as GEE’s built-in Code Editor, an easy-to-use, point-and-click interface that does not require any programming knowledge does not yet exist. Other geographical software programs can query this information, such as ArcGIS and QGIS, but still require either a subscription to the program or a proficient understanding of geospatial data. Anyone in the natural resource field, whether they are a professional, a private landowner, or participate recreationally can use this package to access GEE-hosted data.


# forest_plot_data Audience
`forest_plot_data` is intended for natural resource professionals who would like to extract Google Earth Engine data for given coordinates, but the use of this package can be useful in other disciplines. This package removes the technological barriers that limit the package’s intended users from being able to utilize remotely sensed data. Users can access the base version of this package through a website (…TBD), and advanced users can modify and build upon this package through the package’s GitHub and PyPI repositories. By design, this package is fairly rudimentary, with the goal of expanding the functions of this package to meet the needs of natural resource professionals accordingly.

# forest_plot_data Functionality
The `forest_plot_data` package is built upon `ipyleaflet` and `geemap`, while also utilizing `pandas` and `geopandas` for data handling and `earthengine` for source data. `forest_plot_data` is broken into two key modules:
-	map: module for displaying an interactive map with uploaded coordinates plotted. Users may customize the map as allowed. This module uses `ipyleaflet`, `ipywidgets`, and `geemap`
-	data_process: module for processing GEE data and returning the desired information for the user-provided coordinates.


# forest_plot_data User Guide
a.	The User uploads a csv or xlsx file with the following three columns: a plot identifier (e.g. plot #), latitude (in dd.), longitude (in dd.).
    i.	Additional columns should not be included.
b.	A map will appear with provided coordinates plotted.
c.	User selects a Google Earth Engine dataset to pull from.
d.	User selects desired time frame.
e.	Package returns csv file with all bands within selected GEE dataset.

# Acknowledgements
The author would like to thank the developers of geemap, ipyleafet, and ipywidgets, which were utilized to efficiently create a map and query the desired data. The author would also like to thank the the USDA's U.S. Forest Service Forest Inventory and Analysis program for their financial support.

# References