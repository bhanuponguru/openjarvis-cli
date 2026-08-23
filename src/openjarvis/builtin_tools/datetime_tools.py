import datetime as dt

import pytz

from openjarvis.tools import tool


@tool()
def get_current_datetime(timezone: str = "UTC") -> str:
    """Get the current date and time in a specified timezone.

    Args:
        timezone: IANA timezone name (e.g., "UTC", "America/New_York", "Europe/London").

    Returns:
        ISO 8601 datetime string with weekday.
    """
    try:
        tz = pytz.timezone(timezone)
    except pytz.exceptions.UnknownTimeZoneError:
        return f"Error: Unknown timezone '{timezone}'. Use IANA format like 'UTC' or 'America/New_York'."

    now = dt.datetime.now(tz)
    weekday = now.strftime("%A")
    return f"{now.isoformat()} ({weekday})"

@tool()
def date_arithmetic(date_str: str, days: int = 0, hours: int = 0) -> str:
    """Add or subtract days and hours from a date.

    Args:
        date_str: ISO 8601 datetime string (e.g., "2026-08-13T10:30:00").
        days: Number of days to add (negative to subtract).
        hours: Number of hours to add (negative to subtract).

    Returns:
        ISO 8601 datetime string of the result.
    """
    try:
        if "T" in date_str:
            dt_obj = dt.datetime.fromisoformat(date_str)
        else:
            dt_obj = dt.datetime.fromisoformat(date_str + "T00:00:00")
    except ValueError:
        return f"Error: Invalid date format '{date_str}'. Use ISO 8601 format (e.g., '2026-08-13' or '2026-08-13T10:30:00')."

    result = dt_obj + dt.timedelta(days=days, hours=hours)
    return result.isoformat()

@tool()
def format_datetime(date_str: str, fmt: str) -> str:
    """Reformat a date string to a human-readable format.

    Args:
        date_str: ISO 8601 datetime string (e.g., "2026-08-13T10:30:00").
        fmt: Python strftime format string (e.g., "%B %d, %Y" for "August 13, 2026").

    Returns:
        Formatted datetime string.
    """
    try:
        if "T" in date_str:
            dt_obj = dt.datetime.fromisoformat(date_str)
        else:
            dt_obj = dt.datetime.fromisoformat(date_str + "T00:00:00")
    except ValueError:
        return f"Error: Invalid date format '{date_str}'."

    try:
        return dt_obj.strftime(fmt)
    except Exception as e:
        return f"Error: Invalid format string '{fmt}': {e}"

@tool()
def days_between(date_a: str, date_b: str) -> int:
    """Calculate the number of days between two dates.

    Args:
        date_a: ISO 8601 date/datetime string.
        date_b: ISO 8601 date/datetime string.

    Returns:
        Number of days between the dates (positive if date_b > date_a).

    Raises:
        ValueError: If either date string is not a valid ISO 8601 format.
    """
    try:
        if "T" in date_a:
            dt_a = dt.datetime.fromisoformat(date_a)
        else:
            dt_a = dt.datetime.fromisoformat(date_a + "T00:00:00")

        if "T" in date_b:
            dt_b = dt.datetime.fromisoformat(date_b)
        else:
            dt_b = dt.datetime.fromisoformat(date_b + "T00:00:00")
    except ValueError as exc:
        raise ValueError(f"Invalid date format: {exc}") from exc

    return (dt_b - dt_a).days
