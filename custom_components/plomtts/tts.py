"""Support for the PlomTTS text-to-speech service."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from homeassistant.components.tts import (
    ATTR_VOICE,
    TextToSpeechEntity,
    TtsAudioType,
    Voice,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from plomtts import TTSClient, TTSError, VoiceResponse

from . import PlomTTSConfigEntry
from .const import (
    ATTR_CHUNK_LENGTH,
    ATTR_MAX_NEW_TOKENS,
    ATTR_REPETITION_PENALTY,
    ATTR_SEED,
    ATTR_TEMPERATURE,
    ATTR_TOP_P,
    CONF_CHUNK_LENGTH,
    CONF_MAX_NEW_TOKENS,
    CONF_REPETITION_PENALTY,
    CONF_SEED,
    CONF_TEMPERATURE,
    CONF_TOP_P,
    CONF_VOICE,
    DEFAULT_CHUNK_LENGTH,
    DEFAULT_MAX_NEW_TOKENS,
    DEFAULT_REPETITION_PENALTY,
    DEFAULT_SEED,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 0


def get_tts_parameters(options: Mapping[str, Any]) -> dict[str, Any]:
    """Extract TTS parameters from options."""
    return {
        "max_new_tokens": options.get(CONF_MAX_NEW_TOKENS, DEFAULT_MAX_NEW_TOKENS),
        "chunk_length": options.get(CONF_CHUNK_LENGTH, DEFAULT_CHUNK_LENGTH),
        "top_p": options.get(CONF_TOP_P, DEFAULT_TOP_P),
        "repetition_penalty": options.get(
            CONF_REPETITION_PENALTY, DEFAULT_REPETITION_PENALTY
        ),
        "temperature": options.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE),
        "seed": options.get(CONF_SEED, DEFAULT_SEED),
    }


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: PlomTTSConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up PlomTTS tts platform via config entry."""
    client = config_entry.runtime_data.client

    # Get voices from server
    try:
        voice_response = await hass.async_add_executor_job(client.list_voices)
        voices = voice_response.voices
    except TTSError as err:
        _LOGGER.error("Failed to get voices from PlomTTS server: %s", err)
        return

    default_voice_id = config_entry.options.get(CONF_VOICE)
    if not default_voice_id and voices:
        default_voice_id = voices[0].id

    tts_parameters = get_tts_parameters(config_entry.options)

    async_add_entities(
        [
            PlomTTSTTSEntity(
                client,
                voices,
                default_voice_id,
                config_entry.entry_id,
                config_entry.title,
                tts_parameters,
            )
        ]
    )


class PlomTTSTTSEntity(TextToSpeechEntity):
    """The PlomTTS API entity."""

    _attr_supported_options = [
        ATTR_VOICE,
        ATTR_MAX_NEW_TOKENS,
        ATTR_CHUNK_LENGTH,
        ATTR_TOP_P,
        ATTR_REPETITION_PENALTY,
        ATTR_TEMPERATURE,
        ATTR_SEED,
    ]
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        client: TTSClient,
        voices: list[VoiceResponse],
        default_voice_id: str | None,
        entry_id: str,
        title: str,
        tts_parameters: dict[str, Any],
    ) -> None:
        """Init PlomTTS TTS service."""
        self._client = client
        self._default_voice_id = default_voice_id
        self._voices = sorted(
            (Voice(v.id, v.name) for v in voices),
            key=lambda v: v.name,
        )
        # Default voice first
        if default_voice_id:
            voice_indices = [
                idx
                for idx, v in enumerate(self._voices)
                if v.voice_id == default_voice_id
            ]
            if voice_indices:
                self._voices.insert(0, self._voices.pop(voice_indices[0]))

        self._tts_parameters = tts_parameters

        # Entity attributes
        self._attr_unique_id = entry_id
        self._attr_name = title
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            manufacturer="PlomTTS",
            model="Fish Speech TTS",
            entry_type=DeviceEntryType.SERVICE,
        )
        # PlomTTS supports multiple languages through Fish Speech
        self._attr_supported_languages = ["en", "zh", "ja", "de", "fr", "ko", "es"]
        self._attr_default_language = "en"

    def async_get_supported_voices(self, language: str) -> list[Voice]:
        """Return a list of supported voices for a language."""
        return self._voices

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any]
    ) -> TtsAudioType:
        """Load tts audio file from the engine."""
        _LOGGER.debug("🎤 Getting TTS audio for: %s", message)
        _LOGGER.debug("🔧 Options: %s", options)

        voice_id = options.get(ATTR_VOICE, self._default_voice_id)
        if not voice_id:
            raise HomeAssistantError("No voice selected")

        # Build TTS parameters from options, falling back to defaults
        tts_params = {
            "max_new_tokens": options.get(
                ATTR_MAX_NEW_TOKENS, self._tts_parameters["max_new_tokens"]
            ),
            "chunk_length": options.get(
                ATTR_CHUNK_LENGTH, self._tts_parameters["chunk_length"]
            ),
            "top_p": options.get(ATTR_TOP_P, self._tts_parameters["top_p"]),
            "repetition_penalty": options.get(
                ATTR_REPETITION_PENALTY, self._tts_parameters["repetition_penalty"]
            ),
            "temperature": options.get(
                ATTR_TEMPERATURE, self._tts_parameters["temperature"]
            ),
            "seed": options.get(ATTR_SEED, self._tts_parameters["seed"]),
        }

        try:
            audio_bytes = await self.hass.async_add_executor_job(
                self._client.generate_speech, message, voice_id, **tts_params
            )
            _LOGGER.debug(
                "✅ Successfully generated %d bytes of audio", len(audio_bytes)
            )
        except TTSError as exc:
            _LOGGER.error("❌ Error during TTS processing: %s", exc)
            raise HomeAssistantError(f"TTS generation failed: {exc}") from exc

        return "mp3", audio_bytes
