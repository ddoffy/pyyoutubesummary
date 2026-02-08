# YouTube Summary Chrome Extension

A Chrome extension that summarizes YouTube videos using AI, with automatic cookie capture for authenticated access.

## Features

- **Automatic Cookie Capture**: Automatically retrieves your YouTube cookies for accessing age-restricted or members-only content
- **One-Click Summarization**: Click the extension popup on any YouTube video to get an AI-generated summary
- **Multiple Output Formats**: Choose between JSON, Markdown, or plain text
- **Configurable API Server**: Point to your local or remote summary server

## Installation

### From Source (Developer Mode)

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top right)
3. Click **Load unpacked**
4. Select the `chrome-extension` folder from this repository

### Add Icons (Optional)

The extension needs icons in the `icons/` folder:
- `icon16.png` (16x16 pixels)
- `icon48.png` (48x48 pixels)
- `icon128.png` (128x128 pixels)

You can create simple icons or use any YouTube/summary-related icon set.

## Usage

1. **Start the API server**:
   ```bash
   cd youtube-summary
   cargo run
   ```
   The server runs on `http://localhost:8181` by default.

2. **Navigate to a YouTube video** in Chrome

3. **Click the extension icon** in your browser toolbar

4. **Click "Summarize Video"** to generate a summary

The extension will:
- Automatically detect the video ID from the URL
- Capture your YouTube cookies for authentication
- Send the request to your configured API server
- Display the summary in the popup

## Configuration

### API Server URL

By default, the extension connects to `https://ytsum.ddoffy.org`. You can change this in the popup settings to point to a different server (e.g., `http://localhost:8181` for local development).

### Output Format

Choose from:
- **JSON**: Structured data with video ID, title, summary, and any errors
- **Markdown**: Formatted text suitable for documentation
- **Plain Text**: Simple text output

## Permissions

The extension requires these permissions:

| Permission | Purpose |
|------------|---------|
| `activeTab` | Access current tab URL to detect YouTube videos |
| `cookies` | Read YouTube cookies for authenticated video access |
| `storage` | Save your settings (API URL, format preference) |
| Host permissions for YouTube | Access YouTube page data |
| Host permissions for localhost | Connect to your local API server |

## How Cookies Work

When you're logged into YouTube, your browser stores authentication cookies. This extension:

1. Reads your YouTube cookies using Chrome's `cookies` API
2. Converts them to Netscape cookie format (compatible with yt-dlp)
3. Sends them with the API request
4. The server uses these cookies to download transcripts that may require authentication

This allows summarizing:
- Age-restricted videos
- Members-only content (if you're a member)
- Premium content
- Private videos you have access to

## Troubleshooting

### "No cookies found"
- Make sure you're logged into YouTube
- Try refreshing the YouTube page
- Check that the extension has cookie permissions

### "Failed to connect to server"
- Ensure the API server is running (`cargo run`)
- Check the API URL in settings
- Verify your firewall isn't blocking localhost connections

### "No subtitles available"
- The video may not have English subtitles
- Try a video that has captions enabled

## Development

### Project Structure

```
chrome-extension/
├── manifest.json      # Extension configuration
├── popup.html         # Extension popup UI
├── popup.css          # Popup styles
├── popup.js           # Popup logic
├── background.js      # Service worker
├── content.js         # YouTube page content script
├── icons/             # Extension icons
└── README.md          # This file
```

### Building

The extension doesn't require a build step. Just load the folder as an unpacked extension in Chrome.

### Testing

1. Make changes to the source files
2. Go to `chrome://extensions/`
3. Click the refresh icon on the YouTube Summary extension
4. Test your changes

## API Endpoint

The extension uses the POST endpoint for better security:

```
POST /api/summary
Content-Type: application/json

{
  "id": "VIDEO_ID",
  "cookies": "# Netscape cookie file...",
  "format": "json"  // or "md", "text", "html"
}
```

Response (JSON format):
```json
{
  "results": [
    {
      "video_id": "xxx",
      "title": "Video Title",
      "summary": "Summary text...",
      "error": null
    }
  ]
}
```

## Security Notes

- Cookies are sent via POST body (not URL parameters)
- Always use HTTPS in production
- The extension only activates on YouTube domains
- No data is sent to third parties
