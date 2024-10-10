import re
import geojson
import os

# Function to extract rawLatitude and rawLongitude from the line
def extract_raw_lat_long(line):
    # Regex pattern to match rawLatitude and rawLongitude
    pattern = r"rawLongitude=([\d.-]+),.+rawLatitude=([\d.-]+)"
    match = re.search(pattern, line)
    if match:
        # Extract latitude and longitude as floats
        raw_longitude = float(match.group(1))
        raw_latitude = float(match.group(2))
        return raw_latitude, raw_longitude
    return None, None

# Function to extract latitude and longitude from the line
def extract_lat_long(line):
    # Regex pattern to match the latitude and longitude
    pattern = r"Real GPS\s*([\d]+,[\d]+),([\d]+,[\d]+)"
    match = re.search(pattern, line)
    if match:
        # Extract and convert the latitude and longitude values
        latitude = match.group(1).replace(',', '.')
        longitude = match.group(2).replace(',', '.')
        return float(latitude), float(longitude)
    return None, None

# Function to read a log file and extract all coordinates
def parse_log_file(file_path):
    coordinates = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                latitude, longitude = extract_lat_long(line)
                if latitude is not None and longitude is not None:
                    coordinates.append(((longitude, latitude),"#00ff00"))  # GeoJSON expects (longitude, latitude)
                latitude, longitude = extract_raw_lat_long(line)
                if latitude is not None and longitude is not None:
                    coordinates.append(((longitude, latitude),"#ff0000"))  # GeoJSON expects (longitude, latitude)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    return coordinates

# Function to write coordinates into a GeoJSON file
def write_geojson(coordinates, output_file):
    # Create GeoJSON Point features for each coordinate pair
    features = [geojson.Feature(geometry=geojson.Point(coord[0]), properties={"marker-color": coord[1]}) for coord in coordinates]
    feature_collection = geojson.FeatureCollection(features)
    
    # Write the GeoJSON to a file
    with open(output_file, 'w') as file:
        geojson.dump(feature_collection, file, indent=2)
    print(f"GeoJSON data has been written to {output_file}")

# Function to find all .log files in a given directory
def find_log_files(directory):
    log_files = []
    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file ends with .log
            if file.endswith('.log'):
                log_files.append(os.path.join(root, file))
    return log_files

# Example usage: specify the directory you want to search
directory_path = 'navi_log/NioApp/storage_Log/'  # Change this to your log files directory

# Get the list of .log files in the directory
log_files = find_log_files(directory_path)

# Output the list of found .log files
if log_files:
    print(f"Found {len(log_files)} log files:")
    for log_file in log_files:
        print(log_file)
        output_geojson_file = log_file+'.geojson'
        # Parse the log file to get coordinates
        coordinates = parse_log_file(log_file)
        # Write the extracted coordinates to a GeoJSON file
        if coordinates:
            write_geojson(coordinates, output_geojson_file)
        else:
            print("No valid latitude and longitude values were found in the log file.")
else:
    print("No .log files found in the specified directory.")
