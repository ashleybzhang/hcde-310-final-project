from datetime import datetime, timedelta
from googleapiclient.discovery import build

WORK_START = 9
WORK_END = 18
SLOT_SIZE = 30


def get_busy_times(credentials, emails, start_date_str, end_date_str):
    service = build("calendar", "v3", credentials=credentials)

    time_min = f"{start_date_str}T00:00:00Z"
    time_max = f"{end_date_str}T23:59:59Z"

    items = [{"id": email} for email in emails]
    items.append({"id": "primary"})

    body = {
        "timeMin": time_min,
        "timeMax": time_max,
        "items": items,
    }

    result = service.freebusy().query(body=body).execute()
    calendars = result.get("calendars", {})

    busy_map = {}
    for email, data in calendars.items():
        blocks = []
        for block in data.get("busy", []):
            start = datetime.fromisoformat(block["start"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(block["end"].replace("Z", "+00:00"))
            blocks.append((start, end))
        busy_map[email] = blocks

    return busy_map


def find_free_slots(busy_map, duration_minutes, start_date_str, end_date_str):
    print(">> find_free_slots called")
    print(f">> duration: {duration_minutes}")
    print(f">> date range: {start_date_str} to {end_date_str}")
    print(f">> busy_map keys: {list(busy_map.keys())}")

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str,   "%Y-%m-%d")

    slots_needed = duration_minutes // SLOT_SIZE
    suggestions = []
    print(f">> slots_needed: {slots_needed}")

    current_day = start_date
    while current_day <= end_date:
        print(f">> checking day: {current_day.date()}")

        day_slots = []
        slot_time = current_day.replace(hour=WORK_START, minute=0, second=0, microsecond=0)
        day_end = current_day.replace(hour=WORK_END,   minute=0, second=0, microsecond=0)

        while slot_time < day_end:
            day_slots.append(slot_time)
            slot_time += timedelta(minutes=SLOT_SIZE)

        free_slots = []
        for slot in day_slots:
            slot_end = slot + timedelta(minutes=SLOT_SIZE)
            is_free = True

            for email, blocks in busy_map.items():
                for (b_start, b_end) in blocks:
                    b_start_naive = b_start.replace(tzinfo=None)
                    b_end_naive = b_end.replace(tzinfo=None)

                    if b_start_naive < slot_end and b_end_naive > slot:
                        is_free = False
                        break
                if not is_free:
                    break

            free_slots.append((slot, is_free))

        consecutive = 0
        for i, (slot, is_free) in enumerate(free_slots):
            if is_free:
                consecutive += 1
                if consecutive >= slots_needed:
                    meeting_start = free_slots[i - slots_needed + 1][0]
                    meeting_end = meeting_start + timedelta(minutes=duration_minutes)
                    print(f">> found slot: {meeting_start}")
                    suggestions.append({
                        "start": meeting_start,
                        "end":   meeting_end,
                        "label": meeting_start.strftime("%A, %b %d · %I:%M %p").replace(" 0", " ") +
                                 " – " + meeting_end.strftime("%I:%M %p").lstrip("0"),
                        "start_iso": meeting_start.isoformat(),
                        "end_iso":   meeting_end.isoformat(),
                    })
                    if len(suggestions) >= 5:
                        print(">> returning 5 suggestions")
                        return suggestions
            else:
                consecutive = 0

        current_day += timedelta(days=1)

    print(f">> returning {len(suggestions)} suggestions")
    return suggestions
