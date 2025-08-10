# 🎤 PlomTTS Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/plomdawg/plomtts-hass)

A Home Assistant custom component for Text-to-Speech (TTS) using [PlomTTS](https://github.com/plomdawg/plomtts) - a high-performance AI voice cloning server powered by fish-speech.

This integration provides feature parity with the ElevenLabs integration while supporting local, self-hosted voice generation.

## 🚀 Features

### 🎵 Voice Management
- **Auto-Discovery**: Automatically fetches available voices from your PlomTTS server
- **Voice Selection**: Runtime voice switching via TTS service options
- **Custom Voices**: Support for user-uploaded voice models
- **Voice Validation**: Automatic validation of server connectivity and voice availability

### 🏠 Home Assistant Integration  
- **Config Flow**: Easy setup through the Home Assistant UI
- **TTS Service**: Standard `tts.speak` service compatibility
- **Options Flow**: Configure default voices and server settings
- **Error Handling**: Robust error handling for server connectivity issues
- **HACS Compatible**: Install and update through HACS

### 🔧 Advanced Features
- **Local Hosting**: No cloud dependencies - run entirely on your network
- **Multiple Formats**: Support for WAV and MP3 audio output
- **Performance**: Optimized for local AI inference with GPU acceleration
- **Streaming**: Real-time audio generation (when supported by server)

## 📋 Requirements

### Prerequisites
- Home Assistant 2023.1 or later
- Running [PlomTTS server](https://github.com/plomdawg/plomtts) instance
- Network connectivity between Home Assistant and PlomTTS server

### PlomTTS Server Setup

Before using this integration, you need a running [PlomTTS server](https://github.com/plomdawg/plomtts).

## 📦 Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to `Integrations` 
3. Click the three dots (⋮) and select `Custom repositories`
4. Add this repository URL: `https://github.com/plomdawg/plomtts-hass`
5. Select `Integration` as the category
6. Click `ADD`
7. Find "PlomTTS" in the integration list and click `INSTALL`
8. Restart Home Assistant

### Manual Installation

1. Download this repository
2. Copy the `custom_components/plomtts` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## ⚙️ Configuration

### Initial Setup

1. Go to `Settings` → `Devices & Services`
2. Click `+ Add Integration`
3. Search for "PlomTTS" and select it
4. Enter your PlomTTS server details:
   - **Host**: IP address or hostname of your PlomTTS server (e.g., `192.168.1.100`)
   - **Port**: Port number (default: `8420`)
   - **Use HTTPS**: Enable if your server uses SSL/TLS
5. Click `Submit`

The integration will automatically:
- Test the connection to your PlomTTS server
- Discover available voices
- Set up the TTS entity

### Voice Configuration

After setup, you can configure voice settings:

1. Go to `Settings` → `Devices & Services` → `PlomTTS`
2. Click `Configure`
3. Select your default voice
4. Adjust voice parameters (if supported by your PlomTTS server)
5. Click `Submit`

## 🎯 Usage

### Basic TTS Service

Use the standard Home Assistant TTS service:

```yaml
service: tts.speak
target:
  entity_id: media_player.living_room_speaker
data:
  message: "Hello, this is PlomTTS speaking!"
  entity_id: tts.plomtts
```

### Voice Selection

Choose different voices at runtime:

```yaml
service: tts.speak
target:
  entity_id: media_player.living_room_speaker
data:
  message: "This message uses a specific voice"
  entity_id: tts.plomtts
  options:
    voice: "my_custom_voice"
```

### Advanced Options

```yaml
service: tts.speak
target:
  entity_id: media_player.living_room_speaker
data:
  message: "Advanced TTS with custom settings"
  entity_id: tts.plomtts
  options:
    voice: "my_custom_voice"
    speed: 1.2
    format: "mp3"
```

### Automation Example

```yaml
automation:
  - alias: "Doorbell Announcement"
    trigger:
      platform: state
      entity_id: binary_sensor.front_door
      to: "on"
    action:
      - service: tts.speak
        target:
          entity_id: media_player.all_speakers
        data:
          message: "Someone is at the front door"
          entity_id: tts.plomtts
          options:
            voice: "friendly_voice"
```
