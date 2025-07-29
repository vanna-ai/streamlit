# Vanna Streamlit Response Viewer

A comprehensive Streamlit application for exploring all response types from the Vanna AI API in a single, unified interface.

## Demo

See the app in action:

[![Vanna Streamlit Demo](https://img.youtube.com/vi/VznG45f-aYM/0.jpg)](https://www.youtube.com/watch?v=VznG45f-aYM)

*Click the thumbnail above to watch a demo of the Vanna Streamlit Response Viewer*

## Features

- **Multi-Response Type Support**: Handles all Vanna response types including:
  - Text responses
  - Plotly charts with automatic bdata decoding
  - DataFrames
  - Images
  - Links
  - Interactive buttons
  - SQL queries
  - Error messages

- **Advanced Plotly Support**: 
  - Automatic decoding of binary-encoded data (bdata)
  - Template compatibility fixes
  - Comprehensive error handling
  - Raw JSON inspection for debugging

- **Clean Interface**: 
  - Organized response breakdown
  - Expandable JSON viewers
  - Professional styling with Vanna branding

## Installation

1. Clone this repository:
```bash
git clone https://github.com/vanna-ai/streamlit.git
cd streamlit
```

2. Install the required dependencies:
```bash
pip install streamlit requests pandas plotly numpy
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser and navigate to the local Streamlit URL (typically `http://localhost:8501`)

3. In the sidebar, enter your credentials:
   - **Vanna API Key**: Your Vanna API key (starts with `vn-`)
   - **User Email**: Your registered email address
   - **Agent ID**: Your specific agent identifier

4. Enter your query in the main text area and click "Run Query"

5. Explore the different response types returned by your Vanna agent

## Configuration

### Getting Your Credentials

- **API Key**: Obtain from your Vanna AI dashboard
- **Agent ID**: Found in your Vanna AI agent configuration
- **User Email**: The email associated with your Vanna AI account

### Environment Variables (Optional)

You can set default values using environment variables:

```bash
export VANNA_API_KEY="your-api-key"
export VANNA_USER_EMAIL="your-email@domain.com"
export VANNA_AGENT_ID="your-agent-id"
```

Then modify the sidebar inputs to use these defaults:

```python
api_key = st.text_input("Vanna API Key", type="password", 
                       value=os.getenv("VANNA_API_KEY", ""))
user_email = st.text_input("User Email", 
                          value=os.getenv("VANNA_USER_EMAIL", ""))
agent_id = st.text_input("Agent ID", 
                        value=os.getenv("VANNA_AGENT_ID", ""))
```

## Response Types

This viewer supports all Vanna response types:

| Type | Description | Features |
|------|-------------|----------|
| `text` | Plain text responses | Formatted display |
| `plotly` | Interactive charts | Auto bdata decoding, JSON inspection |
| `dataframe` | Tabular data | Full-width responsive tables |
| `image` | Images and visualizations | Auto-sizing with captions |
| `link` | External links | Clickable with descriptions |
| `buttons` | Interactive elements | Clickable button arrays |
| `sql` | SQL queries | Syntax-highlighted code blocks |
| `error` | Error messages | Formatted error display |

## Technical Details

### Plotly bdata Handling

The application automatically handles Vanna's binary-encoded data format:

- Decodes base64 `bdata` fields with specified `dtype`
- Supports common data types: `i2`, `i4`, `f8`
- Processes nested objects and arrays
- Handles all trace properties that may contain encoded data

### Template Compatibility

Fixes common Plotly template issues:
- Converts `scattermap` to `scattermapbox`
- Removes unsupported trace types
- Ensures compatibility with current Plotly versions

## Troubleshooting

### Common Issues

**Plotly Rendering Errors**:
- The app includes comprehensive error handling for Plotly charts
- Raw JSON is displayed when rendering fails
- Check the expandable "View Plotly JSON" section for debugging

**API Connection Issues**:
- Verify your API key is correct and active
- Ensure your email matches your Vanna account
- Check that the agent ID exists and is accessible

**Empty Responses**:
- Some queries may return only `end` type responses
- Try different query formulations
- Check your agent's configuration and data sources

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with a clear description

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues related to:
- **This Streamlit app**: Open an issue in this repository
- **Vanna AI platform**: Contact Vanna AI support
- **API questions**: Refer to the Vanna AI documentation

## Changelog

### v1.0.0
- Initial release
- Support for all major Vanna response types
- Advanced Plotly chart rendering with bdata decoding
- Clean, professional interface
- Comprehensive error handling