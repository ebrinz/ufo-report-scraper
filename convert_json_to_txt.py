import json
import os

# Set directory path containing JSON files
directory = "../ufo-report-scraper/data/raw_month_data"

# Loop through files in the directory
for filename in os.listdir(directory):
    if filename.endswith(".json"):
        # Open the JSON file and load the data
        with open(os.path.join(directory, filename), "r") as f:
            data = json.load(f)
        
        # Create a new file with the same name but a .txt extension
        new_filename = os.path.splitext(filename)[0] + ".txt"
        new_file_path = os.path.join(directory, new_filename)
        
        # Open the new file for writing
        with open(new_file_path, "w") as f:
            # Loop through the list of reports
            for report in data:
                # Write the report information as bullet points
                f.write(f"- Report ID: {report['report_id']}\n")
                f.write(f"  Location: {report['location']}\n")
                f.write(f"  Entered: {report['entered']}\n")
                f.write(f"  Occurred: {report['occurred']}\n")
                f.write(f"  Reported: {report['reported']}\n")
                f.write(f"  Posted: {report['posted']}\n")
                f.write(f"  Shape: {report['shape']}\n")
                f.write(f"  Duration: {report['duration']}\n")
                f.write(f"  Status Code: {report.get('status_code', '')}\n")
                
                # Write the report characteristics as sub-bullet points
                characteristics = report.get("characteristics", "")
                if characteristics:
                    f.write("  Characteristics:\n")
                    for char in characteristics.split(", "):
                        f.write(f"    - {char}\n")
                
                # Write the report description as a sub-bullet point
                description = report.get("description", "")
                if description:
                    f.write("  Description:\n")
                    for line in description.split("\n"):
                        # Remove extra newlines
                        line = line.strip()
                        if line:
                            f.write(f"    - {line}\n")
                
                # Add a blank line after each report
                f.write("\n")
