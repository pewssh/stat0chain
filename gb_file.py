import random
import string
import threading

# Function to generate random content for a given chunk size
def generate_random_content(size):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=size))

def write_to_file(filename, start_byte, end_byte):
    with open(filename, 'r+b') as file:
        file.seek(start_byte)
        while start_byte < end_byte:
            chunk_size = min(10 * 1024 * 1024, end_byte - start_byte)
            content = generate_random_content(chunk_size)
            file.write(content.encode())
            start_byte += chunk_size

# Function to generate a 1 GB file using multithreading
def generate_1GB_file(filename):
    size_in_b = 1 * 1024 * 1024 * 1024  # 1 GB in bytes
    chunk_size = size_in_b  # Single chunk for simplicity

    # Open the file in write mode to create it
    with open(filename, 'wb') as file:
        file.write(b'\0' * size_in_b)  # Write zeros to allocate space

    # Write content using a single thread (for simplicity)
    write_to_file(filename, 0, size_in_b)

# Generate the 1 GB file using multithreading
generate_1GB_file("dummy_file_1GB.txt")
