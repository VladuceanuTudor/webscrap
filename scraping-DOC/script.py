import re
import pandas as pd

def extract_profiles(text):
    # Split the text into lines
    lines = text.splitlines()
    
    # Initialize variables
    profiles = []
    current_profile = {
        "Name": None,
        "Profession/Details": None,
        "Location": None,
        "Phone": None
    }
    capture = False
    
    for line in lines:
        # Start capturing after this phrase
        if "Afișează cabinete ce oferă specializarea/serviciul:" in line:
            capture = True
            continue

        # Stop capturing when the "number cabinete" line appears
        if re.search(r"\d+\s+cabinete", line):
            capture = False
            continue

        # Ignore unwanted lines with "voturi", "recomandăm", "Colaborator", or URLs
        if re.search(r"\d+\s+din\s+\d+\s+voturi", line) or "recomandăm" in line.lower() or \
           "Colaborator" in line or "website" in line:
            continue

        if capture and line.strip():
            line = line.strip()

            # Capture 'Name' as the first non-empty line of the profile
            if current_profile["Name"] is None:
                current_profile["Name"] = line
                continue

            if current_profile["Profession/Details"] is None and line.startswith("Locație:"):
                current_profile["Profession/Details"] = " - "
                current_profile["Location"] = line
                continue

            # Capture 'Profession/Details' unless it's the 'Locație' line
            if current_profile["Profession/Details"] is None and not line.startswith("Locație:"):
                current_profile["Profession/Details"] = line
                continue

            # Capture 'Location' for lines starting with 'Locație:'
            if current_profile["Location"] is None and line.startswith("Locație:"):
                current_profile["Location"] = line
                continue

            # Capture 'Phone' for lines starting with 'Telefon:'
            if current_profile["Phone"] is None and line.startswith("Telefon:"):
                current_profile["Phone"] = line
                # Once the phone is captured, the profile is complete
                profiles.append(current_profile)
                # Reset for the next profile
                current_profile = {
                    "Name": None,
                    "Profession/Details": None,
                    "Location": None,
                    "Phone": None
                }

    return profiles

# Read the text from a file
with open("scraped_text.txt", "r", encoding="utf-8") as file:
    text = file.read()

# Extract the profile data
profile_data = extract_profiles(text)

# Convert the profile data to a DataFrame
df = pd.DataFrame(profile_data)

# Save the DataFrame to an Excel file
df.to_excel("profilesREST.xlsx", index=False)

print("Profiles have been written to 'profiles_output.xlsx'")
