def load_recipients_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            numbers = [num.strip() for num in content.split(',') if num.strip()]
            return numbers
    except Exception as e:
        print(f"Error loading recipients from {file_path}: {e}")
        return []
