import datetime

def seconds_to_duration(seconds):
    if not seconds:
        seconds = 0
    duration = str(datetime.timedelta(seconds=seconds))
    duration_slices = duration.split(':')
    return f'{duration_slices[0]}h {duration_slices[1]}m {duration_slices[2]}s'
