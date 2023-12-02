from datetime import datetime
import requests
from fastapi import FastAPI, HTTPException, Query


def net_asset_value(scheme_code):
    url = f'https://api.mfapi.in/mf/101206?scheme_code={scheme_code}'
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching data: {response.status_code}")


def calculate_profit(nav_data, start_date, end_date, capital):
    units_allotted_date = start_date
    units_allotted = capital / nav_data[0]['nav']  # NAV on the purchase date

    value_on_redemption_date = 0
    for entry in nav_data:
        entry_date = datetime.strptime(entry['date'], "%Y-%m-%d")
        if entry_date == end_date:
            value_on_redemption_date = units_allotted * entry['nav']
            break

    net_profit = value_on_redemption_date - capital

    return net_profit, units_allotted, value_on_redemption_date


app = FastAPI()

@app.get("/profit")
async def get_profit(
    scheme_code: str = Query(..., title="Scheme Code"),
    start_date: str = Query(..., title="Start Date"),
    end_date: str = Query(..., title="End Date"),
    capital: float = Query(..., title="Capital"),
):
    try:
        # Fetch NAV data
        nav_data = net_asset_value(scheme_code)

        # Parse date strings to datetime objects
        start_date = datetime.strptime(start_date, "%d-%m-%Y")
        end_date = datetime.strptime(end_date, "%d-%m-%Y")

        # Calculate profit, units allotted, and value on redemption date
        net_profit, units_allotted, value_on_redemption_date = calculate_profit(nav_data, start_date, end_date, capital)

        return {
            "net_profit": net_profit,
            "units_allotted": units_allotted,
            "value_on_redemption_date": value_on_redemption_date
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating profit: {str(e)}")
