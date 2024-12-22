# Earnings Call Transcript Analyzer for Strategic Insights

## Overview
This project is a Python-driven tool designed to analyze earnings call transcripts of publicly traded companies. It extracts strategies, initiatives, and mentions relevant to specific departments, aiding businesses in aligning their offerings with company needs. The project integrates Financial Modeling Prep (FMP) API for fetching data and OpenAI’s GPT models for analyzing and summarizing insights into structured JSON outputs.

## Features
- Fetches earnings call transcripts from publicly available APIs.
- Dynamically identifies and extracts department-specific mentions and strategies.
- Produces structured JSON outputs for actionable insights.
- Ensures accuracy and relevance by leveraging GPT models and custom instructions.
- Supports modular scalability for adding additional functionalities.

## Table of Contents
1. [Requirements](#requirements)
2. [Setup](#setup)
3. [Usage Guide](#usage-guide)
4. [Project Structure](#project-structure)
5. [Core Functionalities](#core-functionalities)
6. [Output Examples](#output-examples)
7. [License](#license)

## Requirements
The project dependencies are listed in `requirements_transcripts.txt`. Install them using:

```bash
pip install -r requirements_transcripts.txt
```

### Major Dependencies:
- Python 3.8+
- annotated-types==0.7.0
- httpx==0.27.0
- openai==1.35.3
- pandas==2.1.1
- requests==2.32.3

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/repository-name.git
   cd repository-name
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements_transcripts.txt
   ```

3. Obtain API keys for:
   - Financial Modeling Prep API ([Get API Key](https://financialmodelingprep.com/))
   - OpenAI API ([Get API Key](https://platform.openai.com/signup/))

4. Add the API keys to the relevant function calls or set them as environment variables.

## Usage Guide

1. Prepare your input:
   - Ensure you have a CSV file with product line data at `./data/zluri_pl.csv`.
   - Modify `tickers` in the script to analyze specific companies.

2. Run the script:
   ```bash
   python main_script.py
   ```

3. Outputs will be stored in:
   - `./results_transcripts_mod_dept/{ticker}` as structured JSON and text files.

## Project Structure

```
.
├── data/
│   └── zluri_pl.csv               # Input file with product lines
├── json_results/                  # Directory for raw transcript data
├── results_transcripts_mod_dept/  # Directory for processed insights
├── main_script.py                 # Main pipeline script
├── requirements_transcripts.txt   # Project dependencies
├── README.md                      # Project documentation
```

## Core Functionalities

### 1. Fetch Earnings Call Transcripts
- Uses the Financial Modeling Prep API to fetch transcript data for specified companies and years.

### 2. Generate Department-Specific Insights
- Leverages GPT models to identify and summarize department-specific mentions, strategies, and initiatives from the transcripts.

### 3. Export Results
- Outputs structured insights in JSON and text formats for each analyzed company.

## Output Examples

### Example JSON Output:

```json
[
  {
    "Summary": "Company plans to invest in AI-driven design tools for product innovation.",
    "Snippet": "We are increasing investments in AI to revolutionize our design process and deliver better products."
  },
  {
    "Summary": "Marketing strategy focuses on digital campaigns targeting younger demographics.",
    "Snippet": "Our marketing team is launching a new series of campaigns aimed at Gen Z audiences."
  }
]
```

### Example Directory Structure After Execution:

```
./results_transcripts_mod_dept/AAPL/
├── AAPL_Q3_20231215_insights.txt
├── AAPL_Q3_20231215_json_insights.json
```

## License
This project is licensed under the MIT License. See `LICENSE` file for details.