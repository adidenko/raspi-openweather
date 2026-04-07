#!/usr/bin/python
# raspi openweather by Granpino. May 2020
# Modified by Alexander Didenko in 2025:
#   - Make it actually work with Python 3.11+
#   - Switch from paid API to free API
#   - Remove data not available in free API
#   - Everything re-adjusted to 800x480 resolution
#   - Day/Night time change of background

import sys, pygame
from pygame.locals import *
import time
import datetime
import requests
import json
import threading

pygame.init()
#========================== SETTINGS ========================
debug = False
settings = {
    'api_key': 'PUT_YOUR_API_KEY_HERE_OR_MODIFY_JSON_CONFIG',
    'lat': '52.5244', # Berlin
    'lon': '13.4105', # Berlin
    'wind_unit': 'kmph', # kmph (km/h) or mps (m/s)
    'temp_unit': 'metric', #unit can be metric, or imperial
}

#set size of the screen
size = width, height = 800, 480
fps = 3
weather_refresh_interval = 900
weather_load_interval = 30

# Put your sensitive info in the JSON config
with open('open_weather.json') as f:
    file_settings = json.load(f)
    settings = settings | file_settings
    if debug:
        print(file_settings)
        print(settings)

#============================================================

Temp_Unit = settings["temp_unit"]
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?appid={0}&exclude=minutely,hourly&lat={1}&lon={2}&units={3}"

###setup
degSymF = chr(0x2109) # Unicode for Degree F
degSYM = chr(0x00B0)  # Unicode for degree symbol
pin = '4'

#screen = pygame.display.set_mode(size) # use this for troubleshooting
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

#define colors
cyan = 50, 255, 255
blue = 130, 75, 200
black = 0, 0, 0
white = 255, 255, 255
lblue = 75, 140, 200
silver = 192, 192, 192
green = 0, 255, 0

clock = pygame.time.Clock()

def __del__(self):
	"Destructor to make sure pygame shuts down"

def mps_to_kmph(mps):
    return round((3.6 * mps), 1)

#define function that checks for mouse clicks
def on_click():
    print('clicked')
    #   exit has been pressed at upper right corner
    if int(width-(width*0.2)) < click_pos[0] < width and 20 < click_pos[1] < int(height*0.2):
   	    button(0)

#define action on pressing buttons
def button(number):
    global set_point
    print("You pressed button {0}".format(number))
    if number == 0:    # exiting
        screen.fill(black)
        pygame.display.flip()
        time.sleep(2)
        pygame.quit()
        sys.exit()

def update_weather():
    if debug:
        print("DEBUG IS ENABLED! Loading data from a fixture: weather.json")
        with open('fixtures/weather.json') as f:
            x = json.load(f)
    else:
        # Request data via API
        final_url = BASE_URL.format(settings["api_key"],settings["lat"],settings["lon"],settings["temp_unit"])
        max_retries = 5
        retry_delay = 5
        response = None
        x = None
        update_weather_error = ""

        for attempt in range(max_retries):
            try:
                response = requests.get(final_url, timeout=5)
                x = response.json()
                if 199 < response.status_code >= 300:
                    update_weather_error = "ERROR: {} {}".format(response.status_code, x)
                    print(update_weather_error)
                else:
                    update_weather_error = ""
                break
            except (requests.ConnectionError, requests.Timeout, requests.RequestException) as e:
                update_weather_error = "Network error (attempt {}/{}): {}".format(attempt + 1, max_retries, str(e))
                print(update_weather_error)
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2

        if x is None:
            update_weather_error = "Failed to fetch weather data after {} retries".format(max_retries)
            print(update_weather_error)

    f_main = x["main"]
    f_weather = x["weather"]

    weather_data = {
        "current_temp": round(f_main["temp"], 1),
        "current_feels_like": round(f_main["feels_like"], 1),
        "current_humidity": f_main["humidity"],
        "current_description": f_weather[0]["main"],
        "icon1": f_weather[0]["icon"],
        "name": x["name"],
        "today_date": x["dt"],
        "today_sunrise": x["sys"]["sunrise"],
        "today_sunset": x["sys"]["sunset"],
        "today_temp_max": round(f_main["temp_max"], 1),
        "today_temp_min": round(f_main["temp_min"], 1),
        "today_wind_speed": x["wind"]["speed"],
        "today_description": f_weather[0]["main"],
        "icon2": f_weather[0]["icon"],
        "update_weather_error": update_weather_error
    }

    # Write weather data to /tmp/open_weather.json
    with open('/tmp/open_weather.json', 'w') as f:
        json.dump(weather_data, f)

def read_weather():
    global current_temp, current_feels_like, current_humidity, current_description, name, update_weather_error
    global today_date, today_sunrise, today_sunset, today_temp_max, today_temp_min, today_wind_speed, today_description

    # Load weather icons
    global load_icon
    load_icon = pygame.image.load("icons/{}.png".format(data["icon1"]))

    try:
        with open('/tmp/open_weather.json') as f:
            data = json.load(f)
            if not data:
                raise ValueError("Empty weather data")
            current_temp = data["current_temp"]
            current_feels_like = data["current_feels_like"]
            current_humidity = data["current_humidity"]
            current_description = data["current_description"]
            name = data["name"]
            today_date = data["today_date"]
            today_sunrise = data["today_sunrise"]
            today_sunset = data["today_sunset"]
            today_temp_max = data["today_temp_max"]
            today_temp_min = data["today_temp_min"]
            today_wind_speed = data["today_wind_speed"]
            today_description = data["today_description"]
            update_weather_error = data.get("update_weather_error", "")

    except (FileNotFoundError, json.JSONDecodeError, ValueError, KeyError) as e:
        print("Error reading weather data: {}".format(e))
        current_temp = 0
        current_feels_like = 0
        current_humidity = 0
        current_description = "N/A"
        name = "Unknown"
        today_date = 0
        today_sunrise = 0
        today_sunset = 0
        today_temp_max = 0
        today_temp_min = 0
        today_wind_speed = 0
        today_description = "N/A"
        load_icon = None

#===================

# Fonts
sfont = pygame.font.SysFont('sans', 18, bold=0)
mfont = pygame.font.SysFont('sans', 24, bold=1)
m2font = pygame.font.SysFont('sans', 29, bold=1)
lfont = pygame.font.SysFont('sans', 40, bold=1)
xlfont = pygame.font.SysFont('sans', 80, bold=1)

if Temp_Unit == ("imperial"):  # do not change this
	degSym = chr(0x2109)		# Unicode for DegreeF
else:
	degSym = chr(0x2103)		# Unicode for DegreeC

def get_background_file():
    mytime = time.localtime()
    if mytime.tm_hour < 6 or mytime.tm_hour > 18:
        return "background_night.jpg"
    else:
        return "background_day.jpg"

def refresh_screen():
    global tim2
    global tim3

    tim1 = time.strftime("%a, %b %d", time.localtime()) + " " + time.strftime("(%d.%m.%Y)", time.localtime())
    tim2 = time.strftime("%H:%M", time.localtime())
    tim3 = time.strftime("%S", time.localtime())
    today_sunrise_str = time.strftime("%H:%M", time.localtime(today_sunrise))
    today_sunset_str = time.strftime("%H:%M", time.localtime(today_sunset))

    time_lbl1 = m2font.render(tim1, 1, (white))
    time_lbl2 = lfont.render(tim2, 1, (white))
    time_lbl3 = sfont.render(tim3, 1, (white))

    skin = pygame.image.load(get_background_file())

    screen.blit(skin,(0,0))

	# ===== Current Temp
    name_lbl = mfont.render(name, 1, cyan)
    outsideT_lbl = xlfont.render("{}{}".format(current_temp, degSYM), 1, cyan)
    outsideF_lbl = mfont.render("Feels like: {}{}".format(current_feels_like, degSYM), True, white)
    outsideH_lbl = mfont.render("Humidity " + str(current_humidity) + '%', 1, white)
	# Show degree F symbol
    degree_lbl = lfont.render( degSym, 1, cyan )
    descrip1_lbl = sfont.render(current_description, 1, white)

    # ===== Today Temp
    today_lbl = m2font.render('Today', 1, green)
    today_descr_lbl = sfont.render(today_description, 1, white)
    minmax_lbl = mfont.render("Temp: " +str(today_temp_max)+degSYM + " / " + str(today_temp_min)+ degSYM, 1, white)
    if settings["wind_unit"] == "mps":
        wind_speed_lbl = mfont.render("Wind: {} m/s".format(today_wind_speed), 1, white)
    else:
        wind_speed_lbl = mfont.render("Wind: {} km/h".format(mps_to_kmph(today_wind_speed)), 1, white)
    today_sunrise_lbl =  mfont.render("Sunrise: {}".format(today_sunrise_str), 1, white)
    today_sunset_lbl =  mfont.render("Sunset: {}".format(today_sunset_str), 1, white)

    # Alignment vars
    px_v_base = 164
    px_v_step = 35

    # Current outside section
    screen.blit(time_lbl1,(13, 23)) # date
    screen.blit(time_lbl2, (645, 13)) # HH:MM
    screen.blit(time_lbl3,(750, 13)) # seconds
    screen.blit(load_icon, (280, 60)) # weather icon
    screen.blit(descrip1_lbl, (300, 140)) # description
    screen.blit(outsideT_lbl, (40, 80)) # temp
    # Use vertical pixel step below
    screen.blit(name_lbl, (40, px_v_base)) # location name
    screen.blit(outsideH_lbl, (40, px_v_base+px_v_step)) # humidity
    screen.blit(outsideF_lbl, (40, px_v_base+2*px_v_step)) # feels like

    # Today section
    screen.blit(today_lbl, (421, 80)) # Today name
    screen.blit(today_descr_lbl, (720, 140)) # description
    screen.blit(load_icon, (700, 60)) # weather icon
    # Use vertical pixel step below
    screen.blit(minmax_lbl, (421, px_v_base-px_v_step)) # Temp min/max
    screen.blit(wind_speed_lbl, (421, px_v_base)) # wind speed
    screen.blit(today_sunrise_lbl, (421, px_v_base+px_v_step)) # wind speed
    screen.blit(today_sunset_lbl, (421, px_v_base+2*px_v_step)) # wind speed

    # Lines
    pygame.draw.line(screen, white,(0,53),(800,53)) # horizontal top
    pygame.draw.line(screen, white,(400,69),(400,270)) # vertical middle

    # Show error if weather update failed
    if update_weather_error:
        error_lbl = mfont.render(update_weather_error, 1, (255, 0, 0))
        screen.blit(error_lbl, (10, height - 30))

    time.sleep(.1)
    pygame.display.flip()

def main():
    global click_pos
    timer = pygame.time.get_ticks()
    while True:
        seconds=(pygame.time.get_ticks() - timer)/1000
        if seconds > weather_refresh_interval:
            timer = pygame.time.get_ticks()
            threading.Thread(target=update_weather, daemon=True).start() # update weather in background
        if seconds > weather_load_interval:
            read_weather() # load weather data from file
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                click_pos = pygame.mouse.get_pos()
                print(click_pos)
                on_click()

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE: # ESC to exit
                sys.exit()

        clock.tick(fps) #screen refresh fps
        refresh_screen()

threading.Thread(target=update_weather, daemon=True).start() # update weather in background
time.sleep(5) # give it a second to fetch data before first load
read_weather() # load weather data from file
main()
