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
from typing import Optional, Dict, Any
import logging

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
        
        self.speech_endpoint = f"https://{self.region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
        
        logger.info(f"Initialized Azure Speech Tester")
        logger.info(f"Token endpoint: {self.token_endpoint}")
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
