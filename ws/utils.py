from django.utils import timezone

async def format_time_difference(past_time):

    current_time = timezone.now()
    past_time = current_time - past_time

# Time difference in seconds
    seconds_diff = past_time.total_seconds()

    # Define thresholds for different time units
    thresholds = [
        (60, 's'),
        (3600, 'min'),
        (86400, 'hours'),
        (2592000, 'days'),
        (31536000, 'months'),
        (float('inf'), 'years')
    ]

    # Find the appropriate time unit and format the time difference
    for threshold, unit in thresholds:
        if seconds_diff < threshold:
            if unit == 's':
                return 'just now'
            elif unit == 'min':
                return f"{int(seconds_diff / 60)} min"
            elif unit == 'hours':
                return f"{int(seconds_diff / 3600)} hours"
            elif unit == 'days':
                return f"{int(seconds_diff / 86400)} day" if int(seconds_diff / 86400) == 1 else f"{int(seconds_diff / 86400)} days"
            elif unit == 'months':
                return f"{int(seconds_diff / 2592000)} month" if int(seconds_diff / 2592000) == 1 else f"{int(seconds_diff / 2592000)} months"
            elif unit == 'years':
                return f"{int(seconds_diff / 31536000)} year" if int(seconds_diff / 31536000) == 1 else f"{int(seconds_diff / 31536000)} years"
