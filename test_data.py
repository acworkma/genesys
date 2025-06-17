"""
Sample test data for Azure Speech Service testing.

This module contains sample texts and configurations for testing
Speech-to-Text and Text-to-Speech functionality.
"""

# Sample texts for Text-to-Speech testing
TTS_TEST_TEXTS = [
    {
        "name": "simple_greeting",
        "text": "Hello, this is a test of the Azure Speech Service.",
        "language": "en-US",
        "voice": "en-US-JennyNeural"
    },
    {
        "name": "multilingual_test",
        "text": "Bonjour, ceci est un test du service Azure Speech.",
        "language": "fr-FR",
        "voice": "fr-FR-DeniseNeural"
    },
    {
        "name": "technical_text",
        "text": "The Azure Speech Service provides speech-to-text and text-to-speech capabilities using advanced machine learning models.",
        "language": "en-US",
        "voice": "en-US-AriaNeural"
    },
    {
        "name": "numbers_and_punctuation",
        "text": "The temperature is 72.5 degrees Fahrenheit, or about 22.5 degrees Celsius. That's quite comfortable!",
        "language": "en-US",
        "voice": "en-US-GuyNeural"
    },
    {
        "name": "ssml_test",
        "text": """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
            <voice name="en-US-JennyNeural">
                <prosody rate="slow" pitch="low">
                    This text is spoken slowly and with a low pitch.
                </prosody>
                <break time="1s"/>
                <prosody rate="fast" pitch="high">
                    This text is spoken quickly and with a high pitch!
                </prosody>
            </voice>
        </speak>""",
        "language": "en-US",
        "voice": "en-US-JennyNeural",
        "format": "ssml"
    }
]

# Configuration for different audio formats for TTS
TTS_OUTPUT_FORMATS = [
    {
        "name": "riff_16khz_16bit_mono_pcm",
        "format": "riff-16khz-16bit-mono-pcm",
        "description": "16kHz 16-bit mono PCM"
    },
    {
        "name": "riff_24khz_16bit_mono_pcm",
        "format": "riff-24khz-16bit-mono-pcm", 
        "description": "24kHz 16-bit mono PCM"
    },
    {
        "name": "audio_16khz_32kbitrate_mono_mp3",
        "format": "audio-16khz-32kbitrate-mono-mp3",
        "description": "16kHz 32kbps mono MP3"
    },
    {
        "name": "ogg_16khz_16bit_mono_opus",
        "format": "ogg-16khz-16bit-mono-opus",
        "description": "16kHz 16-bit mono Opus"
    }
]

# Sample languages and voices for testing
SUPPORTED_VOICES = [
    {"language": "en-US", "voice": "en-US-JennyNeural", "gender": "Female"},
    {"language": "en-US", "voice": "en-US-GuyNeural", "gender": "Male"},
    {"language": "en-US", "voice": "en-US-AriaNeural", "gender": "Female"},
    {"language": "en-GB", "voice": "en-GB-SoniaNeural", "gender": "Female"},
    {"language": "en-GB", "voice": "en-GB-RyanNeural", "gender": "Male"},
    {"language": "fr-FR", "voice": "fr-FR-DeniseNeural", "gender": "Female"},
    {"language": "fr-FR", "voice": "fr-FR-HenriNeural", "gender": "Male"},
    {"language": "de-DE", "voice": "de-DE-KatjaNeural", "gender": "Female"},
    {"language": "de-DE", "voice": "de-DE-ConradNeural", "gender": "Male"},
    {"language": "es-ES", "voice": "es-ES-ElviraNeural", "gender": "Female"},
    {"language": "es-ES", "voice": "es-ES-AlvaroNeural", "gender": "Male"},
    {"language": "ja-JP", "voice": "ja-JP-NanamiNeural", "gender": "Female"},
    {"language": "ja-JP", "voice": "ja-JP-KeitaNeural", "gender": "Male"},
]

# Configuration for Speech-to-Text testing
STT_TEST_CONFIG = {
    "languages": ["en-US", "en-GB", "fr-FR", "de-DE", "es-ES", "ja-JP"],
    "sample_rates": [16000, 24000, 48000],
    "audio_formats": ["wav", "mp3", "ogg"],
    "recognition_modes": ["interactive", "conversation", "dictation"],
    "profanity_options": ["masked", "removed", "raw"]
}

# Test phrases for different languages (for STT validation)
STT_EXPECTED_PHRASES = {
    "en-US": [
        "Hello world",
        "This is a test",
        "Azure Speech Service",
        "One two three four five"
    ],
    "en-GB": [
        "Good morning",
        "Weather is lovely today",
        "Testing speech recognition"
    ],
    "fr-FR": [
        "Bonjour le monde",
        "Ceci est un test",
        "Service de reconnaissance vocale"
    ],
    "de-DE": [
        "Hallo Welt",
        "Dies ist ein Test",
        "Spracherkennungsdienst"
    ]
}

# Error test cases - these should potentially fail or produce specific responses
ERROR_TEST_CASES = [
    {
        "name": "empty_audio",
        "description": "Test with empty audio data",
        "audio_data": b"",
        "expected_error": True
    },
    {
        "name": "invalid_format",
        "description": "Test with invalid audio format",
        "content_type": "audio/invalid",
        "expected_error": True
    },
    {
        "name": "unsupported_language",
        "description": "Test with unsupported language code",
        "language": "xx-XX",
        "expected_error": True
    },
    {
        "name": "malformed_ssml",
        "description": "Test with malformed SSML",
        "text": "<speak><voice>Unclosed tags",
        "expected_error": True
    }
]

def get_test_text(test_name: str) -> dict:
    """Get test text configuration by name."""
    for test in TTS_TEST_TEXTS:
        if test["name"] == test_name:
            return test
    return TTS_TEST_TEXTS[0]  # Default to first test

def get_voice_by_language(language: str, gender: str = None) -> str:
    """Get a voice name for a specific language and optional gender."""
    voices = [v for v in SUPPORTED_VOICES if v["language"] == language]
    if gender:
        voices = [v for v in voices if v["gender"].lower() == gender.lower()]
    
    return voices[0]["voice"] if voices else "en-US-JennyNeural"

def get_output_format(format_name: str) -> str:
    """Get output format string by name."""
    for fmt in TTS_OUTPUT_FORMATS:
        if fmt["name"] == format_name:
            return fmt["format"]
    return "riff-16khz-16bit-mono-pcm"  # Default format
