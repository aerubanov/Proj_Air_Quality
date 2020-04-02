def pm25_to_aqius(pm):
    if pm <= 12:
        i_low = 0
        i_high = 50
        c_low = 0
        c_high = 12
    elif 12 < pm <= 35.4:
        i_low = 50
        i_high = 100
        c_low = 12
        c_high = 35.4
    elif 35.4 < pm <= 55.4:
        i_low = 100
        i_high = 150
        c_low = 35.4
        c_high = 55.4
    elif 55.4 < pm <= 150.4:
        i_low = 150
        i_high = 200
        c_low = 55.4
        c_high = 150.4
    elif 150.4 < pm <= 250.4:
        i_low = 200
        i_high = 300
        c_low = 150.4
        c_high = 250.4
    else:
        i_low = 300
        i_high = 500
        c_low = 250.4
        c_high = 500.4
    return (i_high - i_low) / (c_high - c_low) * (pm - c_low) + i_low


def aqi_level(aqi):
    if aqi <= 50:
        return 'good'
    if 50 < aqi <= 100:
        return 'moderate'
    if 100 < aqi <= 150:
        return 'Unhealthy for sens. groups'
    if 150 < aqi <= 200:
        return 'Unhealthy'
    if 200 < aqi <= 300:
        return 'Very Unhealthy'
    if aqi > 300:
        return 'Hazardous'
