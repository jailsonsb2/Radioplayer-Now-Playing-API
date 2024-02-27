# FastAPI Metadata Stream Title Extractor

## Overview

FastAPI Metadata Stream Title Extractor is a simple application that allows users to obtain the title from the metadata of an audio stream and extract the artist and song name from it. It uses the FastAPI library to create a web API that accepts the URL of an MP3 audio stream as input and returns the artist and song name in JSON format.

## Features

- Retrieval of the title from the metadata of an audio stream
- Extraction of the artist and song name from the stream title

## Requirements

Before running the application, make sure you have the following installed:
- Python 3.x
- FastAPI
- Uvicorn

## Setup Instructions

Step 1: Clone the repository
```bash
git clone https://github.com/jailsonsb2/FastAPI_Stream_Title_metadata_Extractor.git
```
Step 2: Navigate to the project directory
```bash
cd FastAPI_Stream_Title_metadata_Extractor
```
Step 3: Install dependencies
```bash
pip install -r requirements.txt
```
Step 4: Run the application
```bash
uvicorn main:app --reload
```
## Usage

To retrieve the title from the metadata of an audio stream, send a GET request to the '/get_stream_title/' endpoint with the 'url' parameter containing the URL of the MP3 audio stream.

## Contribution

Contributions are welcome! Feel free to open an issue or submit a pull request for suggestions, bug fixes, or new features.
