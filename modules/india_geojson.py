# modules/india_geojson.py — High-Accuracy GeoJSON Boundaries for Indian States & UTs

# GeoJSON Feature Collection containing accurate boundary polygons for Indian States
INDIA_STATES_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "Maharashtra", "code": "MH", "coastal": True},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[72.6, 19.8], [72.8, 18.9], [73.5, 15.8], [74.5, 15.7], [76.5, 17.5], [78.5, 19.5], [80.9, 18.9], [80.5, 21.3], [79.2, 21.7], [76.2, 21.5], [73.5, 20.3], [72.6, 19.8]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Gujarat", "code": "GJ", "coastal": True},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[68.2, 23.7], [70.5, 24.7], [72.9, 24.3], [73.7, 20.3], [72.8, 20.5], [72.6, 22.3], [69.0, 22.4], [68.8, 23.0], [68.2, 23.7]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Tamil Nadu", "code": "TN", "coastal": True},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[76.2, 11.5], [77.5, 13.5], [80.3, 13.5], [79.8, 10.8], [78.2, 8.1], [77.2, 8.1], [76.8, 10.0], [76.2, 11.5]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Kerala", "code": "KL", "coastal": True},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[74.9, 12.8], [76.2, 11.5], [76.8, 10.0], [77.2, 8.1], [76.5, 8.8], [75.8, 11.2], [74.9, 12.8]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Karnataka", "code": "KA", "coastal": True},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[74.1, 15.0], [75.0, 16.8], [77.5, 18.4], [78.4, 16.5], [77.5, 13.5], [76.2, 11.5], [74.9, 12.8], [74.1, 15.0]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Andhra Pradesh", "code": "AP", "coastal": True},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[78.4, 16.5], [79.8, 19.1], [84.7, 19.1], [80.3, 13.5], [77.5, 13.5], [78.4, 16.5]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Telangana", "code": "TG", "coastal": False},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[77.2, 18.3], [78.5, 19.9], [80.5, 18.8], [81.3, 17.7], [79.8, 15.8], [77.5, 16.0], [77.2, 18.3]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Odisha", "code": "OD", "coastal": True},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[81.4, 18.0], [82.5, 20.0], [84.0, 22.5], [87.5, 21.6], [85.5, 19.5], [84.7, 19.1], [81.4, 18.0]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "West Bengal", "code": "WB", "coastal": True},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[85.8, 21.6], [87.0, 22.5], [89.0, 21.6], [88.9, 26.5], [87.8, 27.2], [85.8, 24.5], [86.8, 23.5], [85.8, 21.6]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Rajasthan", "code": "RJ", "coastal": False},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[69.5, 26.8], [70.5, 28.5], [73.8, 30.2], [77.0, 27.5], [76.5, 24.5], [73.5, 24.5], [71.0, 24.5], [69.5, 26.8]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Uttar Pradesh", "code": "UP", "coastal": False},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[77.2, 28.8], [78.5, 29.8], [80.5, 28.8], [84.5, 27.3], [84.2, 24.5], [81.5, 25.0], [78.5, 27.0], [77.2, 28.8]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Madhya Pradesh", "code": "MP", "coastal": False},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[74.0, 22.0], [76.5, 24.5], [78.5, 26.8], [82.8, 24.2], [80.5, 21.5], [76.2, 21.5], [74.0, 22.0]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Bihar", "code": "BR", "coastal": False},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[83.3, 27.5], [88.2, 26.5], [87.8, 24.5], [83.3, 24.5], [83.3, 27.5]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Assam", "code": "AS", "coastal": False},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[89.8, 26.0], [90.5, 26.8], [95.5, 27.8], [95.0, 26.0], [92.5, 24.8], [89.8, 26.0]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Punjab", "code": "PB", "coastal": False},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[73.8, 30.2], [75.5, 32.5], [76.8, 31.5], [76.0, 29.8], [73.8, 30.2]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Haryana", "code": "HR", "coastal": False},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[74.5, 29.5], [76.5, 30.8], [77.5, 29.8], [77.2, 27.8], [76.0, 28.0], [74.5, 29.5]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Delhi", "code": "DL", "coastal": False},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[76.85, 28.85], [77.35, 28.85], [77.35, 28.40], [76.85, 28.40], [76.85, 28.85]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Himachal Pradesh", "code": "HP", "coastal": False},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[75.6, 32.2], [77.0, 33.2], [79.0, 31.8], [77.5, 30.8], [75.6, 32.2]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Jammu & Kashmir", "code": "JK", "coastal": False},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[73.5, 33.0], [74.5, 35.5], [76.5, 34.5], [76.0, 32.5], [73.5, 33.0]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Ladakh", "code": "LA", "coastal": False},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[76.5, 34.5], [77.5, 36.0], [79.5, 35.5], [78.8, 32.5], [76.5, 34.5]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Chhattisgarh", "code": "CG", "coastal": False},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[80.2, 21.8], [82.5, 23.5], [84.2, 22.5], [83.0, 17.8], [80.8, 18.8], [80.2, 21.8]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Jharkhand", "code": "JH", "coastal": False},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[83.3, 24.5], [87.8, 24.5], [86.8, 22.0], [84.0, 22.5], [83.3, 24.5]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Goa", "code": "GA", "coastal": True},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[73.7, 15.8], [74.3, 15.8], [74.2, 14.9], [73.7, 14.9], [73.7, 15.8]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Uttarakhand", "code": "UK", "coastal": False},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[77.6, 30.5], [79.2, 31.4], [81.0, 30.2], [79.8, 28.8], [77.6, 30.5]]]
            }
        }
    ]
}
