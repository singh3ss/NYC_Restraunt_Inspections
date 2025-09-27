
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
        nyc_data = requests.get('https://data.cityofnewyork.us/resource/43nn-pn8j.json?$limit=1000000000').json()
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
    
    
    styled_df = df_manhattan_critical.style.set_table_attributes('class="sleek-table"')
    html_table = styled_df.to_html(index=False)
    
    # Use an f-string to embed the HTML table and modern CSS
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manhattan Critical Violations</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #2c3e50;
            --text-color: #ecf0f1;
            --header-bg-color: #34495e;
            --table-border-color: #3f5469;
            --hover-bg-color: #3b5066;
            --critical-color: #e74c3c;
        }}

        body {{
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Inter', sans-serif;
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }}
        .container {{
            max-width: 95%;
            margin: 2rem auto;
            padding: 2rem;
            border-radius: 10px;
            background-color: var(--bg-color);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
            overflow-x: auto; /* Adds horizontal scroll for small screens */
        }}
        h1 {{
            color: var(--text-color);
            text-align: center;
            font-size: 2.5rem;
            font-weight: 600;
            letter-spacing: 1px;
            margin-bottom: 2rem;
            text-transform: uppercase;
        }}
        .sleek-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
            border-radius: 8px;
            overflow: hidden; /* Ensures rounded corners are applied */
        }}
        .sleek-table thead {{
            background-color: var(--header-bg-color);
            color: #fff;
            position: sticky;
            top: 0;
        }}
        .sleek-table th, .sleek-table td {{
            padding: 1.25rem 1.5rem;
            text-align: left;
            border-bottom: 1px solid var(--table-border-color);
        }}
        .sleek-table th {{
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85rem;
        }}
        .sleek-table tbody tr {{
            background-color: var(--bg-color);
            transition: background-color 0.3s ease;
        }}
        .sleek-table tbody tr:hover {{
            background-color: var(--hover-bg-color);
        }}
        .sleek-table tbody tr:last-of-type td {{
            border-bottom: none;
        }}
        .critical-violation {{
            color: var(--critical-color) !important;
            font-weight: 600;
        }}
        .no-data {{
            text-align: center;
            font-size: 1.1rem;
            color: #95a5a6;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Critical Restaurant Violations in Manhattan</h1>
        {html_table}
    </div>
</body>
</html>
"""
    return render_template_string(html_content)

# This part makes the script runnable from the command line
if __name__ == '__main__':
    app.run(debug=True)
