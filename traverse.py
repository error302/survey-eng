import csv
import math
from prettytable import PrettyTable

# Constants for change in northing and easting
change_in_northing = "Change in Northing"
change_in_easting = "Change in Easting"

# Function to calculate changes and adjustments
def calculate_change_and_adjustments(bearing_degrees, distance, total_distance, delta_northing, delta_easting):
    bearing_radians = math.radians(bearing_degrees)
    change_northing = distance * math.sin(bearing_radians)
    change_easting = distance * math.cos(bearing_radians)
    adjusted_change_northing = (distance / total_distance) * delta_northing
    adjusted_change_easting = (distance / total_distance) * delta_easting
    return change_northing, change_easting, adjusted_change_northing, adjusted_change_easting

try:
    # Get user inputs
    file_name = input("Enter file name: ")
    traversal_order = int(input("Enter traversal order: "))
    datum_northing = float(input("Enter Datum Northing: "))
    datum_easting = float(input("Enter Datum Easting: "))
    
    # Read and store data from CSV file
    data = []
    with open(file_name, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        next(reader)  # Skip header
        for row in reader:
            data.append(row)
            
    # Calculate total distance of the traverse
    total_distance = sum(float(row["Distance"]) for row in data)
    
    # Display input data in a table
    table = PrettyTable()
    table.field_names = data[0].keys()
    for row in data:
        table.add_row(row.values())
    print("Input Data:\n")
    print(table)
    
    # Calculate deltas for adjustment calculations
    delta_northing = datum_northing - float(data[0]["Traverse Northing"])
    delta_easting = datum_easting - float(data[0]["Traverse Easting"])
    
    for leg in data:
        bearing_degrees = float(leg["Bearing"])
        distance = float(leg["Distance"])

        (change_northing, change_easting,
         adjusted_change_northing, adjusted_change_easting) = calculate_change_and_adjustments(
            bearing_degrees, distance, total_distance, delta_northing, delta_easting)

        leg[change_in_northing] = change_northing
        leg[change_in_easting] = change_easting
        leg["Adjusted Change in Northing"] = adjusted_change_northing
        leg["Adjusted Change in Easting"] = adjusted_change_easting

    results_table = PrettyTable()
    results_table.field_names = ["Line (Bearing, Distance)", change_in_northing, change_in_easting,
                                 "Station", "Northing", "Easting"]

    for leg_num, leg in enumerate(data, start=1):
        bearing = leg["Bearing"]
        distance = leg["Distance"]
        change_northing = leg[change_in_northing]
        change_easting = leg[change_in_easting]
        station = leg["Station"]
        northing = leg["Northing"]
        easting = leg["Easting"]

        results_table.add_row([f"{bearing}°, {distance} m", change_northing, change_easting,
                                station, northing, easting])

    print("\nCalculated Results:\n")
    print(results_table)

    initial_datum_northing = float(data[0]["Initial Datum Northing"])
    initial_datum_easting = float(data[0]["Initial Datum Easting"])

    for leg in data:
        adjusted_northing = initial_datum_northing + float(leg["Adjusted Change in Northing"])
        adjusted_easting = initial_datum_easting + float(leg["Adjusted Change in Easting"])
        leg["Adjusted Northing"] = adjusted_northing
        leg["Adjusted Easting"] = adjusted_easting

    accuracy_denominator = math.sqrt(delta_northing ** 2 + (delta_easting ** 2 / total_distance))
    accuracy_ratio = 1 / accuracy_denominator

    print("Accuracy:", accuracy_ratio)

    if traversal_order == 1 and accuracy_ratio >= 0.00001:
        print("Congratulations! The accuracy of the traverse is within the required range.")
    elif traversal_order == 2 and 0.00002 <= accuracy_ratio < 0.00001:
        print("The accuracy of the traverse is within the required range.")
    elif traversal_order == 3 and 0.0001 <= accuracy_ratio < 0.00002:
        print("Congratulations! The accuracy of the traverse is within the required range.")
    else:
        print("Sorry! The accuracy of the traverse is not within the required range.")

except FileNotFoundError:
    print("File not found.")
except Exception as e:
    print("An error occurred:", e)
