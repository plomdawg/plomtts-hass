"""Config flow for PlomTTS text-to-speech integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import HomeAssistant
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
)
from plomtts import TTSClient, TTSConnectionError, TTSError

from . import PlomTTSConfigEntry
from .const import (
    CONF_CHUNK_LENGTH,
    CONF_CONFIGURE_VOICE,
    CONF_MAX_NEW_TOKENS,
    CONF_REPETITION_PENALTY,
    CONF_SEED,
    CONF_SERVER_URL,
    CONF_TEMPERATURE,
    CONF_TOP_P,
    CONF_VOICE,
    DEFAULT_CHUNK_LENGTH,
    DEFAULT_MAX_NEW_TOKENS,
    DEFAULT_REPETITION_PENALTY,
    DEFAULT_SEED,
    DEFAULT_SERVER_URL,
    DEFAULT_TEMPERATURE,
    DEFAULT_TIMEOUT,
    DEFAULT_TOP_P,
    DOMAIN,
)

USER_STEP_SCHEMA = vol.Schema(
    {vol.Required(CONF_SERVER_URL, default=DEFAULT_SERVER_URL): str}
)

_LOGGER = logging.getLogger(__name__)


async def get_voices(hass: HomeAssistant, server_url: str) -> dict[str, str]:
    """Get available voices as dict from PlomTTS server."""
    client = TTSClient(base_url=server_url, timeout=DEFAULT_TIMEOUT)

    # Test connection first
    await hass.async_add_executor_job(client.health)

    # Get voices
    voice_response = await hass.async_add_executor_job(client.list_voices)
    voices_dict = {
        voice.id: voice.name
        for voice in sorted(voice_response.voices, key=lambda v: v.name)
    }
    return voices_dict


class PlomTTSConfigFlow(ConfigFlow):
    """Handle a config flow for PlomTTS text-to-speech."""

    VERSION = 1
    domain = DOMAIN

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                voices = await get_voices(self.hass, user_input[CONF_SERVER_URL])
            except TTSConnectionError:
                errors["base"] = "cannot_connect"
            except TTSError:
                errors["base"] = "unknown"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected error during setup")
                errors["base"] = "unknown"
            else:
                if not voices:
                    errors["base"] = "no_voices"
                else:
                    return self.async_create_entry(
                        title="PlomTTS",
                        data=user_input,
                        options={CONF_VOICE: list(voices)[0]},
                    )
        return self.async_show_form(
            step_id="user", data_schema=USER_STEP_SCHEMA, errors=errors
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: PlomTTSConfigEntry,
    ) -> OptionsFlow:
        """Create the options flow."""
        return PlomTTSOptionsFlow(config_entry)


class PlomTTSOptionsFlow(OptionsFlow):
    """PlomTTS options flow."""

    def __init__(self, config_entry: PlomTTSConfigEntry) -> None:
        """Initialize options flow."""
        self.server_url: str = config_entry.data[CONF_SERVER_URL]
        # id -> name
        self.voices: dict[str, str] = {}
        self.voice: str | None = None

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if not self.voices:
            try:
                self.voices = await get_voices(self.hass, self.server_url)
            except (TTSConnectionError, TTSError):
                return self.async_abort(reason="cannot_connect")

        if not self.voices:
            return self.async_abort(reason="no_voices")

        if user_input is not None:
            self.voice = user_input[CONF_VOICE]
            configure_voice = user_input.pop(CONF_CONFIGURE_VOICE)
            if configure_voice:
                return await self.async_step_voice_settings()
            return self.async_create_entry(
                title="PlomTTS",
                data=user_input,
            )

        schema = self.plomtts_config_option_schema()
        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )

    def plomtts_config_option_schema(self) -> vol.Schema:
        """PlomTTS options schema."""
        return self.add_suggested_values_to_schema(
            vol.Schema(
                {
                    vol.Required(
                        CONF_VOICE,
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(label=voice_name, value=voice_id)
                                for voice_id, voice_name in self.voices.items()
                            ]
                        )
                    ),
                    vol.Required(CONF_CONFIGURE_VOICE, default=False): bool,
                }
            ),
            self.config_entry.options,
        )

    async def async_step_voice_settings(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle voice settings."""
        if user_input is not None:
            user_input[CONF_VOICE] = self.voice
            return self.async_create_entry(
                title="PlomTTS",
                data=user_input,
            )
        return self.async_show_form(
            step_id="voice_settings",
            data_schema=self.plomtts_config_options_voice_schema(),
        )

    def plomtts_config_options_voice_schema(self) -> vol.Schema:
        """PlomTTS options voice schema."""
        return vol.Schema(
            {
                vol.Optional(
                    CONF_MAX_NEW_TOKENS,
                    default=self.config_entry.options.get(
                        CONF_MAX_NEW_TOKENS, DEFAULT_MAX_NEW_TOKENS
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=0)),
                vol.Optional(
                    CONF_CHUNK_LENGTH,
                    default=self.config_entry.options.get(
                        CONF_CHUNK_LENGTH, DEFAULT_CHUNK_LENGTH
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1000)),
                vol.Optional(
                    CONF_TOP_P,
                    default=self.config_entry.options.get(CONF_TOP_P, DEFAULT_TOP_P),
                ): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=1.0)),
                vol.Optional(
                    CONF_REPETITION_PENALTY,
                    default=self.config_entry.options.get(
                        CONF_REPETITION_PENALTY, DEFAULT_REPETITION_PENALTY
                    ),
                ): vol.All(vol.Coerce(float), vol.Range(min=1.0, max=2.0)),
                vol.Optional(
                    CONF_TEMPERATURE,
                    default=self.config_entry.options.get(
                        CONF_TEMPERATURE, DEFAULT_TEMPERATURE
                    ),
                ): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=2.0)),
                vol.Optional(
                    CONF_SEED,
                    default=self.config_entry.options.get(CONF_SEED, DEFAULT_SEED),
                ): vol.All(vol.Coerce(int), vol.Range(min=0)),
            }
        )
