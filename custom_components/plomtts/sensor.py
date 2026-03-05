"""Sensor platform for PlomTTS — voice list and random voice selection."""

from __future__ import annotations

import logging
import random
from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import PlomTTSConfigEntry
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=5)


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
            PlomTTSRandomVoiceSensor(voices, entry_id, title),
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


class PlomTTSRandomVoiceSensor(SensorEntity):
    """Rolls a new random PlomTTS voice every few seconds.

    Use `states('sensor.plomtts_random_voice')` in TTS automations to get a
    rotating voice.  For a fresh voice on every single call, use the voices
    sensor instead:
        voice: "{{ state_attr('sensor.plomtts_voices', 'voice_ids') | random }}"
    """

    _attr_should_poll = True
    _attr_icon = "mdi:dice-multiple"

    def __init__(self, voices, entry_id: str, title: str) -> None:
        self._voices = voices
        self._attr_unique_id = f"{entry_id}_random_voice"
        self._attr_name = f"{title} Random Voice"
        self._attr_device_info = _device_info(entry_id)
        self._current_voice: str | None = (
            random.choice(self._voices).id if self._voices else None
        )

    @property
    def native_value(self) -> str | None:
        return self._current_voice

    def update(self) -> None:
        if self._voices:
            self._current_voice = random.choice(self._voices).id
            _LOGGER.debug("🎲 Random voice rolled: %s", self._current_voice)
