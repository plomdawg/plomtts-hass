"""Constants for the PlomTTS text-to-speech integration."""

DOMAIN = "plomtts"

# Configuration keys
CONF_SERVER_URL = "server_url"
CONF_VOICE = "voice"
CONF_CONFIGURE_VOICE = "configure_voice"

# TTS parameters
CONF_MAX_NEW_TOKENS = "max_new_tokens"
CONF_CHUNK_LENGTH = "chunk_length"
CONF_TOP_P = "top_p"
CONF_REPETITION_PENALTY = "repetition_penalty"
CONF_TEMPERATURE = "temperature"
CONF_SEED = "seed"

# Attribute keys
ATTR_VOICE = "voice"
ATTR_MAX_NEW_TOKENS = "max_new_tokens"
ATTR_CHUNK_LENGTH = "chunk_length"
ATTR_TOP_P = "top_p"
ATTR_REPETITION_PENALTY = "repetition_penalty"
ATTR_TEMPERATURE = "temperature"
ATTR_SEED = "seed"

# Default values
DEFAULT_SERVER_URL = "http://localhost:8420"
DEFAULT_MAX_NEW_TOKENS = 0
DEFAULT_CHUNK_LENGTH = 200
DEFAULT_TOP_P = 0.7
DEFAULT_REPETITION_PENALTY = 1.2
DEFAULT_TEMPERATURE = 0.7
DEFAULT_SEED = 0

# Timeouts
DEFAULT_TIMEOUT = 30.0
