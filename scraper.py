import os, time, requests, logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

URL = "https://campusrec.ucsc.edu/FacilityOccupancy"
FACILITY_ID = "facility-1799266f-57d9-4cb2-9f43-f5fd88b241db"

OUTPUT_DIR = "occupancy_logs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Opening hours: [open_hour, close_hour)
WEEKDAY_HOURS = (6, 23)
WEEKEND_HOURS = (8, 20)

session = requests.Session()
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%H:%M")


def get_hours(now: datetime) -> tuple[int, int]:
    return WEEKDAY_HOURS if now.weekday() < 5 else WEEKEND_HOURS


def is_open(now: datetime) -> bool:
    open_hour, close_hour = get_hours(now)
    return open_hour <= now.hour < close_hour


def get_occupancy() -> int | None:
    try:
        resp = session.get(URL, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        div = soup.find('div', id=FACILITY_ID)
        return int(div.select_one('.occupancy-count').text.strip())
    except Exception as e:
        logging.warning(f"fetch failed: {e}")
        return None


def log_occupancy(now: datetime, occupancy: int | None):
    file_name = os.path.join(OUTPUT_DIR, now.strftime("%Y-%m-%d") + ".txt")
    with open(file_name, "a") as f:
        f.write(f"{now:%H:%M}, {occupancy if occupancy is not None else 'ERROR'}\n")
    logging.info(f"logged: {occupancy if occupancy is not None else 'ERROR'}")


def wait(now: datetime) -> float:
    open_hour, close_hour = get_hours(now)

    # 1) If the gym is open right now -> jump to the next quarter-hour
    if is_open(now):
        delta_min = 15 - (now.minute % 15)
        return ((now + timedelta(minutes=delta_min)).replace(second=0, microsecond=0) - now).total_seconds()

    # 2) If it’s after closing (close_hour <= hour < 24) -> next opening tomorrow
    if close_hour <= now.hour < 24:
        tomorrow = now + timedelta(days=1)
        open_tomorrow, _ = get_hours(now + timedelta(days=1))
        return (tomorrow.replace(hour=open_tomorrow, minute=0, second=0, microsecond=0) - now).total_seconds()

    # 3) Otherwise (0 <= hour < open_hour) -> next opening today
    return (now.replace(hour=open_hour, minute=0, second=0, microsecond=0) - now).total_seconds()


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    while True:
        now = datetime.now()
        if is_open(now):
            log_occupancy(now, get_occupancy())
        else:
            clear()
            logging.info(f"closed; next check when open.")
        time.sleep(wait(now))


if __name__ == "__main__":
    clear()
    main()