# TrueContext CSV Template Generator

A streamlined Streamlit application for generating FreeMarker templates (.ftl files) for custom CSV exports from TrueContext (formerly ProntoForms) form definitions.

## 🚀 Quick Start

### Option 1: Deploy to Streamlit Cloud (Recommended)

1. Fork this repository to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Click "New app"
4. Connect your GitHub repository
5. Deploy!

### Option 2: Run Locally

```bash
# Clone the repository
git clone https://github.com/yourusername/truecontext-csv-generator.git
cd truecontext-csv-generator

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

## 📝 How to Use

1. **Upload Form Definition**: Upload a TrueContext form definition JSON file
2. **Select Fields**: Choose which form fields to include in your CSV export
3. **Configure Options**: 
   - Set custom column headers
   - Add filters and conditions
   - Configure date/time formatting
4. **Generate Template**: Create the FreeMarker template
5. **Download**: Save the .ftl file and use it in TrueContext for custom exports

## 🎯 Features

- **Dynamic Field Selection**: Automatically parses form structure and presents all available fields
- **Custom Headers**: Define your own column headers for the CSV output
- **Smart Filtering**: Add conditions to include/exclude data based on field values
- **Date Formatting**: Multiple date/time format options
- **Nested Field Support**: Handles complex form structures with nested sections
- **Preview Mode**: See a preview of your template before downloading
- **Export Options**: Download as .ftl file ready for TrueContext

## 📊 Supported Field Types

- Text fields
- Number fields
- Date/Time fields
- Dropdown selections
- Radio buttons
- Checkboxes
- Multi-select fields
- Nested sections and repeatable sections

## 🔧 Template Features

The generated FreeMarker templates support:
- Conditional logic (`<#if>` statements)
- Data formatting and transformation
- Custom separators and delimiters
- Header row customization
- UTF-8 encoding with BOM for Excel compatibility

## 💡 Tips

- **Excel Compatibility**: Templates are generated with UTF-8 BOM encoding for proper Excel display
- **Field IDs**: TrueContext automatically cleans field IDs (removes spaces, truncates to 19 chars)
- **Testing**: Always test your generated template with sample data in TrueContext
- **Complex Forms**: For forms with repeatable sections, pay attention to the array indexing

## 📁 Project Structure

```
.
├── streamlit_app.py    # Main application
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── .gitignore         # Git ignore rules
```

## 🤝 Support

For issues or feature requests, please create an issue in the GitHub repository.

## 📄 License

This project is designed for TrueContext users to streamline their CSV export workflow.

---

Built with ❤️ using Streamlit for the TrueContext community