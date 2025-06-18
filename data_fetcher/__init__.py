"""Backward compatibility imports for legacy modules."""

from fetchers.zacks import fetch_zacks_rank
from fetchers.tipranks import fetch_tipranks_data

__all__ = ["fetch_zacks_rank", "fetch_tipranks_data"]
