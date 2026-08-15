import json

# Helper to load data
# TODO: maybe cache this so we don't read the file every time, but it's fine for now
def load_data():
    try:
        with open("data/mock_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: Could not find data/mock_data.json!")
        return {"visa_requirements": {}, "applications": {}}

def get_required_documents(country: str) -> str:
    """Gets a list of required documents for a given country's visa."""
    print(f"[Tool Call] get_required_documents called for: {country}")
    data = load_data()
    country_key = country.lower()
    
    if country_key in data["visa_requirements"]:
        docs = data["visa_requirements"][country_key]
        return f"To apply for a {country} visa, the required documents are: {', '.join(docs)}."
    else:
        return f"Sorry, I don't have the document requirements for {country} right now."

def check_visa_status(application_id: str) -> str:
    """Checks the current status of a visa application using the application ID."""
    print(f"[Tool Call] check_visa_status called for: {application_id}")
    data = load_data()
    app_id = application_id.upper()
    
    if app_id in data["applications"]:
        status = data["applications"][app_id]["status"]
        date = data["applications"][app_id]["expected_date"]
        return f"The status for application {app_id} is currently '{status}'. Expected date or action: {date}."
    else:
        return f"I couldn't find any visa application with the ID {app_id}. Please check the number and try again."