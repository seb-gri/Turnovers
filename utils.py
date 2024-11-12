def convert_timestamp_to_seconds(timestamp):
    """
    Convertit un timestamp de la forme HH:MM:SS.SSS en secondes.
    """
    parts = timestamp.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    return hours * 3600 + minutes * 60 + seconds
