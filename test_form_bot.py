"""
Test suite for Event Registration Automation Bot
Uses pytest to validate bot functionality
"""

import pytest
import os
import tempfile
import csv
from unittest.mock import Mock, patch, MagicMock
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from form_bot import EventRegistrationBot


class TestEventRegistrationBot:
    """Test cases for EventRegistrationBot class"""
    
    @pytest.fixture
    def mock_driver(self):
        """Mock WebDriver for testing"""
        driver = Mock()
        driver.page_source = "<html><body>Test page</body></html>"
        return driver
    
    @pytest.fixture
    def mock_wait(self):
        """Mock WebDriverWait for testing"""
        return Mock()
    
    @pytest.fixture
    def sample_test_data(self):
        """Sample test data for testing"""
        return {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '555-0123',
            'event': 'Test Event',
            'url': 'https://httpbin.org/forms/post'
        }
    
    @pytest.fixture
    def temp_csv_file(self, sample_test_data):
        """Create a temporary CSV file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'email', 'phone', 'event', 'url'])
            writer.writeheader()
            writer.writerow(sample_test_data)
            return f.name
    
    @patch('form_bot.webdriver.Chrome')
    @patch('form_bot.WebDriverWait')
    def test_bot_initialization(self, mock_wait, mock_chrome):
        """Test bot initialization"""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        bot = EventRegistrationBot(headless=True)
        
        assert bot.driver is not None
        assert bot.wait is not None
        assert bot.logger is not None
        mock_chrome.assert_called_once()
        
        bot.close()
    
    @patch('form_bot.webdriver.Chrome')
    @patch('form_bot.WebDriverWait')
    def test_navigate_to_form_success(self, mock_wait, mock_chrome):
        """Test successful navigation to form"""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_wait_instance = Mock()
        mock_wait.return_value = mock_wait_instance
        
        bot = EventRegistrationBot(headless=True)
        bot.driver = mock_driver
        bot.wait = mock_wait_instance
        
        # Mock successful form detection
        mock_wait_instance.until.return_value = Mock()
        
        result = bot.navigate_to_form('https://example.com/form')
        
        assert result is True
        mock_driver.get.assert_called_once_with('https://example.com/form')
        mock_wait_instance.until.assert_called_once()
        
        bot.close()
    
    @patch('form_bot.webdriver.Chrome')
    @patch('form_bot.WebDriverWait')
    def test_navigate_to_form_timeout(self, mock_wait, mock_chrome):
        """Test navigation timeout"""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_wait_instance = Mock()
        mock_wait.return_value = mock_wait_instance
        
        bot = EventRegistrationBot(headless=True)
        bot.driver = mock_driver
        bot.wait = mock_wait_instance
        
        # Mock timeout exception
        mock_wait_instance.until.side_effect = TimeoutException()
        
        result = bot.navigate_to_form('https://example.com/form')
        
        assert result is False
        
        bot.close()
    
    @patch('form_bot.webdriver.Chrome')
    @patch('form_bot.WebDriverWait')
    def test_fill_form_success(self, mock_wait, mock_chrome, sample_test_data):
        """Test successful form filling"""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_wait_instance = Mock()
        mock_wait.return_value = mock_wait_instance
        
        bot = EventRegistrationBot(headless=True)
        bot.driver = mock_driver
        bot.wait = mock_wait_instance
        
        # Mock form elements
        name_field = Mock()
        email_field = Mock()
        phone_field = Mock()
        event_dropdown = Mock()
        
        mock_wait_instance.until.return_value = name_field
        mock_driver.find_element.side_effect = [email_field, phone_field, event_dropdown]
        
        # Mock Select dropdown
        with patch('form_bot.Select') as mock_select:
            mock_select_instance = Mock()
            mock_select.return_value = mock_select_instance
            
            result = bot.fill_form(sample_test_data)
            
            assert result is True
            name_field.clear.assert_called_once()
            name_field.send_keys.assert_called_once_with(sample_test_data['name'])
            email_field.clear.assert_called_once()
            email_field.send_keys.assert_called_once_with(sample_test_data['email'])
            phone_field.clear.assert_called_once()
            phone_field.send_keys.assert_called_once_with(sample_test_data['phone'])
        
        bot.close()
    
    @patch('form_bot.webdriver.Chrome')
    @patch('form_bot.WebDriverWait')
    def test_submit_form(self, mock_wait, mock_chrome):
        """Test form submission"""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        bot = EventRegistrationBot(headless=True)
        bot.driver = mock_driver
        
        # Mock submit button
        submit_button = Mock()
        mock_driver.find_element.return_value = submit_button
        
        result = bot.submit_form()
        
        assert result is True
        mock_driver.find_element.assert_called_once_with(By.TYPE, "submit")
        submit_button.click.assert_called_once()
        
        bot.close()
    
    @patch('form_bot.webdriver.Chrome')
    @patch('form_bot.WebDriverWait')
    def test_check_result_success(self, mock_wait, mock_chrome):
        """Test success result detection"""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        bot = EventRegistrationBot(headless=True)
        bot.driver = mock_driver
        
        # Mock page source with success message
        mock_driver.page_source = "<html><body>Thank you for your registration!</body></html>"
        
        success, message = bot.check_result()
        
        assert success is True
        assert message == "Success"
        
        bot.close()
    
    @patch('form_bot.webdriver.Chrome')
    @patch('form_bot.WebDriverWait')
    def test_check_result_error(self, mock_wait, mock_chrome):
        """Test error result detection"""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        bot = EventRegistrationBot(headless=True)
        bot.driver = mock_driver
        
        # Mock page source with error message
        mock_driver.page_source = "<html><body>Error: Invalid email format</body></html>"
        
        success, message = bot.check_result()
        
        assert success is False
        assert message == "Error detected"
        
        bot.close()
    
    @patch('form_bot.webdriver.Chrome')
    @patch('form_bot.WebDriverWait')
    def test_take_screenshot(self, mock_wait, mock_chrome):
        """Test screenshot functionality"""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        bot = EventRegistrationBot(headless=True)
        bot.driver = mock_driver
        
        # Mock successful screenshot
        mock_driver.save_screenshot.return_value = True
        
        result = bot.take_screenshot('test_screenshot.png')
        
        assert result is not None
        assert 'test_screenshot.png' in result
        mock_driver.save_screenshot.assert_called_once()
        
        bot.close()
    
    @patch('form_bot.webdriver.Chrome')
    @patch('form_bot.WebDriverWait')
    def test_process_test_case(self, mock_wait, mock_chrome, sample_test_data):
        """Test complete test case processing"""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_wait_instance = Mock()
        mock_wait.return_value = mock_wait_instance
        
        bot = EventRegistrationBot(headless=True)
        bot.driver = mock_driver
        bot.wait = mock_wait_instance
        
        # Mock all the methods
        bot.navigate_to_form = Mock(return_value=True)
        bot.fill_form = Mock(return_value=True)
        bot.submit_form = Mock(return_value=True)
        bot.check_result = Mock(return_value=(True, "Success"))
        bot.take_screenshot = Mock(return_value="screenshot.png")
        
        success, message = bot.process_test_case(sample_test_data, 1)
        
        assert success is True
        assert message == "Success"
        
        bot.navigate_to_form.assert_called_once_with(sample_test_data['url'])
        bot.fill_form.assert_called_once_with(sample_test_data)
        bot.submit_form.assert_called_once()
        bot.check_result.assert_called_once()
        bot.take_screenshot.assert_called_once()
        
        bot.close()
    
    @patch('form_bot.webdriver.Chrome')
    @patch('form_bot.WebDriverWait')
    def test_run_from_csv(self, mock_wait, mock_chrome, temp_csv_file, sample_test_data):
        """Test CSV processing"""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        bot = EventRegistrationBot(headless=True)
        bot.driver = mock_driver
        
        # Mock process_test_case method
        bot.process_test_case = Mock(return_value=(True, "Success"))
        bot.save_results_log = Mock()
        
        results = bot.run_from_csv(temp_csv_file)
        
        assert len(results) == 1
        assert results[0]['name'] == sample_test_data['name']
        assert results[0]['email'] == sample_test_data['email']
        assert results[0]['success'] is True
        
        bot.process_test_case.assert_called_once()
        bot.save_results_log.assert_called_once()
        
        # Clean up
        os.unlink(temp_csv_file)
        bot.close()
    
    def test_directory_creation(self):
        """Test that necessary directories are created"""
        with patch('form_bot.webdriver.Chrome'):
            with patch('form_bot.WebDriverWait'):
                with patch('os.makedirs') as mock_makedirs:
                    with patch('os.path.exists', return_value=False):
                        bot = EventRegistrationBot(headless=True)
                        
                        # Should create screenshots and logs directories
                        expected_calls = [
                            (('screenshots',), {}),
                            (('logs',), {})
                        ]
                        
                        assert mock_makedirs.call_count >= 2
                        bot.close()
    
    @patch('form_bot.webdriver.Chrome')
    @patch('form_bot.WebDriverWait')
    def test_csv_file_not_found(self, mock_wait, mock_chrome):
        """Test handling of missing CSV file"""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        bot = EventRegistrationBot(headless=True)
        bot.driver = mock_driver
        
        results = bot.run_from_csv('nonexistent_file.csv')
        
        assert results == []
        
        bot.close()


class TestIntegration:
    """Integration tests for the bot"""
    
    @pytest.mark.integration
    def test_real_form_interaction(self):
        """Test interaction with real form (requires internet connection)"""
        # This test can be run manually with a real form
        # For automated testing, we'll skip it unless specifically requested
        pytest.skip("Integration test - requires manual verification")
    
    def test_csv_format_validation(self):
        """Test CSV format validation"""
        # Test with valid CSV
        valid_csv_content = "name,email,phone,event,url\nJohn,john@test.com,555-0123,Event1,http://test.com"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(valid_csv_content)
            temp_file = f.name
        
        # Read the file and validate structure
        with open(temp_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            assert len(rows) == 1
            assert 'name' in rows[0]
            assert 'email' in rows[0]
            assert 'phone' in rows[0]
            assert 'event' in rows[0]
            assert 'url' in rows[0]
        
        # Clean up
        os.unlink(temp_file)


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])