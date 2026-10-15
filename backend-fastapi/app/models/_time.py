from datetime import datetime, timezone


def utcnow() -> datetime:
    """返回不带时区的 UTC 时间（兼容 MySQL DATETIME 列，规避 3.12+ utcnow 弃用）"""
    return datetime.now(timezone.utc).replace(tzinfo=None)
