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

# Page configuration
st.set_page_config(
    page_title="TrueContext CSV Generator", 
    page_icon="📊",
    layout="wide"
)

def parse_form_fields(form_def: Dict) -> List[Dict]:
    """Parse form definition to extract all available fields"""
    fields = []
    
    def extract_from_section(section: Dict, page_name: str, page_label: str) -> None:
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
                    
                    fields.append({
                        'id': answer_id,
                        'clean_id': clean_id,
                        'name': answer_name,
                        'type': answer_type,
                        'page': page_name or page_label,
                        'section': section.get('name') or section.get('label'),
                        'question': answer.get('question') or answer.get('text') or answer_name,
                        'path': f'answers.{clean_id}[0]'
                    })

        # Handle answers as object
        if section.get('answers') and isinstance(section['answers'], dict) and not isinstance(section['answers'], list):
            for key, answer in section['answers'].items():
                if isinstance(answer, dict):
                    answer_id = answer.get('label') or answer.get('id') or key
                    answer_name = answer.get('name') or answer.get('text') or answer.get('question') or key
                    answer_type = answer.get('type') or answer.get('questionType') or 'text'
                    
                    clean_id = str(answer_id).replace(' ', '')[:19]
                    
                    fields.append({
                        'id': answer_id,
                        'clean_id': clean_id,
                        'name': answer_name,
                        'type': answer_type,
                        'page': page_name or page_label,
                        'section': section.get('name') or section.get('label'),
                        'question': answer.get('question') or answer.get('text') or answer_name,
                        'path': f'answers.{clean_id}[0]'
                    })

    def extract_from_page(page: Dict) -> None:
        """Extract fields from a page"""
        page_name = page.get('name') or page.get('label') or page.get('title')
        page_label = page.get('label') or page.get('name')
        
        # Handle sections array
        if page.get('sections') and isinstance(page['sections'], list):
            for section in page['sections']:
                extract_from_section(section, page_name, page_label)
                
                # Handle repeatable sections (type: "Repeat")
                if section.get('type') == 'Repeat' and section.get('rows') and isinstance(section['rows'], list):
                    for row_index, row in enumerate(section['rows']):
                        if row.get('pages') and isinstance(row['pages'], list):
                            for sub_page in row['pages']:
                                if sub_page.get('sections') and isinstance(sub_page['sections'], list):
                                    for sub_section in sub_page['sections']:
                                        extract_from_section(sub_section, f"{page_name} (Row {row_index + 1})", page_label)

        # Handle sections as object
        if page.get('sections') and isinstance(page['sections'], dict) and not isinstance(page['sections'], list):
            for section_key, section in page['sections'].items():
                extract_from_section(section, page_name, page_label)

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
                                
                                fields.append({
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

    return fields

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
    # Header
    st.title("📊 TrueContext CSV Generator")
    st.markdown("Generate FreeMarker templates for custom CSV exports from TrueContext Form Definitions")
    
    # Initialize session state
    if 'form_definition' not in st.session_state:
        st.session_state.form_definition = None
    if 'selected_fields' not in st.session_state:
        st.session_state.selected_fields = set()
    if 'filters' not in st.session_state:
        st.session_state.filters = []
    if 'generated_template' not in st.session_state:
        st.session_state.generated_template = ""
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload Form", "✅ Select Fields", "🔍 Add Filters", "📄 Template"])
    
    # Tab 1: Upload Form Definition
    with tab1:
        st.header("Upload Form Definition")
        
        uploaded_file = st.file_uploader(
            "Select a JSON file containing your TrueContext Form Definition",
            type=['json'],
            help="Upload the JSON form definition from TrueContext"
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
            fields = parse_form_fields(st.session_state.form_definition)
            
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
                    st.session_state.selected_fields = {field['id'] for field in fields}
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
                        is_selected = field['id'] in st.session_state.selected_fields
                        
                        # Create a checkbox for each field
                        checkbox_key = f"field_{field['id']}"
                        selected = st.checkbox(
                            f"**{field['name']}**",
                            value=is_selected,
                            key=checkbox_key,
                            help=f"ID: {field['id']}\nPage: {field.get('page', 'N/A')}\nSection: {field.get('section', 'N/A')}\nType: {field.get('type', 'N/A')}"
                        )
                        
                        if selected and field['id'] not in st.session_state.selected_fields:
                            st.session_state.selected_fields.add(field['id'])
                        elif not selected and field['id'] in st.session_state.selected_fields:
                            st.session_state.selected_fields.remove(field['id'])
                        
                        # Show field details
                        st.caption(f"📄 {field.get('page', 'N/A')} → {field.get('section', 'N/A')}")
                        st.caption(f"🏷️ {field['id']} ({field.get('type', 'N/A')})")
            else:
                st.warning("No fields found in the uploaded form definition.")
        else:
            st.info("Please upload a form definition first.")
    
    # Tab 3: Add Filters
    with tab3:
        st.header("Add Filters & Conditions")
        
        if st.session_state.form_definition:
            fields = parse_form_fields(st.session_state.form_definition)
            
            if fields:
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
        st.header("Generated FreeMarker Template")
        
        if st.session_state.form_definition and st.session_state.selected_fields:
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
                st.info("Click 'Generate Template' to create your FreeMarker template.")
        
        elif not st.session_state.form_definition:
            st.warning("Please upload a form definition first.")
        elif not st.session_state.selected_fields:
            st.warning("Please select at least one field in the 'Select Fields' tab.")
    
    # Progress footer
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.form_definition:
            st.success("✅ Form Uploaded")
        else:
            st.error("❌ Form Not Uploaded")
    
    with col2:
        if st.session_state.selected_fields:
            st.success(f"✅ {len(st.session_state.selected_fields)} Fields Selected")
        else:
            st.error("❌ No Fields Selected")
    
    with col3:
        if st.session_state.generated_template:
            st.success("✅ Template Ready")
        else:
            st.error("❌ Template Not Generated")

if __name__ == "__main__":
    main()