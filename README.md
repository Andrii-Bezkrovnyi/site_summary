# Summary of collected pages

This repository contains a  script is designed to fetch webpages from a specified base URL, generate summaries of the content using the OpenAI API, and create a CSV file containing advertisement data for import into Google Ads

## How Setup and Execution code

### 1. Set Up the Scraping Environment

1. **Clone the repository**:
    ```sh
    git clone https://github.com/Andrii-Bezkrovnyi/site_summary.git
    ```

2. **Create a virtual environment**:
    ```sh
    python -m venv venv
    venv\Scripts\activate (on Windows) 
    source venv/bin/activate  (on Linux)
    ```

3. **Install the required packages**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Configuring environment variables:**

   Create a .env file in the project directory with the following content:

   ```
   OPENAI_API_KEY=YOUR_OPENAI_API_KEY  # Replace with your actual API key of OpenAI

    ```

### 2. Execute the Script

1. **Run the script**:
    ```sh
    python main.py
    ```

   This script will start the scraping and create summary of the site and create a file  `google_ads.csv` with the ads for import into Google Ads.