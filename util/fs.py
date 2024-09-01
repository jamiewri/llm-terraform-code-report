def write_file_to_disk(content: str, filename):
    with open(filename, 'w') as file:
        file.write(content)

def load_file_as_string(path: str) -> str:
    with open(path, 'r') as file:
        string = file.read()
    return string