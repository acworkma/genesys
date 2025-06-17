#!/usr/bin/env python3
"""
Azure Speech Service Endpoint Tester

This script tests Azure Speech Service endpoints by issuing token requests
and performing basic speech-to-text operations.

Required environment variables:
- AZURE_SPEECH_KEY: Your Azure Speech service subscription key
- AZURE_SPEECH_REGION: Your Azure Speech service region (e.g., eastus, westus2)

Optional environment variables:
- AZURE_SPEECH_ENDPOINT: Custom endpoint URL (overrides region-based URL)
"""

import os
import sys
import json
import time
import requests
import base64
import wave
import struct
from typing import Optional, Dict, Any, List
import logging

# Import test data
try:
    from test_data import TTS_TEST_TEXTS, STT_TEST_CONFIG, get_test_text, get_voice_by_language
except ImportError:
    # Fallback if test_data module is not available
    TTS_TEST_TEXTS = []
    STT_TEST_CONFIG = {}
    def get_test_text(name): return {"text": "Hello world", "voice": "en-US-JennyNeural", "language": "en-US"}
    def get_voice_by_language(lang, gender=None): return "en-US-JennyNeural"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AzureSpeechTester:
    """Class to test Azure Speech Service endpoints."""
    
    def __init__(self):
        """Initialize the tester with environment variables."""
        self.subscription_key = os.getenv('AZURE_SPEECH_KEY')
        self.region = os.getenv('AZURE_SPEECH_REGION')
        self.custom_endpoint = os.getenv('AZURE_SPEECH_ENDPOINT')
        
        # Validate required environment variables
        if not self.subscription_key:
            raise ValueError("AZURE_SPEECH_KEY environment variable is required")
        
        if not self.region and not self.custom_endpoint:
            raise ValueError("Either AZURE_SPEECH_REGION or AZURE_SPEECH_ENDPOINT must be set")
        
        # Set up endpoints
        if self.custom_endpoint:
            self.token_endpoint = self.custom_endpoint
        else:
            self.token_endpoint = f"https://{self.region}.api.cognitive.microsoft.com/sts/v1.0/issuetoken"
        
        # Speech service endpoints
        self.stt_endpoint = f"https://{self.region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
        self.tts_endpoint = f"https://{self.region}.tts.speech.microsoft.com/cognitiveservices/v1"
        
        logger.info(f"Initialized Azure Speech Tester")
        logger.info(f"Token endpoint: {self.token_endpoint}")
        logger.info(f"STT endpoint: {self.stt_endpoint}")
        logger.info(f"TTS endpoint: {self.tts_endpoint}")
        logger.info(f"Region: {self.region}")
    
    def get_access_token(self) -> Optional[str]:
        """
        Get an access token from the Azure Speech service.
        
        Returns:
            str: Access token if successful, None otherwise
        """
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            logger.info("Requesting access token...")
            response = requests.post(
                self.token_endpoint,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                token = response.text
                logger.info("Successfully obtained access token")
                return token
            else:
                logger.error(f"Failed to get token. Status: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return None
    
    def test_endpoint_connectivity(self) -> bool:
        """
        Test basic connectivity to the Azure Speech endpoint.
        
        Returns:
            bool: True if endpoint is reachable, False otherwise
        """
        try:
            logger.info("Testing endpoint connectivity...")
            response = requests.get(
                self.token_endpoint.replace('/issuetoken', ''),
                timeout=5
            )
            
            # We expect a 404 or similar for the base URL, but it should be reachable
            if response.status_code in [200, 404, 405]:
                logger.info("Endpoint is reachable")
                return True
            else:
                logger.warning(f"Unexpected status code: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Connectivity test failed: {str(e)}")
            return False
    
    def validate_token_format(self, token: str) -> bool:
        """
        Validate the format of the received token.
        
        Args:
            token (str): The token to validate
            
        Returns:
            bool: True if token format appears valid
        """
        if not token:
            return False
        
        # Azure tokens are typically JWT tokens or opaque strings
        # Basic validation: should be a non-empty string with reasonable length
        if len(token) < 50:  # Tokens should be longer than this
            logger.warning("Token appears too short")
            return False
        
        # Check for common JWT characteristics (optional)
        if token.count('.') == 2:
            logger.info("Token appears to be in JWT format")
        else:
            logger.info("Token appears to be in opaque format")
        
        return True
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """
        Run a comprehensive test of the Azure Speech endpoint.
        
        Returns:
            dict: Test results
        """
        results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'endpoint': self.token_endpoint,
            'region': self.region,
            'tests': {}
        }
        
        # Test 1: Endpoint connectivity
        logger.info("=== Running Endpoint Connectivity Test ===")
        connectivity_result = self.test_endpoint_connectivity()
        results['tests']['connectivity'] = {
            'passed': connectivity_result,
            'description': 'Basic endpoint reachability test'
        }
        
        # Test 2: Token acquisition
        logger.info("=== Running Token Acquisition Test ===")
        token = self.get_access_token()
        token_acquisition_passed = token is not None
        results['tests']['token_acquisition'] = {
            'passed': token_acquisition_passed,
            'description': 'Access token request test'
        }
        
        # Test 3: Token validation
        if token:
            logger.info("=== Running Token Validation Test ===")
            token_valid = self.validate_token_format(token)
            results['tests']['token_validation'] = {
                'passed': token_valid,
                'description': 'Token format validation test',
                'token_length': len(token),
                'token_preview': token[:20] + '...' if len(token) > 20 else token
            }
        else:
            results['tests']['token_validation'] = {
                'passed': False,
                'description': 'Token format validation test',
                'error': 'No token available for validation'
            }
        
        # Test 4: STT endpoint connectivity
        logger.info("=== Running STT Endpoint Connectivity Test ===")
        stt_connectivity_result = self.test_stt_endpoint_connectivity()
        results['tests']['stt_connectivity'] = {
            'passed': stt_connectivity_result,
            'description': 'Speech-to-Text endpoint reachability test'
        }
        
        # Test 5: TTS endpoint connectivity
        logger.info("=== Running TTS Endpoint Connectivity Test ===")
        tts_connectivity_result = self.test_tts_endpoint_connectivity()
        results['tests']['tts_connectivity'] = {
            'passed': tts_connectivity_result,
            'description': 'Text-to-Speech endpoint reachability test'
        }
        
        # Test 6: Speech-to-Text functionality (only if token is available)
        if token:
            logger.info("=== Running Speech-to-Text Tests ===")
            stt_result = self.run_multiple_stt_tests(token)
            results['tests']['speech_to_text'] = {
                'passed': stt_result['passed'],
                'description': f'Speech-to-Text API functionality test ({stt_result["test_count"]} tests)',
                'test_count': stt_result['test_count'],
                'passed_count': stt_result['passed_count'],
                'failed_count': stt_result['failed_count'],
                'details': stt_result['test_results']
            }
        else:
            results['tests']['speech_to_text'] = {
                'passed': False,
                'description': 'Speech-to-Text API functionality test',
                'error': 'No token available for STT test'
            }
        
        # Test 7: Text-to-Speech functionality (only if token is available)
        if token:
            logger.info("=== Running Text-to-Speech Tests ===")
            tts_result = self.run_multiple_tts_tests(token)
            results['tests']['text_to_speech'] = {
                'passed': tts_result['passed'],
                'description': f'Text-to-Speech API functionality test ({tts_result["test_count"]} tests)',
                'test_count': tts_result['test_count'],
                'passed_count': tts_result['passed_count'],
                'failed_count': tts_result['failed_count'],
                'details': tts_result['test_results']
            }
        else:
            results['tests']['text_to_speech'] = {
                'passed': False,
                'description': 'Text-to-Speech API functionality test',
                'error': 'No token available for TTS test'
            }
        
        # Calculate overall success
        total_tests = len(results['tests'])
        passed_tests = sum(1 for test in results['tests'].values() if test['passed'])
        results['summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': f"{(passed_tests/total_tests)*100:.1f}%",
            'overall_success': passed_tests == total_tests
        }
        
        return results
    
    def generate_test_audio(self, duration_seconds: float = 2.0, sample_rate: int = 16000, frequency: float = 440.0) -> bytes:
        """
        Generate a simple test audio file (sine wave) for STT testing.
        
        Args:
            duration_seconds (float): Duration of the audio in seconds
            sample_rate (int): Sample rate in Hz
            frequency (float): Frequency of the sine wave in Hz
            
        Returns:
            bytes: WAV audio data
        """
        import math
        
        # Generate a sine wave
        frames = int(duration_seconds * sample_rate)
        
        # Create audio data
        audio_data = []
        for i in range(frames):
            # Generate sine wave
            sample = int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
            audio_data.append(struct.pack('<h', sample))
        
        # Create WAV file in memory
        import io
        wav_buffer = io.BytesIO()
        
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(b''.join(audio_data))
        
        return wav_buffer.getvalue()
    
    def test_speech_to_text(self, token: str) -> Dict[str, Any]:
        """
        Test Speech-to-Text endpoint with generated audio.
        
        Args:
            token (str): Access token for authentication
            
        Returns:
            dict: Test results including recognition results
        """
        try:
            logger.info("Testing Speech-to-Text endpoint...")
            
            # Generate test audio
            audio_data = self.generate_test_audio(duration_seconds=1.0)
            
            # Prepare headers
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'audio/wav; codecs=audio/pcm; samplerate=16000',
                'Accept': 'application/json'
            }
            
            # Prepare query parameters
            params = {
                'language': 'en-US',
                'format': 'detailed',
                'profanity': 'masked'
            }
            
            # Make the request
            response = requests.post(
                self.stt_endpoint,
                headers=headers,
                params=params,
                data=audio_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("STT test completed successfully")
                return {
                    'passed': True,
                    'response_code': response.status_code,
                    'recognition_result': result,
                    'audio_duration': '1.0 seconds'
                }
            else:
                logger.error(f"STT test failed. Status: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return {
                    'passed': False,
                    'response_code': response.status_code,
                    'error': response.text
                }
                
        except Exception as e:
            logger.error(f"STT test error: {str(e)}")
            return {
                'passed': False,
                'error': str(e)
            }
    
    def test_text_to_speech(self, token: str, test_name: str = "simple_greeting") -> Dict[str, Any]:
        """
        Test Text-to-Speech endpoint with sample text.
        
        Args:
            token (str): Access token for authentication
            test_name (str): Name of test case to use from test_data
            
        Returns:
            dict: Test results including audio generation results
        """
        try:
            logger.info(f"Testing Text-to-Speech endpoint with test case: {test_name}")
            
            # Get test configuration
            test_config = get_test_text(test_name)
            
            # Prepare SSML or plain text
            if test_config.get('format') == 'ssml':
                content = test_config['text']
                content_type = 'application/ssml+xml'
            else:
                # Create SSML wrapper for plain text
                content = f"""
                <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='{test_config['language']}'>
                    <voice name='{test_config['voice']}'>
                        {test_config['text']}
                    </voice>
                </speak>
                """
                content_type = 'application/ssml+xml'
            
            # Prepare headers
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': content_type,
                'X-Microsoft-OutputFormat': 'riff-16khz-16bit-mono-pcm',
                'User-Agent': 'Azure-Speech-Tester/1.0'
            }
            
            # Make the request
            response = requests.post(
                self.tts_endpoint,
                headers=headers,
                data=content.encode('utf-8'),
                timeout=30
            )
            
            if response.status_code == 200:
                audio_size = len(response.content)
                logger.info(f"TTS test completed successfully. Audio size: {audio_size} bytes")
                return {
                    'passed': True,
                    'response_code': response.status_code,
                    'audio_size_bytes': audio_size,
                    'content_type': response.headers.get('Content-Type', 'Unknown'),
                    'text_input': test_config['text'][:50] + '...' if len(test_config['text']) > 50 else test_config['text'],
                    'voice_used': test_config['voice'],
                    'language': test_config['language'],
                    'test_case': test_name
                }
            else:
                logger.error(f"TTS test failed. Status: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return {
                    'passed': False,
                    'response_code': response.status_code,
                    'error': response.text,
                    'test_case': test_name
                }
                
        except Exception as e:
            logger.error(f"TTS test error: {str(e)}")
            return {
                'passed': False,
                'error': str(e),
                'test_case': test_name
            }
    
    def test_stt_endpoint_connectivity(self) -> bool:
        """
        Test STT endpoint connectivity.
        
        Returns:
            bool: True if endpoint is reachable
        """
        try:
            logger.info("Testing STT endpoint connectivity...")
            # Make a simple GET request to check connectivity
            response = requests.get(
                self.stt_endpoint.replace('/speech/recognition/conversation/cognitiveservices/v1', ''),
                timeout=5
            )
            
            # We expect a 404 or similar, but it should be reachable
            if response.status_code in [200, 404, 405]:
                logger.info("STT endpoint is reachable")
                return True
            else:
                logger.warning(f"STT endpoint unexpected status: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"STT connectivity test failed: {str(e)}")
            return False
    
    def test_tts_endpoint_connectivity(self) -> bool:
        """
        Test TTS endpoint connectivity.
        
        Returns:
            bool: True if endpoint is reachable
        """
        try:
            logger.info("Testing TTS endpoint connectivity...")
            # Make a simple GET request to check connectivity
            response = requests.get(
                self.tts_endpoint.replace('/cognitiveservices/v1', ''),
                timeout=5
            )
            
            # We expect a 404 or similar, but it should be reachable
            if response.status_code in [200, 404, 405]:
                logger.info("TTS endpoint is reachable")
                return True
            else:
                logger.warning(f"TTS endpoint unexpected status: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"TTS connectivity test failed: {str(e)}")
            return False
    
    def run_multiple_tts_tests(self, token: str) -> Dict[str, Any]:
        """
        Run multiple TTS tests with different configurations.
        
        Args:
            token (str): Access token for authentication
            
        Returns:
            dict: Combined test results
        """
        if not TTS_TEST_TEXTS:
            # Fallback to single test if test data is not available
            return self.test_text_to_speech(token)
        
        logger.info("Running multiple TTS tests...")
        results = {
            'passed': True,
            'test_count': 0,
            'passed_count': 0,
            'failed_count': 0,
            'test_results': []
        }
        
        # Test with different configurations
        test_cases = ['simple_greeting', 'technical_text', 'numbers_and_punctuation']
        available_tests = [t['name'] for t in TTS_TEST_TEXTS]
        
        for test_case in test_cases:
            if test_case in available_tests:
                logger.info(f"Running TTS test: {test_case}")
                test_result = self.test_text_to_speech(token, test_case)
                results['test_results'].append(test_result)
                results['test_count'] += 1
                
                if test_result['passed']:
                    results['passed_count'] += 1
                else:
                    results['failed_count'] += 1
                    results['passed'] = False
        
        # If no specific tests available, run default test
        if results['test_count'] == 0:
            default_result = self.test_text_to_speech(token)
            results['test_results'].append(default_result)
            results['test_count'] = 1
            results['passed_count'] = 1 if default_result['passed'] else 0
            results['failed_count'] = 0 if default_result['passed'] else 1
            results['passed'] = default_result['passed']
        
        return results
    
    def run_multiple_stt_tests(self, token: str) -> Dict[str, Any]:
        """
        Run multiple STT tests with different audio configurations.
        
        Args:
            token (str): Access token for authentication
            
        Returns:
            dict: Combined test results
        """
        logger.info("Running multiple STT tests...")
        results = {
            'passed': True,
            'test_count': 0,
            'passed_count': 0,
            'failed_count': 0,
            'test_results': []
        }
        
        # Test with different audio durations and frequencies
        test_configs = [
            {'duration': 1.0, 'frequency': 440, 'name': 'short_tone'},
            {'duration': 2.0, 'frequency': 880, 'name': 'medium_tone'},
            {'duration': 0.5, 'frequency': 220, 'name': 'brief_tone'}
        ]
        
        for config in test_configs:
            try:
                logger.info(f"Running STT test: {config['name']}")
                
                # Generate test audio with specific parameters
                audio_data = self.generate_test_audio(
                    duration_seconds=config['duration'],
                    frequency=config['frequency']
                )
                
                test_result = self.test_speech_to_text_with_audio(token, audio_data, config['name'])
                results['test_results'].append(test_result)
                results['test_count'] += 1
                
                if test_result['passed']:
                    results['passed_count'] += 1
                else:
                    results['failed_count'] += 1
                    results['passed'] = False
                    
            except Exception as e:
                logger.error(f"STT test {config['name']} failed: {str(e)}")
                results['test_results'].append({
                    'passed': False,
                    'error': str(e),
                    'test_name': config['name']
                })
                results['test_count'] += 1
                results['failed_count'] += 1
                results['passed'] = False
        
        return results
    
    def test_speech_to_text_with_audio(self, token: str, audio_data: bytes, test_name: str = "audio_test") -> Dict[str, Any]:
        """
        Test Speech-to-Text endpoint with provided audio data.
        
        Args:
            token (str): Access token for authentication
            audio_data (bytes): Audio data to send for recognition
            test_name (str): Name of the test for identification
            
        Returns:
            dict: Test results including recognition results
        """
        try:
            logger.info(f"Testing Speech-to-Text with audio test: {test_name}")
            
            # Prepare headers
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'audio/wav; codecs=audio/pcm; samplerate=16000',
                'Accept': 'application/json'
            }
            
            # Prepare query parameters
            params = {
                'language': 'en-US',
                'format': 'detailed',
                'profanity': 'masked'
            }
            
            # Make the request
            response = requests.post(
                self.stt_endpoint,
                headers=headers,
                params=params,
                data=audio_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"STT test '{test_name}' completed successfully")
                return {
                    'passed': True,
                    'response_code': response.status_code,
                    'recognition_result': result,
                    'audio_size_bytes': len(audio_data),
                    'test_name': test_name
                }
            else:
                logger.error(f"STT test '{test_name}' failed. Status: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return {
                    'passed': False,
                    'response_code': response.status_code,
                    'error': response.text,
                    'test_name': test_name
                }
                
        except Exception as e:
            logger.error(f"STT test '{test_name}' error: {str(e)}")
            return {
                'passed': False,
                'error': str(e),
                'test_name': test_name
            }

def print_test_results(results: Dict[str, Any]):
        """Print formatted test results."""
        print("\n" + "="*60)
        print("AZURE SPEECH SERVICE TEST RESULTS")
        print("="*60)
        print(f"Timestamp: {results['timestamp']}")
        print(f"Endpoint: {results['endpoint']}")
        print(f"Region: {results['region']}")
        print("\nTest Results:")
        print("-" * 40)
        
        for test_name, test_data in results['tests'].items():
            status = "✅ PASS" if test_data['passed'] else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            print(f"  Description: {test_data['description']}")
            
            if 'error' in test_data:
                print(f"  Error: {test_data['error']}")
            
            if 'token_length' in test_data:
                print(f"  Token Length: {test_data['token_length']}")
                print(f"  Token Preview: {test_data['token_preview']}")
            
            if 'response_code' in test_data:
                print(f"  Response Code: {test_data['response_code']}")
            
            if 'audio_size_bytes' in test_data:
                print(f"  Generated Audio Size: {test_data['audio_size_bytes']} bytes")
                
            if 'content_type' in test_data:
                print(f"  Content Type: {test_data['content_type']}")
                
            if 'audio_duration' in test_data:
                print(f"  Test Audio Duration: {test_data['audio_duration']}")
                
            if 'recognition_result' in test_data:
                result = test_data['recognition_result']
                if isinstance(result, dict) and 'DisplayText' in result:
                    print(f"  Recognition Result: {result.get('DisplayText', 'N/A')}")
                elif isinstance(result, dict):
                    print(f"  Recognition Status: {result.get('RecognitionStatus', 'Unknown')}")
                    
            if 'test_count' in test_data:
                print(f"  Sub-tests: {test_data['passed_count']}/{test_data['test_count']} passed")
                
            if 'details' in test_data and isinstance(test_data['details'], list):
                for i, detail in enumerate(test_data['details'][:3]):  # Show first 3 details
                    status = "✅" if detail.get('passed', False) else "❌"
                    test_name = detail.get('test_name', detail.get('test_case', f'Test {i+1}'))
                    print(f"    {status} {test_name}")
                    
                    if detail.get('voice_used'):
                        print(f"        Voice: {detail['voice_used']}")
                    if detail.get('audio_size_bytes'):
                        print(f"        Audio Size: {detail['audio_size_bytes']} bytes")
                    if detail.get('error'):
                        print(f"        Error: {detail['error'][:60]}...")
                
                if len(test_data['details']) > 3:
                    print(f"    ... and {len(test_data['details']) - 3} more tests")
            
            print()
        
        print("Summary:")
        print("-" * 40)
        summary = results['summary']
        print(f"Tests Passed: {summary['passed_tests']}/{summary['total_tests']}")
        print(f"Success Rate: {summary['success_rate']}")
        
        overall_status = "✅ SUCCESS" if summary['overall_success'] else "❌ FAILED"
        print(f"Overall Result: {overall_status}")
        print("="*60)


def print_usage():
        """Print usage instructions."""
        print("\nAzure Speech Service Endpoint Tester")
        print("="*40)
        print("\nRequired Environment Variables:")
        print("  AZURE_SPEECH_KEY     - Your Azure Speech subscription key")
        print("  AZURE_SPEECH_REGION  - Your Azure region (e.g., eastus, westus2)")
        print("\nOptional Environment Variables:")
        print("  AZURE_SPEECH_ENDPOINT - Custom endpoint URL (overrides region)")
        print("\nUsage:")
        print("  export AZURE_SPEECH_KEY='your-key-here'")
        print("  export AZURE_SPEECH_REGION='eastus'")
        print("  python azure_speech_test.py")
        print("\nExample regions: eastus, westus, westus2, eastus2, centralus")
        print("Example endpoint format: https://<region>.api.cognitive.microsoft.com/sts/v1.0/issuetoken")


def main():
        """Main function to run the tests."""
        try:
            # Check if help is requested
            if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
                print_usage()
                return
            
            # Initialize and run tests
            tester = AzureSpeechTester()
            results = tester.run_comprehensive_test()
            
            # Print results
            print_test_results(results)
            
            # Exit with appropriate code
            if results['summary']['overall_success']:
                print("\n🎉 All tests passed! Your Azure Speech endpoint is working correctly.")
                sys.exit(0)
            else:
                print("\n⚠️  Some tests failed. Please check your configuration and network connectivity.")
                sys.exit(1)
                
        except ValueError as e:
            logger.error(f"Configuration error: {str(e)}")
            print_usage()
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            sys.exit(1)


if __name__ == "__main__":
    main()
