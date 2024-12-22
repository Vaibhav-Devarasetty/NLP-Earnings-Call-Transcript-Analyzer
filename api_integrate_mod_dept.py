import certifi
import json
import os
from datetime import datetime
from urllib.request import urlopen
import requests
import ast
import pandas as pd
from openai import AssistantEventHandler, OpenAI
import re
import sys

client = OpenAI(api_key="")

def modified_candidate_labels_specific(pl_path):
    pls = pd.read_csv(pl_path)

    modified_labels = []

    for i in range(len(pls)):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. you are just going to provide me with the modified label and no extra text, the modified label should be specific towards the product line which will be mentioned and it should be very short"},
                {"role": "user", "content": f"Modify the following label to create a specific label that is more selective than the original but not overly specific towards the product line. The product line is:\n\n{pls['Product Line'][i]}\n\n the specific label is {pls['Value'][i]}."},
            ],
            max_tokens=50,
            temperature=0,
        )
        specific_label = response.choices[0].message.content
        modified_labels.append(specific_label)
    
    return modified_labels

def modified_candidate_labels(candidate_labels, pl_path):
    pls = pd.read_csv(pl_path)

    pl_list = list(pls[list(pls.keys())[1]])
    phrase = ""

    for i in range(len(pl_list)):
        if i == len(pl_list) - 1:
            phrase += pl_list[i]
        else:
            phrase += pl_list[i] + ", "

    modified_labels = []

    for label in candidate_labels:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. you are just going to provide me with the modified candidate label and no extra text, the modified candidate label should be specific towards the product line which will be mentioned"},
                {"role": "user", "content": f"Modify the following candidate label to create a specific candidate label that is more selective than the original but not overly specific towards the product line. The product line is:\n\n{phrase}\n\n the specific candidate label is {label}."},
            ],
            max_tokens=50,
            temperature=0,
        )
        specific_label = response.choices[0].message.content
        modified_labels.append(specific_label)
    
    return modified_labels


# Function to read text from a file
def read_text_file(file_path):
    """Reads and returns the content of a text file."""
    with open(file_path, 'r') as file:
        text = file.read()
    return text

def get_jsonparsed_data(url):
    """Fetches and parses JSON data from a URL."""
    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")
    return json.loads(data)

def save_transcript_to_file(data):
    """Saves the transcript data to a file with a structured naming convention."""
    ticker = data['symbol']
    quarter = data['quarter']
    date_str = data['date']
    content = data['content']

    date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    file_name = f"{ticker}_Q{quarter}_{date.strftime('%Y%m%d')}.txt"
    directory = f"./json_results/{ticker}"
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, file_name)

    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write(content)
        print(f"File saved to {file_path}")
    else:
        print(f"File already exists: {file_path}")
    
    return file_path

# Define the event handler class
class EventHandler(AssistantEventHandler):
    """Event handler for processing assistant events."""
    def on_text_created(self, text) -> None:
        pass

    def on_tool_call_created(self, tool_call):
        pass

    def on_message_done(self, message) -> None:
        message_content = message.content[0].text
        print(f"{message_content.value}")

# response = client.files.list(purpose="assistants")
# files = list(response.data)
# number_of_files = 2
# selected_files = []
# for i in range(number_of_files):
#     selected_file = files[i]
#     selected_files.append(selected_file)
# for selected_file in selected_files:
#     client.files.delete(selected_file.id)

def pipeline(ticker, candidate_labels, fmp_api_key = "", openai_api_key = ""):
    """Pipeline function to fetch transcripts, save them, and analyze using OpenAI API."""
    current_year = datetime.now().year
    url = f"https://financialmodelingprep.com/api/v4/batch_earning_call_transcript/{ticker}?year={current_year}&apikey={fmp_api_key}"

    directory = f"./json_results/{ticker}"
    os.makedirs(directory, exist_ok=True)
    file_path = ""

    # Check if directory is empty
    if not os.listdir(directory):
        data = get_jsonparsed_data(url)

        if len(data) == 4:
            data_1 = get_jsonparsed_data(f"https://financialmodelingprep.com/api/v4/batch_earning_call_transcript/{ticker}?year={current_year + 1}&apikey={fmp_api_key}")
            if len(data_1) != 0:
                data = data_1

        elif len(data) == 0:
            flag = False
            for i in range(1, 4):
                data_1 = get_jsonparsed_data(f"https://financialmodelingprep.com/api/v4/batch_earning_call_transcript/{ticker}?year={current_year - i}&apikey={fmp_api_key}")
                if len(data_1) != 0:
                    data = data_1
                    flag = True
                    break
            
            if not flag:
                return False

        if data:
            file_path = save_transcript_to_file(data[0])
        
        
    else:
        file_path = os.path.join(directory, os.listdir(directory)[0])
        print(f"Files already exist in the directory: {directory}")

    # Initialize the OpenAI client
    client = OpenAI(api_key=openai_api_key)

    # Instruction for the assistant
    instruction = f"""You are an expert marketing research professional who has a keen eye to identify signals and opportunities from publicly available reports and filings of companies. Your task is to understand the product offering of a specific department that we are looking to sell to {ticker} and go through the entire earnings call of {ticker} meticulously to find out any announcement, mentions, strategy or initiative that could be important to determine the need for such an offering of that department.
The call transcript is attached, and the department is mentioned in the messages.
Please output the mentions, initiative or strategy in the following way:
1) The summary of the mention, initiative or strategy spoken about in the earnings call that indicates relevance to the department.
2) Snippet to the actual mention, initiative or strategy.

Important:
1) The snippets are accurate and directly related to the strategy, mention or initiative.
2) Return all initiatives, strategies and mentions related to the department.
3) If no relevant initiatives, strategies or mentions are found, do not provide any text and explicitly mention that no relevant information was found.

Output Format:
1) Provide the output in a JSON format only.
2) The output format should be in this way for each initiative, strategy or mention:
    "Summary": "The summary of the mention, initiative or strategy spoken about in the earnings call that indicates relevance to the department.",
    "Snippet": "Provide the relevant snippet from the text that discusses the mention, initiative or strategy"
3) "The Output format needs to conserve the number of tokens, so format JSON without extra spaces or indentation."
It will be a list with each element in the list being the above json formatted text with the above mentioned format for each strategy, initiative or mention.
"""

    # Create the assistant
    assistant = client.beta.assistants.create(
        name="Data Analyser",
        instructions=instruction,
        model="gpt-4o",
        tools=[{"type": "file_search"}],
        response_format="auto",
        temperature=0
    )

    # Directory containing the subdirectories for each company
    root_directory = f"./results_transcripts_mod_dept/{ticker}"
    os.makedirs(root_directory, exist_ok=True)

    # Candidate labels to search for
    # candidate_labels = ['Design', 'Marketing', 'Education', 'Legal', 'Customer Service', 'Finance', 'Engineering', 'Human Resources', 'Sales', 'Health', 'Supply Chain/Logistics']

    # Output file path
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    output_file_path = os.path.join(root_directory, f"{file_name}_insights.txt")
    output_json_path = os.path.join(root_directory, f"{file_name}_json_insights.json")

    with open(output_file_path, "w") as f:
        original_stdout = sys.stdout
        sys.stdout = f
        vector_store = client.beta.vector_stores.create(name=f"{ticker}_Earnings_Transcripts")

        file_streams = [open(file_path, "rb")]

        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id, files=file_streams
        )

        assistant = client.beta.assistants.update(
            assistant_id= assistant.id,
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        )

        # Process each department's strategies and initiatives
        for dept_name in candidate_labels:
            print(f"-----------------{dept_name}-----------------")
            thread = client.beta.threads.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"""Search for key initiatives and strategies for {dept_name} department
Output Format: Provide the output in a JSON format only.
"Summary": "The summary of the mention, initiative or strategy spoken about in the earnings call that indicates any need for the product offering",
"Snippet": "Provide the relevant snippet from the text that discusses the strategy, initiative."""
                    }
                ]
            )

            with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=assistant.id,
                event_handler=EventHandler(),
            ) as stream:
                stream.until_done()

        sys.stdout = original_stdout

    response = client.files.list(purpose="assistants")
    files = list(response.data)
    number_of_files = 1
    selected_files = []
    for i in range(number_of_files):
        selected_file = files[i]
        selected_files.append(selected_file)
    for selected_file in selected_files:
        client.files.delete(selected_file.id)

    client.beta.vector_stores.delete(vector_store_id=vector_store.id)
    client.beta.assistants.delete(assistant_id=assistant.id)

    text_1 = read_text_file(output_file_path)
    response = client.chat.completions.create(
            model="gpt-4o",
            response_format={ "type": "json_object" },
            temperature=0,
            messages=[
                {"role": "system", "content": "You are a highly intelligent and accurate assistant. Your task is to convert the following structured text data into a JSON file, where each department is a key in the JSON object. The value for each key should be a list of JSON objects (if there is relevant information for that department) or an empty list (if there is no relevant information). If the text data is incomplete, you should still produce a valid JSON object by modifying the text accordingly. Please conserve the text tokens as much as possible to avoid hitting the token limit and ensure the response does not end prematurely, as this would prevent the response content from being loaded into a JSON object properly. The Output format needs to conserve the number of tokens, so format JSON without extra spaces or  indentation."},
                {"role": "user", "content": f"{text_1}"}
            ]
        )
    try:
        # Convert the generated text to a JSON object
        #print(response.choices[0].message.content)
        json_data = json.loads(response.choices[0].message.content)

        # Save the JSON data to a file
        with open(output_json_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)

    except json.JSONDecodeError as e:
        print("JSON decoding Failed. Response content might be incomplete.")
        print(f"Error: {e}")
    
    return True



if __name__ == "__main__":
    # Load the CSV file
    tickers = ["AAPL", "CSCO", "AMD", "NVDA"]
    
    fmp_api_key = ""
    openai_api_key = ""

    candidate_labels = ['Design', 'Marketing', 'Education', 'Legal', 'Customer Service', 'Finance', 'Engineering', 'Human Resources', 'Sales', 'Health', 'Supply Chain/Logistics']

    pl_path = "./data/zluri_pl.csv"

    candidate_labels = modified_candidate_labels(candidate_labels=candidate_labels, pl_path=pl_path)

    for ticker in tickers:
        print(f"Ticker : {ticker}")
        response = pipeline(ticker=ticker, candidate_labels = candidate_labels, fmp_api_key=fmp_api_key, openai_api_key=openai_api_key)
        if response:
            print(f"The Ticker {ticker} has been successfully analysed by fetching and generating insights.")
        else:
            print(f"The Ticker {ticker} doesn't have any recent earning calls (might be either acquired or bankruptcy)")