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

## Advanced Usage

### Custom Bot Configuration

```python
from form_bot import EventRegistrationBot

# Initialize with custom settings
bot = EventRegistrationBot(
    driver_path="/path/to/chromedriver",  # Optional: custom driver path
    headless=True  # Run in background
)

# Process single test case
test_data = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'phone': '555-0123',
    'event': 'Workshop A',
    'url': 'https://example.com/register'
}

success, message = bot.process_test_case(test_data, 1)
bot.close()
```

### Extending the Bot

To add new form fields or functionality:

1. **Add new CSV columns** in your test data
2. **Update `fill_form()` method** to handle new fields
3. **Modify `check_result()` method** if needed for custom success detection

## Troubleshooting

### Common Issues

1. **ChromeDriver Version Mismatch**
   - Solution: Update Chrome browser or download matching ChromeDriver

2. **Form Fields Not Found**
   - Solution: Inspect the target form and update field selectors

3. **Timeout Errors**
   - Solution: Increase wait time or check internet connection

4. **Permission Denied**
   - Solution: Run with appropriate permissions or adjust file paths

### Debug Mode

Enable detailed logging by setting log level:
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Ensure all dependencies are properly installed
4. Verify ChromeDriver compatibility

## Changelog

### v1.0.0
- Initial release
- Basic form automation
- CSV test data support
- Screenshot capture
- Comprehensive logging
- Pytest integration