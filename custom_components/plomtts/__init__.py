"""The PlomTTS text-to-speech integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from plomtts import TTSClient, TTSConnectionError, TTSError, VoiceResponse

from .const import CONF_SERVER_URL, DEFAULT_TIMEOUT

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.TTS, Platform.SENSOR]


@dataclass(kw_only=True, slots=True)
class PlomTTSData:
    """PlomTTS data type."""

    client: TTSClient
    voices: list[VoiceResponse]


type PlomTTSConfigEntry = ConfigEntry[PlomTTSData]


async def async_setup_entry(hass: HomeAssistant, entry: PlomTTSConfigEntry) -> bool:
    """Set up PlomTTS text-to-speech from a config entry."""
    _LOGGER.debug("🚀 Setting up PlomTTS integration for %s", entry.title)

    try:
        entry.add_update_listener(update_listener)

        server_url = entry.data[CONF_SERVER_URL]
        client = TTSClient(base_url=server_url, timeout=DEFAULT_TIMEOUT)

        # Test connection
        try:
            await hass.async_add_executor_job(client.health)
            _LOGGER.debug(
                "✅ Successfully connected to PlomTTS server at %s", server_url
            )
        except (TTSConnectionError, TTSError) as err:
            _LOGGER.error(
                "❌ Failed to connect to PlomTTS server at %s: %s", server_url, err
            )
            raise ConfigEntryNotReady("Failed to connect to PlomTTS server") from err

        # Fetch voices once at setup time — shared across platforms
        try:
            voice_response = await hass.async_add_executor_job(client.list_voices)
            voices = voice_response.voices
            _LOGGER.debug("✅ Loaded %d voices from PlomTTS server", len(voices))
        except (TTSConnectionError, TTSError) as err:
            _LOGGER.error("❌ Failed to fetch voices from PlomTTS server: %s", err)
            raise ConfigEntryNotReady("Failed to fetch voices from PlomTTS server") from err

        entry.runtime_data = PlomTTSData(client=client, voices=voices)
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

        _LOGGER.info("✅ PlomTTS integration setup completed for %s", entry.title)
        return True
    except Exception as err:
        _LOGGER.error("❌ Failed to setup PlomTTS integration: %s", err)
        raise


async def async_unload_entry(hass: HomeAssistant, entry: PlomTTSConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("🔄 Unloading PlomTTS integration for %s", entry.title)

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        _LOGGER.info("✅ PlomTTS integration unloaded successfully for %s", entry.title)
    else:
        _LOGGER.warning("⚠️ PlomTTS integration unload had issues for %s", entry.title)

    return unload_ok


async def update_listener(
    hass: HomeAssistant, config_entry: PlomTTSConfigEntry
) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)
