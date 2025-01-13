import requests
import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
LAT = 54.9614281          # Latitude for Vilnius
LON = 23.9083493          # Longitude for Vilnius
TIMEZONE = 'Europe/Vilnius'

# Solar Panel Specifications
PANEL_AREA = 23          # in square meters
EFFICIENCY = 0.20         # 20% efficiency
SYSTEM_LOSSES = 0.15      # 15% system losses

def get_hourly_weather_data():
    url = 'https://api.open-meteo.com/v1/forecast'
    params = {
        'latitude': LAT,
        'longitude': LON,
        'hourly': 'direct_radiation,diffuse_radiation,shortwave_radiation,cloudcover',
        'timezone': TIMEZONE,
        'start': (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime('%Y-%m-%dT00:00'),
        'end': (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime('%Y-%m-%dT23:59'),
    }
    try:
        #logger.info("Requesting hourly weather data from Open-Meteo API...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        #logger.info("Hourly weather data fetched successfully.")
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
        logger.error(f"Response Content: {response.text}")
    except requests.exceptions.Timeout:
        logger.error("Request timed out.")
    except requests.exceptions.RequestException as err:
        logger.error(f"An error occurred: {err}")
    return None

def calculate_hourly_potential_output(data):
    if not data:
        logger.warning("No data available to calculate potential output.")
        return {}

    # Extract hourly data
    hourly = data.get('hourly', {})
    times = hourly.get('time', [])
    direct_radiation = hourly.get('direct_radiation', [])
    diffuse_radiation = hourly.get('diffuse_radiation', [])
    shortwave_radiation = hourly.get('shortwave_radiation', [])
    cloud_cover = hourly.get('cloudcover', [])

    if not times:
        logger.warning("No hourly time data available.")
        return {}

    # Initialize a dictionary to store hourly energy
    hourly_energy = {}

    for i, time_str in enumerate(times):
        try:
            # Extract solar irradiance values
            direct = direct_radiation[i] if i < len(direct_radiation) else 0
            diffuse = diffuse_radiation[i] if i < len(diffuse_radiation) else 0
            ghi = shortwave_radiation[i] if i < len(shortwave_radiation) else 0  # GHI in W/m²

            # Calculate total irradiance on the panel
            # Assuming panel is horizontal. For tilted panels, adjust GHI accordingly.
            # Total irradiance (W/m²) = Direct + Diffuse
            total_irradiance = direct + diffuse  # W/m²

            # Convert irradiance to kWh for the hour
            # Energy (kWh) = Power (kW) * Time (hours)
            # Here, Power (kW) = Irradiance (W/m²) * Panel Area (m²) / 1000
            # Time = 1 hour
            power_kw = (total_irradiance * PANEL_AREA) / 1000  # kW
            energy_kwh = power_kw * EFFICIENCY * (1 - SYSTEM_LOSSES)  # kWh

            # Store the energy value
            hourly_energy[time_str] = round(energy_kwh, 3)
        except IndexError:
            logger.warning(f"Missing data for time index {i}: {time_str}")
            hourly_energy[time_str] = 0
        except Exception as e:
            logger.error(f"Error processing time {time_str}: {e}")
            hourly_energy[time_str] = 0

    return hourly_energy

def add_sun_data(np_data):
    data = get_hourly_weather_data()
    if data:
        hourly_output = calculate_hourly_potential_output(data)
        if hourly_output:
            for item in np_data:
                for sun_time, power in hourly_output.items():
                    #print(item, sun_time, power)
                    if sun_time in item['start']:
                        item['sun'] = power
            return(np_data) 
        else:
            print("Could not calculate hourly potential output.")
    else:
        print("Failed to retrieve weather data.")
    return

def main():
    data = get_hourly_weather_data()
    if data:
        hourly_output = calculate_hourly_potential_output(data)
        if hourly_output:
            print("Estimated Potential Solar Panel Output (kWh) for Tomorrow:")
            for time, energy in hourly_output.items():
                print(f"{time}: {energy} kWh")
        else:
            print("Could not calculate hourly potential output.")
    else:
        print("Failed to retrieve weather data.")


if __name__ == "__main__":
    main()
