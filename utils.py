from flask import request

def build_format_string(resolution=None):
    if resolution:
        return f"bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]/best"
    return "bestvideo+bestaudio/best"

def get_ip():
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr

def format_time(seconds):
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    parts = []
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if sec or not parts:
        parts.append(f"{sec} second{'s' if sec != 1 else ''}")

    return " ".join(parts)