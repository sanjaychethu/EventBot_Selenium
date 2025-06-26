"""
Event Registration Automation Bot
A Selenium WebDriver bot that automates form filling for event registration
"""

import csv
import os
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False
    print("webdriver-manager not available. Please ensure ChromeDriver is in PATH or provide driver_path.")


class EventRegistrationBot:
    def __init__(self, driver_path=None, headless=False):
        """
        Initialize the bot with Chrome WebDriver
        
        Args:
            driver_path (str): Path to ChromeDriver executable
            headless (bool): Run browser in headless mode
        """
        self.driver = None
        self.wait = None
        self.setup_logging()
        self.setup_directories()
        self.setup_driver(driver_path, headless)
    
    def setup_logging(self):
        """Setup logging configuration"""
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_directories(self):
        """Create necessary directories"""
        directories = ['screenshots', 'logs']
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                self.logger.info(f"Created directory: {directory}")
    
    def setup_driver(self, driver_path, headless):
        """Setup Chrome WebDriver with options"""
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            if driver_path:
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            elif WEBDRIVER_MANAGER_AVAILABLE:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # Assumes chromedriver is in PATH
                self.driver = webdriver.Chrome(options=chrome_options)
            
            # Execute script to remove automation indicators
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 10)
            self.logger.info("WebDriver initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise
    
    def navigate_to_form(self, url):
        """Navigate to the registration form"""
        try:
            self.driver.get(url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
            self.logger.info(f"Successfully navigated to: {url}")
            return True
        except TimeoutException:
            self.logger.error(f"Timeout waiting for form to load at: {url}")
            return False
        except Exception as e:
            self.logger.error(f"Error navigating to form: {str(e)}")
            return False
    
    def fill_form(self, test_data):
        """
        Fill the registration form with provided data
        
        Args:
            test_data (dict): Dictionary containing form data
        """
        try:
            # Fill Name field
            name_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "name"))
            )
            name_field.clear()
            name_field.send_keys(test_data['name'])
            self.logger.info(f"Filled name: {test_data['name']}")
            
            # Fill Email field
            email_field = self.driver.find_element(By.NAME, "email")
            email_field.clear()
            email_field.send_keys(test_data['email'])
            self.logger.info(f"Filled email: {test_data['email']}")
            
            # Fill Phone field (try multiple possible field names)
            phone_field = None
            phone_selectors = ["phone", "phone_number", "telephone", "mobile"]
            for selector in phone_selectors:
                try:
                    phone_field = self.driver.find_element(By.NAME, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if phone_field:
                phone_field.clear()
                phone_field.send_keys(test_data['phone'])
                self.logger.info(f"Filled phone: {test_data['phone']}")
            else:
                self.logger.warning("Phone field not found")
            
            # Select Event (try dropdown first, then radio buttons)
            try:
                event_dropdown = Select(self.driver.find_element(By.NAME, "event"))
                event_dropdown.select_by_visible_text(test_data['event'])
                self.logger.info(f"Selected event from dropdown: {test_data['event']}")
            except NoSuchElementException:
                try:
                    # Try radio buttons or checkboxes
                    event_option = self.driver.find_element(
                        By.XPATH, f"//input[@value='{test_data['event']}' or @id='{test_data['event']}']"
                    )
                    event_option.click()
                    self.logger.info(f"Selected event option: {test_data['event']}")
                except NoSuchElementException:
                    self.logger.warning(f"Event field not found for: {test_data['event']}")
            
            # Small delay to ensure form is filled
            time.sleep(0.5)
            return True
            
        except Exception as e:
            self.logger.error(f"Error filling form: {str(e)}")
            return False
    
    def submit_form(self):
        """Submit the form and wait for response"""
        try:
            # Try different submit button selectors
            submit_selectors = [
                (By.TYPE, "submit"),
                (By.XPATH, "//button[contains(text(), 'Submit')]"),
                (By.XPATH, "//input[@value='Submit']"),
                (By.XPATH, "//button[contains(@class, 'submit')]")
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(*selector)
                    break
                except NoSuchElementException:
                    continue
            
            if submit_button:
                submit_button.click()
                self.logger.info("Form submitted")
                
                # Wait for response (success or error message)
                time.sleep(2)
                return True
            else:
                self.logger.error("Submit button not found")
                return False
            
        except Exception as e:
            self.logger.error(f"Error submitting form: {str(e)}")
            return False
    
    def take_screenshot(self, filename):
        """Take a screenshot of the current page"""
        try:
            screenshot_path = os.path.join('screenshots', filename)
            self.driver.save_screenshot(screenshot_path)
            self.logger.info(f"Screenshot saved: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {str(e)}")
            return None
    
    def check_result(self):
        """Check if form submission was successful"""
        try:
            # Look for success message
            success_indicators = [
                "success", "thank you", "registered", "confirmation",
                "submitted", "complete", "received", "congratulations"
            ]
            
            page_text = self.driver.page_source.lower()
            for indicator in success_indicators:
                if indicator in page_text:
                    self.logger.info("Form submission appears successful")
                    return True, "Success"
            
            # Look for error message
            error_indicators = [
                "error", "invalid", "required", "missing", "failed",
                "incorrect", "please", "must", "cannot"
            ]
            
            for indicator in error_indicators:
                if indicator in page_text:
                    self.logger.warning("Form submission appears to have errors")
                    return False, "Error detected"
            
            # Check for redirect to success page
            current_url = self.driver.current_url.lower()
            if any(word in current_url for word in ["success", "thank", "confirm"]):
                self.logger.info("Redirected to success page")
                return True, "Success"
            
            self.logger.info("Form submission result unclear")
            return None, "Unknown"
            
        except Exception as e:
            self.logger.error(f"Error checking result: {str(e)}")
            return False, "Error checking result"
    
    def process_test_case(self, test_data, test_case_num):
        """Process a single test case"""
        self.logger.info(f"Processing test case #{test_case_num}")
        
        try:
            # Navigate to form
            if not self.navigate_to_form(test_data['url']):
                return False, "Navigation failed"
            
            # Fill form
            if not self.fill_form(test_data):
                return False, "Form filling failed"
            
            # Submit form
            if not self.submit_form():
                return False, "Form submission failed"
            
            # Check result
            success, message = self.check_result()
            
            # Take screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_name = f"test_case_{test_case_num}_{timestamp}.png"
            self.take_screenshot(screenshot_name)
            
            return success, message
            
        except Exception as e:
            self.logger.error(f"Error in test case #{test_case_num}: {str(e)}")
            return False, f"Exception: {str(e)}"
    
    def run_from_csv(self, csv_file):
        """Run automation using test data from CSV file"""
        try:
            with open(csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                test_cases = list(reader)
            
            self.logger.info(f"Loaded {len(test_cases)} test cases from {csv_file}")
            
            results = []
            for i, test_data in enumerate(test_cases, 1):
                try:
                    success, message = self.process_test_case(test_data, i)
                    result = {
                        'test_case': i,
                        'name': test_data.get('name', 'Unknown'),
                        'email': test_data.get('email', 'Unknown'),
                        'phone': test_data.get('phone', 'Unknown'),
                        'event': test_data.get('event', 'Unknown'),
                        'url': test_data.get('url', 'Unknown'),
                        'success': success,
                        'message': message,
                        'timestamp': datetime.now().isoformat()
                    }
                    results.append(result)
                    
                    # Log result
                    status = "SUCCESS" if success else "FAILURE"
                    self.logger.info(f"Test case #{i} - {status}: {message}")
                    
                    # Wait between test cases to avoid overwhelming the server
                    if i < len(test_cases):  # Don't wait after the last test case
                        time.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"Error in test case #{i}: {str(e)}")
                    results.append({
                        'test_case': i,
                        'name': test_data.get('name', 'Unknown'),
                        'email': test_data.get('email', 'Unknown'),
                        'phone': test_data.get('phone', 'Unknown'),
                        'event': test_data.get('event', 'Unknown'),
                        'url': test_data.get('url', 'Unknown'),
                        'success': False,
                        'message': f"Exception: {str(e)}",
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Save results to log file
            self.save_results_log(results)
            return results
            
        except FileNotFoundError:
            self.logger.error(f"CSV file not found: {csv_file}")
            return []
        except Exception as e:
            self.logger.error(f"Error processing CSV file: {str(e)}")
            return []
    
    def save_results_log(self, results):
        """Save test results to a log file"""
        try:
            log_file = f"logs/test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(log_file, 'w') as f:
                f.write("Event Registration Bot - Test Results\n")
                f.write("=" * 50 + "\n\n")
                
                for result in results:
                    f.write(f"Test Case #{result['test_case']}\n")
                    f.write(f"Name: {result['name']}\n")
                    f.write(f"Email: {result['email']}\n")
                    f.write(f"Phone: {result['phone']}\n")
                    f.write(f"Event: {result['event']}\n")
                    f.write(f"URL: {result['url']}\n")
                    f.write(f"Status: {'SUCCESS' if result['success'] else 'FAILURE'}\n")
                    f.write(f"Message: {result['message']}\n")
                    f.write(f"Timestamp: {result['timestamp']}\n")
                    f.write("-" * 30 + "\n")
                
                # Summary
                total_tests = len(results)
                successful_tests = sum(1 for r in results if r['success'])
                f.write(f"\nSUMMARY:\n")
                f.write(f"Total Tests: {total_tests}\n")
                f.write(f"Successful: {successful_tests}\n")
                f.write(f"Failed: {total_tests - successful_tests}\n")
                if total_tests > 0:
                    f.write(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%\n")
            
            self.logger.info(f"Results saved to: {log_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving results log: {str(e)}")
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.logger.info("WebDriver closed")

def main():
    """Main function to run the bot"""
    print("Event Registration Automation Bot")
    print("=" * 40)
    
    # Configuration
    CSV_FILE = 'test_data.csv'
    HEADLESS_MODE = False  # Set to True for headless operation
     # <-- SET YOUR PATH HERE
    
    # Initialize bot
    bot = EventRegistrationBot(headless=HEADLESS_MODE)  # Don't pass driver_path
  # Don't pass driver_path

    
    try:
        print(f"Loading test data from: {CSV_FILE}")
        results = bot.run_from_csv(CSV_FILE)
        
        # Print summary
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r['success'])
        
        print(f"\n{'='*50}")
        print(f"AUTOMATION COMPLETE")
        print(f"{'='*50}")
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        if total_tests > 0:
            print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        print(f"\nResults saved to logs directory")
        print(f"Screenshots saved to screenshots directory")
        
    except KeyboardInterrupt:
        print("\nAutomation stopped by user")
    except Exception as e:
        print(f"Error running automation: {str(e)}")
    finally:
        bot.close()
if __name__ == "__main__":
    main()
