"""Early warning. We buy tracking; this module only decides when an ETA change matters."""
from dataclasses import dataclass


@dataclass(frozen=True)
class EtaUpdate:
    booking: str
    days_before_scheduled_arrival: int   # how early the new ETA became known (T minus this)
    delay_days: int                      # new ETA minus scheduled arrival


@dataclass(frozen=True)
class Alert:
    booking: str
    lead_days: int        # warning time before the scheduled arrival
    stockout_days: int    # days the line would stop with no action


def evaluate(update: EtaUpdate, safety_stock_days: int) -> Alert | None:
    """Alert only when the delay outruns the plant's safety stock."""
    if update.delay_days < 0 or safety_stock_days < 0:
        raise ValueError("delay_days and safety_stock_days must be non-negative")
    stockout = update.delay_days - safety_stock_days
    if stockout <= 0:
        return None
    return Alert(update.booking, update.days_before_scheduled_arrival, stockout)
