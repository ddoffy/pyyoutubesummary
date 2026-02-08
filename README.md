# YouTube Summary

A tool to summarize YouTube videos using Google Gemini, consisting of a Python backend and a Chrome extension.

## 1. Backend Setup

### Prerequisites
- Python 3.9+
- A Google Gemini API Key

### Installation

1.  **Clone the repository** (if you haven't already).
2.  **Set up environment variables**:
    Create a `.env` file in the root directory:
    ```bash
    GEMINI_API_KEY=your_api_key_here
    ```
3.  **Install dependencies**:
    Using `pip` with the new `pyproject.toml`:
    ```bash
    # Create a virtual environment (optional but recommended)
    python3 -m venv .venv
    source .venv/bin/activate
    
    # Install dependencies
    pip install .
    ```

### Running the Server

Use the provided helper script:
```bash
./start_server.sh
```
Or run manually:
```bash
python3 main.py
```
The server will start on `http://localhost:8282`.

## 2. Chrome Extension Setup

### Build

1.  Navigate to the extension directory:
    ```bash
    cd chrome-extension
    ```
2.  Install Node.js dependencies:
    ```bash
    npm install
    ```
3.  Build the extension:
    ```bash
    npm run build
    ```

### Load in Chrome

1.  Open Chrome and go to `chrome://extensions`.
2.  Enable **Developer mode** (top right).
3.  Click **Load unpacked**.
4.  Select the `chrome-extension/dist` directory.

## 3. Usage

1.  Ensure the backend server is running.
2.  Open a YouTube video.
3.  Click the YouTube Summary extension icon.
4.  (Optional) Open "Server Settings" and verify the URL is correct (default: `https://pyytsum.ddoffy.org` or `http://localhost:8282` if running locally).
5.  Click **Summarize Video**.
