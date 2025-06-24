def parse_diagnosis_from_header(header_content_string):
    target_key = "# reason for admission:" 
    for line in header_content_string.splitlines():
        cleaned_line = line.strip().lower() 
        if target_key in cleaned_line:
            diagnosis = cleaned_line.split(':', 1)[1].strip()
            if 'myocardial infarction' in diagnosis:
                return 'Myocardial Infarction'
            return diagnosis.capitalize()
    return None