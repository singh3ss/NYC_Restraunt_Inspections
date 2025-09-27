from flask import Flask, render_template_string
import requests
import pandas as pd

# Create the Flask application instance
app = Flask(__name__)

# The core data processing logic is placed inside a function
def get_critical_violations():
    # Fetch NYC restaurant data from the API
    try:
        # Fetch up to 1000 records to ensure a good sample size
        nyc_data = requests.get('https://data.cityofnewyork.us/resource/43nn-pn8j.json?$limit=1000').json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return pd.DataFrame() # Return an empty DataFrame on failure

    # Create a pandas DataFrame
    df = pd.DataFrame(nyc_data)
    
    # Filter out any rows with missing data that might cause errors
    df = df.dropna(subset=['dba','boro','street','zipcode','inspection_date','critical_flag','cuisine_description','violation_description','grade'])
    
    # Select and rename columns for clarity
    df = df[['dba','boro','street','zipcode','inspection_date','critical_flag','cuisine_description','violation_description','grade']]
    df = df.rename(columns={
        'dba': 'Restaurant Name',
        'boro': 'Borough',
        'street': 'Street',
        'zipcode': 'Zipcode',
        'inspection_date': 'Inspection Date',
        'critical_flag': 'critical_flag',
        'cuisine_description': 'Cuisine Description',
        'violation_description': 'Violation Description',
        'grade': 'Grade'
    })

    # Filter for critical violations in Manhattan
    df_manhattan_critical = df[(df['critical_flag'] == 'Critical') & (df['Borough'] == 'Manhattan')]
    
    return df_manhattan_critical.sort_values(by='Inspection Date', ascending=False)

# The web route that will run when you navigate to the page
@app.route('/')
def home():
    df_manhattan_critical = get_critical_violations()
    
    # Apply a CSS class to the table for styling
    styled_df = df_manhattan_critical.style.set_table_attributes('class="responsive-table"')
    html_table = styled_df.to_html()

    # HTML template with embedded CSS for responsiveness
    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Manhattan Critical Violations</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            .table-container {
                overflow-x: auto; /* Enables horizontal scrolling for the table */
            }
            .responsive-table {
                width: 100%; /* Table takes full width of its container */
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            .responsive-table th, .responsive-table td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            .responsive-table th {
                background-color: #f2f2f2;
            }
            /* Optional: Add media queries for more specific responsiveness */
            @media screen and (max-width: 600px) {
                .responsive-table thead {
                    display: none; /* Hide table headers on small screens */
                }
                .responsive-table, .responsive-table tbody, .responsive-table tr, .responsive-table td {
                    display: block; /* Make table elements stack vertically */
                    width: 100%;
                }
                .responsive-table tr {
                    margin-bottom: 15px;
                    border: 1px solid #ddd;
                }
                .responsive-table td {
                    text-align: right;
                    padding-left: 50%;
                    position: relative;
                }
                .responsive-table td::before {
                    content: attr(data-th); /* Display column header as label */
                    position: absolute;
                    left: 6px;
                    width: 45%;
                    padding-right: 10px;
                    white-space: nowrap;
                    text-align: left;
                    font-weight: bold;
                }
            }
        </style>
    </head>
    <body>
        <h1>Manhattan Critical Violations</h1>
        <div class="table-container">
            {{ table | safe }}
        </div>
    </body>
    </html>
    """
    return render_template_string(template, table=html_table)

if __name__ == '__main__':
    app.run(debug=True)