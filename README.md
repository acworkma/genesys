# Azure Speech Service Endpoint Tester

This Python script allows you to test Azure Speech Service endpoints, specifically the token issuance endpoint in the format: `https://<region>.api.cognitive.microsoft.com/sts/v1.0/issuetoken`

## Features

- ✅ **Token Acquisition Testing**: Tests the ability to obtain access tokens from Azure Speech Service
- ✅ **Endpoint Connectivity**: Validates basic network connectivity to Azure endpoints
- ✅ **Token Validation**: Performs basic validation of received tokens
- ✅ **Environment Variable Support**: Configurable via environment variables
- ✅ **Comprehensive Logging**: Detailed logging for debugging and monitoring
- ✅ **Multiple Test Cases**: Runs a suite of tests with detailed reporting

## Prerequisites

- Python 3.6 or higher
- Azure Speech Service subscription
- Azure Speech Service subscription key
- Network connectivity to Azure endpoints

## Installation

1. Clone or download the files to your local machine
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install requests
```

## Configuration

### Method 1: Environment Variables (Recommended)

Set the following environment variables:

```bash
export AZURE_SPEECH_KEY="your-azure-speech-subscription-key"
export AZURE_SPEECH_REGION="your-azure-region"  # e.g., eastus, westus2
```

### Method 2: .env File

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and fill in your actual values:
```bash
AZURE_SPEECH_KEY=your-azure-speech-key-here
AZURE_SPEECH_REGION=eastus
```

### Required Configuration

- **AZURE_SPEECH_KEY**: Your Azure Speech Service subscription key
- **AZURE_SPEECH_REGION**: Your Azure region (e.g., eastus, westus2, centralus)

### Optional Configuration

- **AZURE_SPEECH_ENDPOINT**: Custom endpoint URL (overrides region-based URL)

## Usage

### Quick Start with Test Runner

```bash
./run_tests.sh
```

The test runner will:
- Create a virtual environment (if needed)
- Install dependencies
- Load environment variables from `.env` file (if present)
- Run the comprehensive test suite

### Manual Execution

```bash
python azure_speech_test.py
```

### Help

```bash
python azure_speech_test.py --help
```

## Test Cases

The script runs the following test cases:

1. **Endpoint Connectivity Test**
   - Validates that the Azure Speech endpoint is reachable
   - Tests basic network connectivity

2. **Token Acquisition Test**
   - Attempts to obtain an access token from the Azure Speech Service
   - Validates the HTTP response and status codes

3. **Token Validation Test**
   - Performs basic format validation on received tokens
   - Checks token length and structure

## Example Output

```
=============================================================
AZURE SPEECH SERVICE TEST RESULTS
=============================================================
Timestamp: 2025-06-16 10:30:45
Endpoint: https://eastus.api.cognitive.microsoft.com/sts/v1.0/issuetoken
Region: eastus

Test Results:
----------------------------------------
Connectivity: ✅ PASS
  Description: Basic endpoint reachability test

Token Acquisition: ✅ PASS
  Description: Access token request test

Token Validation: ✅ PASS
  Description: Token format validation test
  Token Length: 1248
  Token Preview: eyJ0eXAiOiJKV1QiLCJ...

Summary:
----------------------------------------
Tests Passed: 3/3
Success Rate: 100.0%
Overall Result: ✅ SUCCESS
=============================================================

🎉 All tests passed! Your Azure Speech endpoint is working correctly.
```

## Common Azure Regions

- `eastus` - East US
- `westus` - West US
- `westus2` - West US 2
- `eastus2` - East US 2
- `centralus` - Central US
- `northeurope` - North Europe
- `westeurope` - West Europe
- `southeastasia` - Southeast Asia
- `eastasia` - East Asia

## Troubleshooting

### Authentication Errors
- Verify your `AZURE_SPEECH_KEY` is correct
- Ensure your Azure Speech Service subscription is active
- Check that you're using the correct region

### Network Connectivity Issues
- Verify your internet connection
- Check if corporate firewalls are blocking Azure endpoints
- Try different Azure regions

### Token Issues
- Tokens are typically valid for 10 minutes
- Ensure your system clock is synchronized
- Check Azure service status if issues persist

## Files

- `azure_speech_test.py` - Main test script
- `requirements.txt` - Python dependencies
- `.env.example` - Example environment configuration
- `run_tests.sh` - Automated test runner script
- `README.md` - This documentation

## Exit Codes

- `0` - All tests passed
- `1` - Some tests failed or configuration error

## License

This script is provided as-is for testing Azure Speech Service endpoints. Use responsibly and in accordance with Azure's terms of service.
