"""Sensor platform for PlomTTS — voice list."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import PlomTTSConfigEntry
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: PlomTTSConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up PlomTTS sensor platform."""
    voices = config_entry.runtime_data.voices
    entry_id = config_entry.entry_id
    title = config_entry.title

    async_add_entities(
        [
            PlomTTSVoicesSensor(voices, entry_id, title),
        ]
    )


def _device_info(entry_id: str) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, entry_id)},
        manufacturer="PlomTTS",
        model="Fish Speech TTS",
        entry_type=DeviceEntryType.SERVICE,
    )


class PlomTTSVoicesSensor(SensorEntity):
    """Exposes the full list of available PlomTTS voices as sensor attributes.

    State  : number of voices
    Attributes:
      voice_ids  — list of voice IDs (use with Jinja `| random` for per-call variety)
      voices     — list of {id, name} dicts
    """

    _attr_should_poll = False
    _attr_icon = "mdi:account-voice"

    def __init__(self, voices, entry_id: str, title: str) -> None:
        self._voices = voices
        self._attr_unique_id = f"{entry_id}_voices"
        self._attr_name = f"{title} Voices"
        self._attr_device_info = _device_info(entry_id)

    @property
    def native_value(self) -> int:
        return len(self._voices)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "voice_ids": [v.id for v in self._voices],
            "voices": [{"id": v.id, "name": v.name} for v in self._voices],
        }


