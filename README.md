# Event Registration Automation Bot

A Selenium WebDriver-based automation bot that fills out event registration forms using test data from CSV files and logs the results.

## Features

- **Automated Form Filling**: Automatically fills Name, Email, Phone, and Event Selection fields
- **Multiple Test Cases**: Runs multiple test scenarios from CSV data
- **Screenshot Capture**: Takes screenshots of form submission results
- **Comprehensive Logging**: Logs all activities and results with timestamps
- **Error Handling**: Robust error handling and reporting
- **Modular Design**: Clean, maintainable code structure
- **Testing Support**: Includes pytest tests for validation

## Project Structure

```
├── form_bot.py           # Main automation script
├── test_form_bot.py      # Pytest test suite
├── test_data.csv         # Sample test cases
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── screenshots/         # Generated screenshots (auto-created)
└── logs/               # Log files (auto-created)
```

## Prerequisites

- Python 3.7 or higher
- Google Chrome browser
- ChromeDriver (can be auto-managed)

## Installation

1. **Clone or download this project**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **ChromeDriver Setup (Optional):**
   - The bot can automatically manage ChromeDriver using `webdriver-manager`
   - Alternatively, download ChromeDriver manually from https://chromedriver.chromium.org/
   - Ensure ChromeDriver version matches your Chrome browser version

## Usage

### Running the Bot

1. **Basic Usage:**
   ```bash
   python form_bot.py
   ```

2. **With Custom CSV File:**
   ```python
   from form_bot import EventRegistrationBot
   
   bot = EventRegistrationBot(headless=False)
   results = bot.run_from_csv('your_test_data.csv')
   bot.close()
   ```

3. **Headless Mode:**
   ```python
   bot = EventRegistrationBot(headless=True)
   ```

### CSV Format

Your test data CSV should have the following columns:
```csv
name,email,phone,event,url
John Doe,john.doe@example.com,555-0123,Workshop A,https://example.com/form
```

### Running Tests

```bash
# Run all tests
pytest test_form_bot.py -v

# Run tests with HTML report
pytest test_form_bot.py --html=logs/test_report.html
```

## Configuration

### Test Form URLs

The default test uses `https://httpbin.org/forms/post` which is a testing service. For real-world usage:

1. Update the URLs in your CSV file
2. Modify the form field selectors in `fill_form()` method if needed
3. Adjust the success/error detection logic in `check_result()` method

### Customizing Form Fields

If your target form has different field names, update the selectors in the `fill_form()` method:

```python
# Current selectors
name_field = self.wait.until(EC.presence_of_element_located((By.NAME, "name")))
email_field = self.driver.find_element(By.NAME, "email")
phone_field = self.driver.find_element(By.NAME, "phone")

# Update to match your form
name_field = self.wait.until(EC.presence_of_element_located((By.ID, "full_name")))
```

## Output Files

### Screenshots
- Location: `screenshots/`
- Format: `test_case_{number}_{timestamp}.png`
- Contains form submission results

### Logs
- **Main Log**: `logs/bot.log` - Detailed execution log
- **Results Log**: `logs/test_results_{timestamp}.txt` - Summary of all test cases
- **Test Report**: `logs/test_report.html` - HTML test report (when using pytest)
