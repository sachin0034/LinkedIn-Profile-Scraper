
# LinkedIn Profile Scraper

This Python script automates the process of logging into LinkedIn, searching for "CEO" profiles, and scraping detailed information from those profiles. It uses `Selenium` to navigate the LinkedIn website and `BeautifulSoup` to extract data from the profile pages.

## Prerequisites

1. **Python**: Make sure you have Python 3.7 or higher installed on your system.
2. **Selenium**: Install the Selenium package to control the web browser.
3. **Google Chrome**: Make sure you have Google Chrome installed.
4. **ChromeDriver**: Download the ChromeDriver that matches your installed version of Chrome from [here](https://sites.google.com/chromium.org/driver/).

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd LinkedInProfileScraper
   ```

2. **Install required Python packages**:
   ```bash
   pip install -r requirements.txt
   ```
   Ensure `requirements.txt` contains the following:
   ```text
   selenium
   beautifulsoup4
   ```

3. **Download ChromeDriver**:
   - Download the ChromeDriver for your version of Chrome from [ChromeDriver Downloads](https://sites.google.com/chromium.org/driver/).
   - Extract the downloaded file and place it in a directory included in your system's PATH, or specify its path when initializing the `webdriver`.

## Usage

### Step 1: Set Your LinkedIn Credentials

Replace the placeholders with your actual LinkedIn credentials in the `main.py` file:

```python
username = "your_email@example.com"
password = "your_password"
```

### Step 2: Run the Script

Run the script using the following command:

```bash
python main.py
```

### Step 3: Follow the Process

1. **Login**: The script will navigate to LinkedIn's login page and log in using your credentials.
2. **Search for "CEO" Profiles**: It will enter "CEO" into the search bar and submit the query.
3. **Filter by People**: The script will filter the search results to show only "People".
4. **Visit Profiles**: It will visit each profile in the search results, extract data, and save it to `linkedin_profiles.json`.

### Step 4: View the Scraped Data

After the script has completed, you will find a `linkedin_profiles.json` file containing all the scraped data.

## Important Notes

- **LinkedIn Account**: Make sure your LinkedIn account is in good standing, as LinkedIn may detect and restrict scraping activities.
- **Script Performance**: The script includes randomized delays (`time.sleep()`) to mimic human interaction. Adjust these delays if necessary, but shorter delays increase the risk of getting flagged by LinkedIn.
- **Legal Compliance**: Make sure you comply with LinkedIn's terms of service when using this script.

## Error Handling

The script includes several error-handling mechanisms to ensure smooth execution:
- Handles `TimeoutException`, `NoSuchElementException`, and `StaleElementReferenceException` when interacting with page elements.
- Includes `traceback` for detailed error messages.

## Contributions

Feel free to fork this repository, submit pull requests, and suggest improvements!

## License

This project is licensed under the MIT License.
