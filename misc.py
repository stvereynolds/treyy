from seleniumbase import SB
import random
import base64
import requests


# ============================================================
# Misc Helpers (added harmless utilities)
# ============================================================

def noop(*args, **kwargs):
    """A harmless no-op function."""
    return None

def jitter_delay():
    """Extra random jitter to vary timing."""
    return random.uniform(0.1, 0.4)


# ============================================================
# Core Utility Functions (reordered + renamed)
# ============================================================

def b64_to_text(encoded_val):
    """Decode Base64 text."""
    return base64.b64decode(encoded_val).decode("utf-8")


def maybe_click(driver, css_sel, wait_time=4):
    """Click an element if present."""
    if driver.is_element_present(css_sel):
        driver.cdp.click(css_sel, timeout=wait_time)


def random_pause(low=450, high=800):
    """Return a random delay in milliseconds."""
    return random.randint(low, high)


def get_geo(proxy_cfg):
    """Fetch geolocation data with optional proxy."""
    try:
        r = requests.get("http://ip-api.com/json/", proxies=proxy_cfg, timeout=10)
        return r.json(), proxy_cfg
    except requests.exceptions.RequestException:
        fallback = requests.get("http://ip-api.com/json/").json()
        return fallback, False


def start_driver(url, tz, loc, proxy):
    """Start SeleniumBase driver with CDP."""
    drv = SB(
        uc=True,
        locale="en",
        ad_block=True,
        chromium_arg='--disable-webgl',
        proxy=proxy
    )
    drv.activate_cdp_mode(url, tzone=tz, geoloc=loc)
    return drv


# ============================================================
# Initial Setup (variable names changed)
# ============================================================

proxy_host = "127.0.0.1"
proxy_port_num = "18080"
proxy_enabled = False  # override to disable proxy

proxy_settings = {"http": proxy_enabled}

geo_data, proxy_enabled = get_geo(proxy_settings)

lat = geo_data["lat"]
lon = geo_data["lon"]
tz_id = geo_data["timezone"]
lang = geo_data["countryCode"].lower()

encoded_user = "YnJ1dGFsbGVz"
decoded_user = b64_to_text(encoded_user)

stream_url = f"https://www.twitch.tv/{decoded_user}"


# ============================================================
# Main Loop (structure preserved)
# ============================================================

while True:

    with start_driver(
        stream_url,
        tz_id,
        (lat, lon),
        proxy_enabled
    ) as driver_main:

        delay_ms = random_pause()

        driver_main.sleep(2 + jitter_delay())
        maybe_click(driver_main, 'button:contains("Accept")')
        driver_main.sleep(2 + jitter_delay())

        driver_main.sleep(12)
        maybe_click(driver_main, 'button:contains("Start Watching")')
        driver_main.sleep(10)
        maybe_click(driver_main, 'button:contains("Accept")')

        if driver_main.is_element_present("#live-channel-stream-information"):

            maybe_click(driver_main, 'button:contains("Accept")')

            # Spawn secondary viewer
            driver_secondary = driver_main.get_new_driver(undetectable=True)
            driver_secondary.activate_cdp_mode(
                stream_url,
                tzone=tz_id,
                geoloc=(lat, lon)
            )
            driver_secondary.sleep(10)

            maybe_click(driver_secondary, 'button:contains("Start Watching")')
            driver_secondary.sleep(10)
            maybe_click(driver_secondary, 'button:contains("Accept")')

            driver_main.sleep(delay_ms / 1000)

        else:
            break
