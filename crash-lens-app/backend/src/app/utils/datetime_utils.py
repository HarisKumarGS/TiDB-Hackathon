from datetime import datetime, timezone


def get_utc_now_naive() -> datetime:
    """
    Get current UTC datetime as timezone-naive for database storage.
    
    PostgreSQL expects timezone-naive datetime objects for timestamp columns.
    This function returns the current UTC time without timezone info.
    
    Returns:
        datetime: Current UTC time without timezone info
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def ensure_naive_utc(dt: datetime) -> datetime:
    """
    Ensure a datetime object is timezone-naive UTC.
    
    Args:
        dt: Input datetime object
        
    Returns:
        datetime: Timezone-naive UTC datetime
    """
    if dt.tzinfo is not None:
        # Convert to UTC and remove timezone info
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt
