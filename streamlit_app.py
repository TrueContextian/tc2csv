#!/usr/bin/env python3
"""
TrueContext CSV Generator - Streamlit Version
Converts React application to Streamlit for generating FreeMarker templates from TrueContext Form Definitions
"""

import streamlit as st
import json
import pandas as pd
from typing import List, Dict, Set, Optional
import base64
from io import StringIO
import hashlib

# Page configuration
st.set_page_config(
    page_title="TrueContext CSV Generator", 
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for TrueContext Dark Theme
st.markdown("""
<style>
    /* TrueContext Dark Theme Colors */
    :root {
        --tc-primary: #00A4E4;
        --tc-primary-light: #33B5E5;
        --tc-secondary: #0077BE;
        --tc-bg-dark: #0E1117;
        --tc-bg-secondary: #1C1E26;
        --tc-bg-card: #262730;
        --tc-text-primary: #FAFAFA;
        --tc-text-secondary: #B8BCC8;
        --tc-border: #383A42;
        --tc-success: #00D25B;
        --tc-warning: #FFAB00;
        --tc-danger: #FC424A;
    }
    
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #00A4E4 0%, #0077BE 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 164, 228, 0.25);
        border: 1px solid rgba(0, 164, 228, 0.3);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 600;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.95;
        font-size: 1.1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #00A4E4 0%, #0077BE 100%);
        color: white !important;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 164, 228, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 164, 228, 0.4);
        background: linear-gradient(135deg, #33B5E5 0%, #00A4E4 100%);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #262730;
        color: #B8BCC8;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: 500;
        border: 1px solid #383A42;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00A4E4 0%, #0077BE 100%);
        color: white !important;
        border: 1px solid #00A4E4;
        box-shadow: 0 4px 12px rgba(0, 164, 228, 0.3);
    }
    
    /* Info boxes */
    .info-card {
        background: linear-gradient(135deg, #1C1E26 0%, #262730 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #00A4E4;
        margin-bottom: 1rem;
        color: #FAFAFA;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border: 1px solid #383A42;
    }
    
    .info-card strong {
        color: #00A4E4;
    }
    
    /* Success/Error boxes for progress */
    .progress-success {
        background: linear-gradient(135deg, #00D25B 0%, #00A745 100%);
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0, 210, 91, 0.3);
    }
    
    .progress-pending {
        background: #262730;
        border: 1px solid #383A42;
        border-radius: 10px;
        padding: 1rem;
    }
    
    .progress-info {
        background: linear-gradient(135deg, #00A4E4 0%, #0077BE 100%);
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0, 164, 228, 0.3);
    }
    
    /* Metrics styling */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1C1E26 0%, #262730 100%);
        border: 1px solid #383A42;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #00A4E4;
        font-weight: 600;
    }
    
    /* File uploader */
    [data-testid="stFileUploaderDropzone"] {
        border: 2px dashed #00A4E4 !important;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(0, 164, 228, 0.05) 0%, rgba(0, 119, 190, 0.05) 100%);
    }
    
    /* Checkbox styling */
    .stCheckbox {
        color: #FAFAFA;
    }
    
    .stCheckbox label {
        font-weight: 500;
        color: #FAFAFA !important;
    }
    
    /* Text input */
    .stTextInput > div > div > input {
        background-color: #262730;
        color: #FAFAFA;
        border: 1px solid #383A42;
    }
    
    /* Select box */
    .stSelectbox > div > div {
        background-color: #262730;
        color: #FAFAFA;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #1C1E26 0%, #262730 100%);
        border-radius: 10px;
        font-weight: 500;
        color: #FAFAFA;
        border: 1px solid #383A42;
    }
    
    /* Text area */
    .stTextArea > div > div > textarea {
        background-color: #1C1E26;
        color: #FAFAFA;
        border: 1px solid #383A42;
    }
    
    /* Download button special styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #00D25B 0%, #00A745 100%);
        color: white !important;
        border: none;
        box-shadow: 0 4px 15px rgba(0, 210, 91, 0.3);
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #00E566 0%, #00D25B 100%);
        box-shadow: 0 6px 20px rgba(0, 210, 91, 0.4);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #B8BCC8;
        padding: 2rem 0;
        margin-top: 3rem;
        border-top: 1px solid #383A42;
    }
    
    .footer strong {
        color: #00A4E4;
    }
    
    /* Divider */
    hr {
        border-color: #383A42 !important;
    }
    
    /* Info, warning, error messages */
    .stAlert {
        background-color: #262730;
        color: #FAFAFA;
        border: 1px solid #383A42;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

def parse_form_fields_separated(form_def: Dict) -> tuple:
    """
    Parse form definition to extract fields, separating main form from repeating sections
    Returns: (main_fields, repeating_fields, repeating_sections_info)
    """
    main_fields = []
    repeating_fields = []
    repeating_sections = {}  # Track repeating section names and their parent pages
    field_occurrence_counter = {}  # Track how many times we've seen each field ID
    
    def extract_from_section(section: Dict, page_name: str, page_label: str, is_repeating: bool = False, section_name: str = None) -> None:
        """Extract fields from a section"""
        # Handle answers as array
        if section.get('answers') and isinstance(section['answers'], list):
            for answer in section['answers']:
                answer_id = answer.get('label') or answer.get('id') or answer.get('uniqueId')
                answer_name = answer.get('name') or answer.get('text') or answer.get('question') or answer_id
                answer_type = answer.get('type') or answer.get('questionType') or 'text'
                
                if answer_id and answer_name:
                    # TrueContext strips spaces and truncates IDs to 19 characters
                    clean_id = str(answer_id).replace(' ', '')[:19]
                    
                    field_data = {
                        'id': answer_id,
                        'clean_id': clean_id,
                        'name': answer_name,
                        'type': answer_type,
                        'page': page_name or page_label,
                        'section': section.get('name') or section.get('label'),
                        'question': answer.get('question') or answer.get('text') or answer_name,
                        'path': f'answers.{clean_id}',
                        'repeating_section': section_name if is_repeating else None
                    }
                    
                    # Add to appropriate list
                    if is_repeating:
                        field_data['display_name'] = f"{answer_name} (Repeating)"
                        repeating_fields.append(field_data)
                        if section_name and section_name not in repeating_sections:
                            repeating_sections[section_name] = {
                                'page': page_name,
                                'section': section.get('name') or section.get('label')
                            }
                    else:
                        field_data['display_name'] = answer_name
                        main_fields.append(field_data)

        # Handle answers as object
        if section.get('answers') and isinstance(section['answers'], dict) and not isinstance(section['answers'], list):
            for key, answer in section['answers'].items():
                if isinstance(answer, dict):
                    answer_id = answer.get('label') or answer.get('id') or key
                    answer_name = answer.get('name') or answer.get('text') or answer.get('question') or key
                    answer_type = answer.get('type') or answer.get('questionType') or 'text'
                    
                    clean_id = str(answer_id).replace(' ', '')[:19]
                    
                    field_data = {
                        'id': answer_id,
                        'clean_id': clean_id,
                        'name': answer_name,
                        'type': answer_type,
                        'page': page_name or page_label,
                        'section': section.get('name') or section.get('label'),
                        'question': answer.get('question') or answer.get('text') or answer_name,
                        'path': f'answers.{clean_id}',
                        'repeating_section': section_name if is_repeating else None
                    }
                    
                    # Add to appropriate list
                    if is_repeating:
                        field_data['display_name'] = f"{answer_name} (Repeating)"
                        repeating_fields.append(field_data)
                        if section_name and section_name not in repeating_sections:
                            repeating_sections[section_name] = {
                                'page': page_name,
                                'section': section.get('name') or section.get('label')
                            }
                    else:
                        field_data['display_name'] = answer_name
                        main_fields.append(field_data)

    def extract_from_page(page: Dict) -> None:
        """Extract fields from a page"""
        page_name = page.get('name') or page.get('label') or page.get('title')
        page_label = page.get('label') or page.get('name')
        
        # Handle sections array
        if page.get('sections') and isinstance(page['sections'], list):
            for section in page['sections']:
                # Check if this is a repeating section
                if section.get('type') == 'Repeat':
                    section_name = section.get('name') or section.get('label') or 'Repeating Section'
                    # Extract the structure from the first row/template
                    if section.get('rows') and isinstance(section['rows'], list) and len(section['rows']) > 0:
                        row = section['rows'][0]
                        if row.get('pages') and isinstance(row['pages'], list):
                            for sub_page in row['pages']:
                                if sub_page.get('sections') and isinstance(sub_page['sections'], list):
                                    for sub_section in sub_page['sections']:
                                        extract_from_section(sub_section, page_name, page_label, is_repeating=True, section_name=section_name)
                else:
                    # Regular non-repeating section
                    extract_from_section(section, page_name, page_label, is_repeating=False)

        # Handle sections as object
        if page.get('sections') and isinstance(page['sections'], dict) and not isinstance(page['sections'], list):
            for section_key, section in page['sections'].items():
                # Check if this is a repeating section
                if section.get('type') == 'Repeat':
                    section_name = section.get('name') or section.get('label') or 'Repeating Section'
                    # Extract structure from template
                    if section.get('rows') and isinstance(section['rows'], list) and len(section['rows']) > 0:
                        row = section['rows'][0]
                        if row.get('pages') and isinstance(row['pages'], list):
                            for sub_page in row['pages']:
                                if sub_page.get('sections') and isinstance(sub_page['sections'], list):
                                    for sub_section in sub_page['sections']:
                                        extract_from_section(sub_section, page_name, page_label, is_repeating=True, section_name=section_name)
                else:
                    extract_from_section(section, page_name, page_label, is_repeating=False)

    # Try different possible root structures
    
    # Option 1: Standard form definition with pages array
    if form_def.get('pages') and isinstance(form_def['pages'], list):
        for page in form_def['pages']:
            extract_from_page(page)
    
    # Option 2: Pages as object
    elif form_def.get('pages') and isinstance(form_def['pages'], dict):
        for page_key, page in form_def['pages'].items():
            extract_from_page(page)
    
    # Option 3: Direct dataRecord structure
    elif form_def.get('dataRecord', {}).get('pages'):
        data_pages = form_def['dataRecord']['pages']
        if isinstance(data_pages, list):
            for page in data_pages:
                extract_from_page(page)
        else:
            for page_key, page in data_pages.items():
                extract_from_page(page)
    
    # Option 4: Root level sections
    elif form_def.get('sections'):
        sections = form_def['sections']
        if isinstance(sections, list):
            for section in sections:
                extract_from_section(section, 'Main Page', 'main')
        else:
            for section_key, section in sections.items():
                extract_from_section(section, 'Main Page', 'main')
    
    # Option 5: Recursive search for form elements
    else:
        def find_form_elements(obj, path=''):
            if obj and isinstance(obj, dict):
                for key, value in obj.items():
                    if value and isinstance(value, dict):
                        # Check if this looks like a question/answer
                        if value.get('label') or value.get('name') or value.get('question'):
                            answer_id = value.get('label') or value.get('id') or key
                            answer_name = value.get('name') or value.get('text') or value.get('question') or key
                            answer_type = value.get('type') or value.get('questionType') or 'text'
                            
                            if answer_id and answer_name:
                                clean_id = str(answer_id).replace(' ', '')[:19]
                                
                                main_fields.append({
                                    'id': answer_id,
                                    'clean_id': clean_id,
                                    'name': answer_name,
                                    'type': answer_type,
                                    'page': path or 'Unknown',
                                    'section': 'Unknown',
                                    'question': answer_name,
                                    'path': f'answers.{clean_id}[0]'
                                })
                        elif isinstance(value, (list, dict)) and value:
                            # Recursively search deeper
                            find_form_elements(value, f"{path}.{key}" if path else key)
        
        find_form_elements(form_def)

    return main_fields, repeating_fields, repeating_sections

# Keep the old parser for backward compatibility
def parse_form_fields(form_def: Dict) -> List[Dict]:
    """Legacy parser that returns all fields combined"""
    main_fields, repeating_fields, _ = parse_form_fields_separated(form_def)
    return main_fields + repeating_fields

def generate_dual_templates(main_fields: List[Dict], repeating_fields: List[Dict], 
                           selected_main_ids: Set[str], selected_repeat_ids: Set[str],
                           repeating_sections: Dict[str, str], main_filters: List[Dict] = None, 
                           repeat_filters: List[Dict] = None) -> tuple:
    """
    Generate two FreeMarker templates: one for main form, one for repeating sections
    Returns: (main_template, repeating_template)
    """
    
    def generate_filter_condition(filters, all_fields, is_repeat=False):
        """Generate FreeMarker condition from filters"""
        if not filters:
            return ""
        
        conditions = []
        for i, filter_obj in enumerate(filters):
            if not filter_obj.get('field'):
                continue
                
            field = next((f for f in all_fields if f.get('unique_id', f['id']) == filter_obj['field']), None)
            if not field:
                continue
            
            field_path = field['path']
            if is_repeat:
                # For repeat sections, use row.fieldname
                field_path = f"row.{field['clean_id']}"
            else:
                # For main form, use full path
                field_path = f"{field['path']}[0]"
            
            operator = filter_obj.get('operator', 'equals')
            value = filter_obj.get('value', '')
            
            if operator == 'equals':
                condition = f'{field_path} == "{value}"'
            elif operator == 'not_equals':
                condition = f'{field_path} != "{value}"'
            elif operator == 'contains':
                condition = f'{field_path}?contains("{value}")'
            elif operator == 'not_contains':
                condition = f'!{field_path}?contains("{value}")'
            elif operator == 'exists':
                condition = f'{field_path}?has_content'
            elif operator == 'not_exists':
                condition = f'!{field_path}?has_content'
            else:
                condition = f'{field_path} == "{value}"'
            
            # Add logic operator for subsequent conditions
            if i > 0 and filter_obj.get('logic'):
                condition = f" {filter_obj['logic']} {condition}"
            
            conditions.append(condition)
        
        return ''.join(conditions) if conditions else ""
    
    # Generate main form template with submission ID
    main_template = "\ufeff"  # UTF-8 BOM
    main_template += '"SubmissionID","FormName","SubmissionDate"'
    
    selected_main = [f for f in main_fields if f['id'] in selected_main_ids]
    for field in selected_main:
        main_template += f',"{field["name"]}"'
    main_template += '\n'
    
    # Generate filter condition for main form (wraps entire row)
    main_condition = generate_filter_condition(main_filters, main_fields, is_repeat=False)
    
    # Data row for main form with optional filter wrapper
    if main_condition:
        main_template += f'<#if {main_condition}>\n'
    
    main_template += '"${dataRecord.submissionId}","${dataRecord.form.name}","${dataRecord.serverReceiveDate}"'
    for field in selected_main:
        main_template += f',="${{({field["path"]}[0])!""}}"'
    main_template += '\n'
    
    if main_condition:
        main_template += '</#if>\n'
    
    # Generate repeating sections template
    repeat_template = "\ufeff"  # UTF-8 BOM
    repeat_template += '"SubmissionID","SectionName","RowNumber"'
    
    selected_repeat = [f for f in repeating_fields if f['id'] in selected_repeat_ids]
    for field in selected_repeat:
        repeat_template += f',"{field["name"]}"'
    repeat_template += '\n'
    
    # Generate rows for each repeating section
    for section_name, section_info in repeating_sections.items():
        # FreeMarker loop for repeating section
        repeat_template += f'<#list answers.{section_name.replace(" ", "")} as row>\n'
        
        # Generate filter condition for repeat section (per row)
        repeat_condition = generate_filter_condition(repeat_filters, repeating_fields, is_repeat=True)
        
        if repeat_condition:
            repeat_template += f'<#if {repeat_condition}>\n'
        
        repeat_template += f'"${{dataRecord.submissionId}}","{section_name}",${{row?index + 1}}'
        
        for field in selected_repeat:
            if field.get('repeating_section') == section_name:
                repeat_template += f',="${{(row.{field["clean_id"]})!""}}"'
        
        repeat_template += '\n'
        
        if repeat_condition:
            repeat_template += '</#if>\n'
            
        repeat_template += '</#list>\n'
    
    return main_template, repeat_template

def parse_json_payload(json_payload: str) -> List[Dict]:
    """
    Parse a JSON payload to extract field paths and types for mapping
    Returns list of field information that can be mapped to form fields
    """
    try:
        payload = json.loads(json_payload)
        fields = []
        
        def extract_fields(obj, path=""):
            """Recursively extract field paths from JSON object"""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    if isinstance(value, dict):
                        fields.append({
                            'path': current_path,
                            'type': 'object',
                            'example': str(value)[:100] + "..." if len(str(value)) > 100 else str(value),
                            'mappable': False  # Objects themselves aren't directly mappable
                        })
                        extract_fields(value, current_path, "object")
                    elif isinstance(value, list):
                        fields.append({
                            'path': current_path,
                            'type': 'array',
                            'example': str(value)[:100] + "..." if len(str(value)) > 100 else str(value),
                            'mappable': False  # Arrays themselves aren't directly mappable
                        })
                        if value:  # If array has elements, analyze first element
                            extract_fields(value[0], f"{current_path}[0]")
                    else:
                        # Determine data type
                        if isinstance(value, str):
                            data_type = 'string'
                        elif isinstance(value, (int, float)):
                            data_type = 'number'
                        elif isinstance(value, bool):
                            data_type = 'boolean'
                        else:
                            data_type = 'string'
                        
                        fields.append({
                            'path': current_path,
                            'type': data_type,
                            'example': str(value),
                            'mappable': True  # These can be mapped to form fields
                        })
            elif isinstance(obj, list) and obj:
                # For arrays at root level, analyze first item
                extract_fields(obj[0], f"{path}[0]")
        
        extract_fields(payload)
        return fields
        
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON: {str(e)}")
        return []
    except Exception as e:
        st.error(f"Error parsing JSON: {str(e)}")
        return []

def generate_json_payload_template(payload_fields: List[Dict], field_mappings: Dict[str, str], form_fields: List[Dict]) -> str:
    """
    Generate a FreeMarker template for JSON payload based on field mappings
    """
    if not field_mappings:
        return ""
    
    # Group mappings by their parent paths for nested structure
    nested_mappings = {}
    for payload_path, form_field_id in field_mappings.items():
        if not form_field_id:
            continue
            
        # Find the form field details
        form_field = next((f for f in form_fields if f['id'] == form_field_id), None)
        if not form_field:
            continue
        
        # Build FreeMarker expression
        freemarker_expr = f"${{({form_field['path']}[0])!\"\"}}"
        
        # Store the mapping with context
        nested_mappings[payload_path] = {
            'freemarker': freemarker_expr,
            'form_field': form_field,
            'payload_field': next((p for p in payload_fields if p['path'] == payload_path), None)
        }
    
    # Generate the template as a JSON structure with FreeMarker expressions
    template = "{\n"
    
    for i, (path, mapping) in enumerate(nested_mappings.items()):
        if i > 0:
            template += ",\n"
        
        # Handle nested paths by creating proper JSON structure
        path_parts = path.split('.')
        indent = "  "
        
        if len(path_parts) == 1:
            # Simple key-value at root level
            template += f'{indent}"{path_parts[0]}": {mapping["freemarker"]}'
        else:
            # For now, flatten nested paths with dot notation in comments
            template += f'{indent}// Nested path: {path}\n'
            template += f'{indent}"{path_parts[-1]}": {mapping["freemarker"]}'
    
    template += "\n}"
    
    return template

def generate_freemarker_template(fields: List[Dict], selected_field_ids: Set[str], filters: List[Dict]) -> str:
    """Generate FreeMarker template based on selected fields and filters"""
    if not selected_field_ids:
        return ""
    
    # Match fields using unique_id first, then fall back to id
    selected_fields = [field for field in fields if field.get('unique_id', field['id']) in selected_field_ids]
    
    template = ""
    
    # Add CSV header with display names for clarity
    headers = [f'"{field.get("display_name", field["name"])}"' for field in selected_fields]
    template += ",".join(headers) + "\n"
    
    # Start conditional logic if filters exist
    if filters:
        conditions = []
        for i, filter_obj in enumerate(filters):
            # Find field using unique_id first, then fall back to id
            field = next((f for f in fields if f.get('unique_id', f['id']) == filter_obj['field']), None)
            if not field:
                continue
            
            field_path = field['path']
            condition = ""
            
            operator = filter_obj['operator']
            value = filter_obj['value']
            
            if operator == 'equals':
                condition = f'{field_path} == "{value}"'
            elif operator == 'not_equals':
                condition = f'{field_path} != "{value}"'
            elif operator == 'contains':
                condition = f'{field_path}?contains("{value}")'
            elif operator == 'not_contains':
                condition = f'!{field_path}?contains("{value}")'
            elif operator == 'exists':
                condition = f'{field_path}?has_content'
            elif operator == 'not_exists':
                condition = f'!{field_path}?has_content'
            else:
                condition = f'{field_path} == "{value}"'
            
            if i > 0 and filter_obj.get('logic'):
                condition = f" {filter_obj['logic']} {condition}"
            
            conditions.append(condition)
        
        if conditions:
            template += f"<#if {''.join(conditions)}>\n"
    
    # Add data row with null handling
    data_values = [f'"${{({field["path"]})!""}}"' for field in selected_fields]
    template += ",".join(data_values) + "\n"
    
    # Close conditional logic if filters exist
    if filters and any(f.get('field') for f in filters):
        template += '</#if>\n'
    
    return template

def main():
    # Branded Header
    st.markdown("""
    <div class="main-header">
        <h1>🔷 TrueContext CSV Template Generator</h1>
        <p>Create FreeMarker templates for custom CSV exports from your form definitions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'form_definition' not in st.session_state:
        st.session_state.form_definition = None
    if 'selected_fields' not in st.session_state:
        st.session_state.selected_fields = set()
    if 'filters' not in st.session_state:
        st.session_state.filters = []
    if 'generated_template' not in st.session_state:
        st.session_state.generated_template = ""
    
    # Create tabs with TrueContext styling
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "1️⃣ Upload Form Definition", 
        "2️⃣ Select Fields", 
        "3️⃣ Configure Filters", 
        "4️⃣ Generate CSV Template",
        "5️⃣ JSON Payload Builder"
    ])
    
    # Tab 1: Upload Form Definition
    with tab1:
        st.markdown("### 📁 Step 1: Upload Your Standard JSON Output")
        
        st.markdown("""
        <div class="info-card">
            <strong>ℹ️ How to get your form definition:</strong><br>
            1. Log in to your TrueContext account<br>
            2. Navigate to Data & Analytics, then Submissions (by Form)<br>
            3. Select your form and hover your mouse next to the title, Download Standard JSON (JSON)<br>
            4. Upload the downloaded JSON file below
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose your TrueContext form definition file",
            type=['json'],
            help="Upload the JSON form definition exported from TrueContext",
            label_visibility="visible"
        )
        
        if uploaded_file is not None:
            try:
                # Read the uploaded JSON file
                json_data = json.loads(uploaded_file.read().decode('utf-8'))
                st.session_state.form_definition = json_data
                
                # Parse fields
                fields = parse_form_fields(json_data)
                
                if fields:
                    st.success(f"✅ Form Definition loaded successfully! Found {len(fields)} fields.")
                    
                    # Show form summary
                    with st.expander("📋 Form Summary"):
                        pages = set()
                        sections = set()
                        for field in fields:
                            if field.get('page'):
                                pages.add(field['page'])
                            if field.get('section'):
                                sections.add(field['section'])
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Fields Found", len(fields))
                        with col2:
                            st.metric("Pages", len(pages))
                        with col3:
                            st.metric("Sections", len(sections))
                else:
                    st.warning("⚠️ No fields found in the form definition.")
                    
                    # Debug information
                    with st.expander("🔧 Debugging Information"):
                        st.write("**JSON Structure Found:**")
                        structure_info = {key: str(type(value).__name__) for key, value in json_data.items()}
                        st.json(structure_info)
                        
                        st.write("**Expected structures:**")
                        st.code("""
• Form Definition: pages → sections → answers
• Data Record: dataRecord → pages → sections → answers  
• Simplified: sections → answers
                        """)
                        
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON file. Please upload a valid TrueContext Form Definition.")
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
    
    # Tab 2: Select Fields
    with tab2:
        st.header("Select Fields for CSV")
        
        if st.session_state.form_definition:
            # Use the separated parser to get fields with unique IDs
            main_fields, repeating_fields, _ = parse_form_fields_separated(st.session_state.form_definition)
            fields = main_fields + repeating_fields
            
            # Ensure all fields have unique_id
            seen_ids = {}
            for field in fields:
                base_id = field['id']
                if base_id not in seen_ids:
                    seen_ids[base_id] = 0
                    field['unique_id'] = base_id
                else:
                    seen_ids[base_id] += 1
                    field['unique_id'] = f"{base_id}_{seen_ids[base_id]}"
            
            if fields:
                st.info(f"Select the fields you want to include in your CSV export. Currently selected: {len(st.session_state.selected_fields)} of {len(fields)} fields")
                
                # Search and filter options
                col1, col2 = st.columns([2, 1])
                with col1:
                    search_term = st.text_input("🔍 Search fields", placeholder="Type to search field names...")
                with col2:
                    select_all = st.button("Select All")
                    clear_all = st.button("Clear All")
                
                if select_all:
                    st.session_state.selected_fields = {field.get('unique_id', field['id']) for field in fields}
                    st.rerun()
                
                if clear_all:
                    st.session_state.selected_fields = set()
                    st.rerun()
                
                # Filter fields based on search
                filtered_fields = fields
                if search_term:
                    filtered_fields = [
                        field for field in fields 
                        if search_term.lower() in field['name'].lower() or 
                           search_term.lower() in field.get('page', '').lower() or
                           search_term.lower() in field.get('section', '').lower()
                    ]
                
                # Display fields in a grid
                cols = st.columns(3)
                for i, field in enumerate(filtered_fields):
                    with cols[i % 3]:
                        # Use unique_id for tracking selection
                        field_unique_id = field.get('unique_id', field['id'])
                        is_selected = field_unique_id in st.session_state.selected_fields
                        
                        # Create a checkbox for each field with truly unique key
                        # Use hash to ensure uniqueness even with special characters
                        field_hash = hashlib.md5(f"{field_unique_id}_{i}".encode()).hexdigest()[:8]
                        checkbox_key = f"field_{field_hash}_{i}"
                        display_name = field.get('display_name', field['name'])
                        
                        selected = st.checkbox(
                            f"**{display_name}**",
                            value=is_selected,
                            key=checkbox_key,
                            help=f"ID: {field['id']}\nPage: {field.get('page', 'N/A')}\nSection: {field.get('section', 'N/A')}\nType: {field.get('type', 'N/A')}\nPath: {field.get('path', 'N/A')}"
                        )
                        
                        if selected and field_unique_id not in st.session_state.selected_fields:
                            st.session_state.selected_fields.add(field_unique_id)
                        elif not selected and field_unique_id in st.session_state.selected_fields:
                            st.session_state.selected_fields.remove(field_unique_id)
                        
                        # Show field details
                        st.caption(f"📄 {field.get('page', 'N/A')} → {field.get('section', 'N/A')}")
                        if field.get('row_index') is not None:
                            st.caption(f"🏷️ {field['id']} [Row {field['row_index'] + 1}] ({field.get('type', 'N/A')})")
                        else:
                            st.caption(f"🏷️ {field['id']} ({field.get('type', 'N/A')})")
            else:
                st.warning("No fields found in the uploaded form definition.")
        else:
            st.info("Please upload a form definition first.")
    
    # Tab 3: Add Filters
    with tab3:
        st.header("Add Filters & Conditions")
        
        if st.session_state.form_definition:
            # Parse fields with separation to understand form structure
            main_fields, repeating_fields, _ = parse_form_fields_separated(st.session_state.form_definition)
            has_repeating = len(repeating_fields) > 0
            
            if has_repeating:
                st.info("""
                📋 **Dual Filter Mode**: Your form has repeating sections.
                • **Main Form Filters**: Wrap the entire submission with IF conditions
                • **Repeat Filters**: Apply per-row within repeating sections
                """)
                
                # Create tabs for different filter types
                filter_tab1, filter_tab2 = st.tabs(["Main Form Filters", "Repeating Section Filters"])
                
                # Main Form Filters
                with filter_tab1:
                    st.subheader("Main Form Data Filters")
                    st.caption("These filters determine whether the entire submission appears in the main CSV")
                    
                    if 'main_filters' not in st.session_state:
                        st.session_state.main_filters = []
                    
                    if st.button("➕ Add Main Filter"):
                        new_filter = {
                            'id': len(st.session_state.main_filters),
                            'field': '',
                            'operator': 'equals',
                            'value': '',
                            'logic': 'and'
                        }
                        st.session_state.main_filters.append(new_filter)
                        st.rerun()
                    
                    if st.session_state.main_filters:
                        for i, filter_obj in enumerate(st.session_state.main_filters):
                            with st.container():
                                cols = st.columns([1, 2, 2, 2, 1])
                                
                                with cols[0]:
                                    if i > 0:
                                        logic = st.selectbox(
                                            "Logic",
                                            options=['and', 'or'],
                                            value=filter_obj.get('logic', 'and'),
                                            key=f"main_logic_{i}"
                                        )
                                        st.session_state.main_filters[i]['logic'] = logic
                                    else:
                                        st.write("**Filter**")
                                
                                with cols[1]:
                                    field_options = [''] + [f"{field['name']} ({field['id']})" for field in main_fields]
                                    field_values = [''] + [field['id'] for field in main_fields]
                                    
                                    current_field = filter_obj.get('field', '')
                                    try:
                                        field_index = field_values.index(current_field) if current_field in field_values else 0
                                    except ValueError:
                                        field_index = 0
                                    
                                    selected_field_index = st.selectbox(
                                        "Main Field",
                                        range(len(field_options)),
                                        format_func=lambda x: field_options[x],
                                        index=field_index,
                                        key=f"main_field_{i}"
                                    )
                                    st.session_state.main_filters[i]['field'] = field_values[selected_field_index]
                                
                                with cols[2]:
                                    operator = st.selectbox(
                                        "Operator",
                                        options=['equals', 'not_equals', 'contains', 'not_contains', 'exists', 'not_exists'],
                                        format_func=lambda x: {
                                            'equals': 'Equals',
                                            'not_equals': 'Not Equals',
                                            'contains': 'Contains',
                                            'not_contains': 'Does Not Contain',
                                            'exists': 'Has Value',
                                            'not_exists': 'Is Empty'
                                        }[x],
                                        index=['equals', 'not_equals', 'contains', 'not_contains', 'exists', 'not_exists'].index(filter_obj.get('operator', 'equals')),
                                        key=f"main_operator_{i}"
                                    )
                                    st.session_state.main_filters[i]['operator'] = operator
                                
                                with cols[3]:
                                    if operator not in ['exists', 'not_exists']:
                                        value = st.text_input(
                                            "Value",
                                            value=filter_obj.get('value', ''),
                                            key=f"main_value_{i}"
                                        )
                                        st.session_state.main_filters[i]['value'] = value
                                    else:
                                        st.write("(no value needed)")
                                
                                with cols[4]:
                                    if st.button("🗑️", key=f"main_remove_{i}"):
                                        st.session_state.main_filters.pop(i)
                                        st.rerun()
                                
                                st.divider()
                    else:
                        st.info("No main form filters added yet.")
                
                # Repeating Section Filters
                with filter_tab2:
                    st.subheader("Repeating Section Row Filters")
                    st.caption("These filters determine which rows from repeating sections appear in the repeating CSV")
                    
                    if 'repeat_filters' not in st.session_state:
                        st.session_state.repeat_filters = []
                    
                    if st.button("➕ Add Repeat Filter"):
                        new_filter = {
                            'id': len(st.session_state.repeat_filters),
                            'field': '',
                            'operator': 'equals',
                            'value': '',
                            'logic': 'and'
                        }
                        st.session_state.repeat_filters.append(new_filter)
                        st.rerun()
                    
                    if st.session_state.repeat_filters:
                        for i, filter_obj in enumerate(st.session_state.repeat_filters):
                            with st.container():
                                cols = st.columns([1, 2, 2, 2, 1])
                                
                                with cols[0]:
                                    if i > 0:
                                        logic = st.selectbox(
                                            "Logic",
                                            options=['and', 'or'],
                                            value=filter_obj.get('logic', 'and'),
                                            key=f"repeat_logic_{i}"
                                        )
                                        st.session_state.repeat_filters[i]['logic'] = logic
                                    else:
                                        st.write("**Filter**")
                                
                                with cols[1]:
                                    field_options = [''] + [f"{field['name']} ({field['id']})" for field in repeating_fields]
                                    field_values = [''] + [field['id'] for field in repeating_fields]
                                    
                                    current_field = filter_obj.get('field', '')
                                    try:
                                        field_index = field_values.index(current_field) if current_field in field_values else 0
                                    except ValueError:
                                        field_index = 0
                                    
                                    selected_field_index = st.selectbox(
                                        "Repeat Field",
                                        range(len(field_options)),
                                        format_func=lambda x: field_options[x],
                                        index=field_index,
                                        key=f"repeat_field_{i}"
                                    )
                                    st.session_state.repeat_filters[i]['field'] = field_values[selected_field_index]
                                
                                with cols[2]:
                                    operator = st.selectbox(
                                        "Operator",
                                        options=['equals', 'not_equals', 'contains', 'not_contains', 'exists', 'not_exists'],
                                        format_func=lambda x: {
                                            'equals': 'Equals',
                                            'not_equals': 'Not Equals',
                                            'contains': 'Contains',
                                            'not_contains': 'Does Not Contain',
                                            'exists': 'Has Value',
                                            'not_exists': 'Is Empty'
                                        }[x],
                                        index=['equals', 'not_equals', 'contains', 'not_contains', 'exists', 'not_exists'].index(filter_obj.get('operator', 'equals')),
                                        key=f"repeat_operator_{i}"
                                    )
                                    st.session_state.repeat_filters[i]['operator'] = operator
                                
                                with cols[3]:
                                    if operator not in ['exists', 'not_exists']:
                                        value = st.text_input(
                                            "Value",
                                            value=filter_obj.get('value', ''),
                                            key=f"repeat_value_{i}"
                                        )
                                        st.session_state.repeat_filters[i]['value'] = value
                                    else:
                                        st.write("(no value needed)")
                                
                                with cols[4]:
                                    if st.button("🗑️", key=f"repeat_remove_{i}"):
                                        st.session_state.repeat_filters.pop(i)
                                        st.rerun()
                                
                                st.divider()
                    else:
                        st.info("No repeating section filters added yet.")
            
            else:
                # Single template mode - use existing filter UI
                fields = parse_form_fields(st.session_state.form_definition)
                
                if fields:
                    st.info("📋 **Single Template Mode**: Your form has no repeating sections.")
                    
                    # Add new filter button
                    if st.button("➕ Add Filter"):
                        new_filter = {
                            'id': len(st.session_state.filters),
                            'field': '',
                            'operator': 'equals',
                            'value': '',
                            'logic': 'and'
                        }
                        st.session_state.filters.append(new_filter)
                        st.rerun()
                    
                    # Display existing filters
                    if st.session_state.filters:
                        st.write("**Current Filters:**")
                        
                        for i, filter_obj in enumerate(st.session_state.filters):
                            with st.container():
                                cols = st.columns([1, 2, 2, 2, 1])
                                
                                # Logic operator (for filters after the first)
                                with cols[0]:
                                    if i > 0:
                                        logic = st.selectbox(
                                            "Logic",
                                            options=['and', 'or'],
                                            value=filter_obj.get('logic', 'and'),
                                            key=f"logic_{i}"
                                        )
                                        st.session_state.filters[i]['logic'] = logic
                                    else:
                                        st.write("**Filter**")
                                
                                # Field selection
                                with cols[1]:
                                    field_options = [''] + [f"{field['name']} ({field['id']})" for field in fields]
                                    field_values = [''] + [field['id'] for field in fields]
                                    
                                    current_field = filter_obj.get('field', '')
                                    try:
                                        field_index = field_values.index(current_field) if current_field in field_values else 0
                                    except ValueError:
                                        field_index = 0
                                    
                                    selected_field_index = st.selectbox(
                                        "Field",
                                        range(len(field_options)),
                                        format_func=lambda x: field_options[x],
                                        index=field_index,
                                        key=f"field_{i}"
                                    )
                                    st.session_state.filters[i]['field'] = field_values[selected_field_index]
                                
                                # Operator selection
                                with cols[2]:
                                    operator = st.selectbox(
                                        "Operator",
                                        options=['equals', 'not_equals', 'contains', 'not_contains', 'exists', 'not_exists'],
                                        format_func=lambda x: {
                                            'equals': 'Equals',
                                            'not_equals': 'Not Equals',
                                            'contains': 'Contains',
                                            'not_contains': 'Does Not Contain',
                                            'exists': 'Has Value',
                                            'not_exists': 'Is Empty'
                                        }[x],
                                        index=['equals', 'not_equals', 'contains', 'not_contains', 'exists', 'not_exists'].index(filter_obj.get('operator', 'equals')),
                                        key=f"operator_{i}"
                                    )
                                    st.session_state.filters[i]['operator'] = operator
                                
                                # Value input (only for operators that need a value)
                                with cols[3]:
                                    if operator not in ['exists', 'not_exists']:
                                        value = st.text_input(
                                            "Value",
                                            value=filter_obj.get('value', ''),
                                            key=f"value_{i}"
                                        )
                                        st.session_state.filters[i]['value'] = value
                                    else:
                                        st.write("(no value needed)")
                                
                                # Remove button
                                with cols[4]:
                                    if st.button("🗑️", key=f"remove_{i}"):
                                        st.session_state.filters.pop(i)
                                        st.rerun()
                                
                                st.divider()
                    else:
                        st.info("No filters added yet. Add filters to conditionally include records in your CSV export.")
                else:
                    st.warning("No fields available for filtering.")
        else:
            st.info("Please upload a form definition first.")
    
    # Tab 4: Generate Template
    with tab4:
        st.header("Generated FreeMarker Templates")
        
        if st.session_state.form_definition:
            # Parse fields with separation
            main_fields, repeating_fields, repeating_sections = parse_form_fields_separated(st.session_state.form_definition)
            
            # Check if form has repeating sections
            has_repeating = len(repeating_fields) > 0
            
            if has_repeating:
                st.info("""
                📊 **Dual Template Mode**: Your form contains repeating sections/tables.
                Two CSV templates will be generated:
                1. **Main Form CSV** - One row per submission (using main form fields from Tab 2)
                2. **Repeating Data CSV** - Multiple rows per submission (using repeating fields from Tab 2)
                
                Both CSVs will include a SubmissionID field for joining the data.
                """)
                
                # Use fields already selected in Tab 2
                if st.session_state.selected_fields:
                    # Separate selected fields into main and repeating based on the fields' properties
                    selected_main_ids = set()
                    selected_repeat_ids = set()
                    
                    # Get unique_id mapping for selected fields
                    all_fields = main_fields + repeating_fields
                    seen_ids = {}
                    for field in all_fields:
                        base_id = field['id']
                        if base_id not in seen_ids:
                            seen_ids[base_id] = 0
                            field['unique_id'] = base_id
                        else:
                            seen_ids[base_id] += 1
                            field['unique_id'] = f"{base_id}_{seen_ids[base_id]}"
                    
                    # Categorize selected fields
                    for field in all_fields:
                        field_unique_id = field.get('unique_id', field['id'])
                        if field_unique_id in st.session_state.selected_fields:
                            if field.get('repeating_section'):
                                selected_repeat_ids.add(field['id'])
                            else:
                                selected_main_ids.add(field['id'])
                    
                    # Show field summary
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Main Form Fields Selected")
                        main_selected = [f for f in main_fields if f['id'] in selected_main_ids]
                        if main_selected:
                            for field in main_selected:
                                st.write(f"✅ {field['name']}")
                        else:
                            st.write("No main form fields selected")
                    
                    with col2:
                        st.subheader("Repeating Section Fields Selected")
                        repeat_selected = [f for f in repeating_fields if f['id'] in selected_repeat_ids]
                        if repeat_selected:
                            for field in repeat_selected:
                                section_label = f" ({field.get('repeating_section', 'Table')})"
                                st.write(f"✅ {field['name']}{section_label}")
                        else:
                            st.write("No repeating section fields selected")
                    
                    # Generate templates button
                    if st.button("🔄 Generate Dual Templates", type="primary"):
                        # Get filters from session state
                        main_filters = st.session_state.get('main_filters', [])
                        repeat_filters = st.session_state.get('repeat_filters', [])
                        
                        main_template, repeat_template = generate_dual_templates(
                            main_fields, repeating_fields,
                            selected_main_ids, selected_repeat_ids,
                            repeating_sections, main_filters, repeat_filters
                        )
                        st.session_state.main_template = main_template
                        st.session_state.repeat_template = repeat_template
                else:
                    st.warning("⚠️ Please select fields in Tab 2 first before generating templates.")
                
                # Show and download templates
                if 'main_template' in st.session_state and 'repeat_template' in st.session_state:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📄 Main Form Template")
                        st.download_button(
                            label="📥 Download Main.ftl",
                            data=st.session_state.main_template,
                            file_name="main-form.ftl",
                            mime="text/plain"
                        )
                        with st.expander("Preview Main Template"):
                            st.code(st.session_state.main_template, language="freemarker")
                    
                    with col2:
                        st.subheader("📄 Repeating Data Template")
                        st.download_button(
                            label="📥 Download Repeating.ftl",
                            data=st.session_state.repeat_template,
                            file_name="repeating-data.ftl",
                            mime="text/plain"
                        )
                        with st.expander("Preview Repeating Template"):
                            st.code(st.session_state.repeat_template, language="freemarker")
            
            else:
                # Single template mode for forms without repeating sections
                if st.session_state.selected_fields:
                    fields = parse_form_fields(st.session_state.form_definition)
                    
                    # Generate template button
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("🔄 Generate Template", type="primary"):
                            template = generate_freemarker_template(
                                fields, 
                                st.session_state.selected_fields, 
                                st.session_state.filters
                            )
                            st.session_state.generated_template = template
                    
                    # Show template if generated
                    if st.session_state.generated_template:
                        with col2:
                            # Download button
                            st.download_button(
                                label="📥 Download .ftl",
                                data=st.session_state.generated_template,
                                file_name="truecontext-csv-template.ftl",
                                mime="text/plain"
                            )
                
                        # Template summary
                        st.info(f"""
                        **Template Summary:**
                        • {len(st.session_state.selected_fields)} columns selected
                        • {len([f for f in st.session_state.filters if f.get('field')])} filters applied
                        • Ready to use with TrueContext FreeMarker Document
                        """)
                        
                        # Show template content
                        st.text_area(
                            "Generated FreeMarker Template",
                            value=st.session_state.generated_template,
                            height=400,
                            help="Copy this template to use in your TrueContext FreeMarker document"
                        )
                else:
                    st.info("Please select at least one field in the 'Select Fields' tab.")
        else:
            st.warning("Please upload a form definition first.")
    
    # Tab 5: JSON Payload Builder
    with tab5:
        st.header("🔧 JSON Payload Builder")
        st.markdown("Build FreeMarker templates for JSON payloads by mapping form fields to JSON structure")
        
        if st.session_state.form_definition:
            # Get all available form fields
            fields = parse_form_fields(st.session_state.form_definition)
            
            if fields:
                # Initialize session state for JSON payload
                if 'json_payload' not in st.session_state:
                    st.session_state.json_payload = ""
                if 'payload_fields' not in st.session_state:
                    st.session_state.payload_fields = []
                if 'field_mappings' not in st.session_state:
                    st.session_state.field_mappings = {}
                
                st.markdown("""
                <div class="info-card">
                    <strong>📋 How to use:</strong><br>
                    1. Paste a sample JSON request body below<br>
                    2. The tool will parse the JSON structure<br>
                    3. Map each JSON field to a form field<br>
                    4. Generate a FreeMarker template for the JSON payload
                </div>
                """, unsafe_allow_html=True)
                
                # JSON input area
                st.subheader("Sample JSON Request Body")
                json_input = st.text_area(
                    "Paste your sample JSON payload here:",
                    value=st.session_state.json_payload,
                    height=200,
                    placeholder='{\n  "name": "John Doe",\n  "email": "john@example.com",\n  "age": 30,\n  "address": {\n    "street": "123 Main St",\n    "city": "Anytown"\n  }\n}',
                    help="Paste a sample JSON request body that you want to generate a template for"
                )
                
                if json_input != st.session_state.json_payload:
                    st.session_state.json_payload = json_input
                    st.session_state.payload_fields = parse_json_payload(json_input)
                    st.session_state.field_mappings = {}  # Reset mappings when JSON changes
                    st.rerun()
                
                if st.session_state.payload_fields:
                    st.subheader("Field Mapping")
                    st.markdown("Map JSON fields to your form fields:")
                    
                    # Create form field options for dropdowns
                    form_field_options = [''] + [f"{field['name']} ({field['id']})" for field in fields]
                    form_field_values = [''] + [field['id'] for field in fields]
                    
                    # Display mappable fields
                    mappable_fields = [f for f in st.session_state.payload_fields if f['mappable']]
                    
                    if mappable_fields:
                        for i, payload_field in enumerate(mappable_fields):
                            with st.container():
                                col1, col2, col3 = st.columns([2, 2, 1])
                                
                                with col1:
                                    st.write(f"**{payload_field['path']}**")
                                    st.caption(f"Type: {payload_field['type']} | Example: {payload_field['example']}")
                                
                                with col2:
                                    current_mapping = st.session_state.field_mappings.get(payload_field['path'], '')
                                    try:
                                        field_index = form_field_values.index(current_mapping) if current_mapping in form_field_values else 0
                                    except ValueError:
                                        field_index = 0
                                    
                                    selected_field_index = st.selectbox(
                                        "Map to Form Field",
                                        range(len(form_field_options)),
                                        format_func=lambda x: form_field_options[x],
                                        index=field_index,
                                        key=f"mapping_{payload_field['path']}_{i}",
                                        label_visibility="collapsed"
                                    )
                                    
                                    st.session_state.field_mappings[payload_field['path']] = form_field_values[selected_field_index]
                                
                                with col3:
                                    if st.session_state.field_mappings.get(payload_field['path']):
                                        st.markdown("✅ **Mapped**")
                                    else:
                                        st.markdown("⚪ Not mapped")
                                
                                st.divider()
                        
                        # Generate template button
                        mapped_count = len([m for m in st.session_state.field_mappings.values() if m])
                        if mapped_count > 0:
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                if st.button("🔄 Generate JSON Template", type="primary"):
                                    json_template = generate_json_payload_template(
                                        st.session_state.payload_fields,
                                        st.session_state.field_mappings,
                                        fields
                                    )
                                    st.session_state.json_template = json_template
                            
                            with col2:
                                st.info(f"📊 {mapped_count} of {len(mappable_fields)} fields mapped")
                            
                            # Show generated template
                            if 'json_template' in st.session_state and st.session_state.json_template:
                                st.subheader("Generated JSON FreeMarker Template")
                                
                                col1, col2 = st.columns([3, 1])
                                with col2:
                                    st.download_button(
                                        label="📥 Download JSON Template",
                                        data=st.session_state.json_template,
                                        file_name="json-payload-template.ftl",
                                        mime="text/plain"
                                    )
                                
                                st.text_area(
                                    "FreeMarker JSON Template",
                                    value=st.session_state.json_template,
                                    height=300,
                                    help="Copy this template to use in your TrueContext FreeMarker document for JSON payloads"
                                )
                        else:
                            st.info("Map at least one field to generate a template")
                    else:
                        st.info("No mappable fields found in the JSON structure")
                
                elif json_input:
                    st.error("Please provide valid JSON to parse")
                else:
                    st.info("Enter a sample JSON payload above to get started")
            else:
                st.warning("No fields found in the uploaded form definition.")
        else:
            st.info("Please upload a form definition first in Tab 1.")
    
    # Progress indicator with TrueContext styling
    st.markdown("---")
    st.markdown("### 📊 Progress Tracker")
    
    progress_cols = st.columns(5)
    
    with progress_cols[0]:
        if st.session_state.form_definition:
            st.markdown("""
            <div class="progress-success" style="text-align: center;">
                <h3 style="color: white; margin: 0;">✅</h3>
                <p style="color: white; margin: 0; font-weight: 500;">Form Uploaded</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="progress-pending" style="text-align: center;">
                <h3 style="color: #B8BCC8; margin: 0;">⏳</h3>
                <p style="color: #B8BCC8; margin: 0;">Awaiting Upload</p>
            </div>
            """, unsafe_allow_html=True)
    
    with progress_cols[1]:
        if st.session_state.selected_fields:
            st.markdown(f"""
            <div class="progress-success" style="text-align: center;">
                <h3 style="color: white; margin: 0;">✅</h3>
                <p style="color: white; margin: 0; font-weight: 500;">{len(st.session_state.selected_fields)} Fields</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="progress-pending" style="text-align: center;">
                <h3 style="color: #B8BCC8; margin: 0;">⏳</h3>
                <p style="color: #B8BCC8; margin: 0;">Select Fields</p>
            </div>
            """, unsafe_allow_html=True)
    
    with progress_cols[2]:
        # Count filters from both single and dual filter modes
        single_filters = len([f for f in st.session_state.get('filters', []) if f.get('field')])
        main_filters = len([f for f in st.session_state.get('main_filters', []) if f.get('field')])
        repeat_filters = len([f for f in st.session_state.get('repeat_filters', []) if f.get('field')])
        total_filters = single_filters + main_filters + repeat_filters
        
        if total_filters > 0:
            st.markdown(f"""
            <div class="progress-info" style="text-align: center;">
                <h3 style="color: white; margin: 0;">🔍</h3>
                <p style="color: white; margin: 0; font-weight: 500;">{total_filters} Filters</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="progress-pending" style="text-align: center;">
                <h3 style="color: #B8BCC8; margin: 0;">⭕</h3>
                <p style="color: #B8BCC8; margin: 0;">No Filters</p>
            </div>
            """, unsafe_allow_html=True)
    
    with progress_cols[3]:
        template_ready = (
            ('generated_template' in st.session_state and st.session_state.generated_template) or
            ('main_template' in st.session_state and st.session_state.main_template)
        )
        if template_ready:
            st.markdown("""
            <div class="progress-success" style="text-align: center;">
                <h3 style="color: white; margin: 0;">✅</h3>
                <p style="color: white; margin: 0; font-weight: 500;">CSV Ready</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="progress-pending" style="text-align: center;">
                <h3 style="color: #B8BCC8; margin: 0;">⏳</h3>
                <p style="color: #B8BCC8; margin: 0;">Generate CSV</p>
            </div>
            """, unsafe_allow_html=True)
    
    with progress_cols[4]:
        json_template_ready = 'json_template' in st.session_state and st.session_state.json_template
        if json_template_ready:
            st.markdown("""
            <div class="progress-success" style="text-align: center;">
                <h3 style="color: white; margin: 0;">✅</h3>
                <p style="color: white; margin: 0; font-weight: 500;">JSON Ready</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="progress-pending" style="text-align: center;">
                <h3 style="color: #B8BCC8; margin: 0;">⭕</h3>
                <p style="color: #B8BCC8; margin: 0;">Optional</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer with TrueContext branding
    st.markdown("""
    <div class="footer">
        <p>
            <strong>TrueContext CSV Template Generator</strong><br>
            Part of the TrueContext Platform | Formerly ProntoForms<br>
            <small>© 2024 TrueContext. All rights reserved.</small>
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()