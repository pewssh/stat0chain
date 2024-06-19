import time
import random
import string
import subprocess
import csv
import logging
import colorlog
import uuid
import statistics
from collections import defaultdict
import sys
import os


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create a colorlog handler
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red,bg_white',
    }
))
logger.addHandler(handler)

total_data_parity_max = 6

def generate_random_file(filename, size_in_kb):
    content = ''.join(random.choices(string.ascii_letters + string.digits, k=size_in_kb * 1024))
    with open(filename, 'w') as file:
        file.write(content)

# def generate_random_file(filename, size_in_bytes):
    # random_bytes = os.urandom(size_in_bytes)
    # with open(filename, 'wb') as file:
        # file.write(random_bytes)



def create_allocation(data, parity):
    if data + parity > total_data_parity_max:
        return "Data + Parity should be less than 46"
    command = "./zbox newallocation   --data {} --parity {} --lock 10".format(data, parity)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print("Output:", result.stdout)
    allocationId = result.stdout.split(" ")[-1].strip()
    logging.info( "Allocation :{} created with data: {} and parity: {}".format(allocationId, data, parity))
    return allocationId


def generate_data_parity(data, parity):
    cases = []
    i = max(data, parity)
    j = min(data, parity)
    for k in range(1, i+1):
        for l in range(1, j+1):
            cases.append((k, l))

    return cases

# ./zbox upload --localpath /absolute-path-to-local-file/hello.txt --remotepath /myfiles/hello.txt --allocation d0939e912851959637257573b08c748474f0dd0ebbc8e191e4f6ad69e4fdc7ac

def upload_file(allocation, file, remotepath):
    command = "./zbox upload --localpath {} --remotepath /{} --allocation {}".format(file, remotepath, allocation)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print("Output:", result.stdout)
    print("Error" , result.stderr)
    if "Error" in result.stderr:
        raise Exception("Filename already exists in the allocation. Please try with different filename.")
    return "File uploaded"


KB = 1024
MB = 1024 * KB
GB = 1024 * MB

def create_allocation_upload_file(data, parity):
    appended_data =[]
    allocationId = create_allocation(data, parity)

    max_size_in_bytes = 0.5 * GB
    base_size_in_bytes = 500 * KB
    num_files = 5

    for i in range(1,1):
        size_in_bytes = base_size_in_bytes + int(i * (max_size_in_bytes - base_size_in_bytes) / (num_files - 1))
        filename = "file_new{}.txt".format(uuid.uuid4())
        logging.info(f"Generating random file {filename} of size {size_in_bytes} bytes")
        generate_random_file(filename, size_in_bytes)
        logging.info(f"File Generated {filename} of size {size_in_bytes} bytes")
        start = time.time()
        try:
            logging.info(f"Uploading file {filename} of size {size_in_bytes} bytes")
            upload_file(allocationId, filename, filename)
            end = time.time()
            print("Time taken to write file: ", end - start)

            row = {
                "Data": data,
                "Parity": parity,
                "File Size": str(size_in_bytes/ (1024 ** 3)) + "GB",
                "Time": str(end - start) + "seconds"
            }
            appended_data.append(row)
        except Exception as e:
            logging.error(f"Benchmarking Failed with error: {str(e)}")
            break

        finally:
            subprocess.run("rm -rf {}".format(filename), shell=True)
    return appended_data

# main method 
def mean_data(res):
    grouped_data = defaultdict(list)

    for record in res:
        keys = (record['Data'], record['Parity'], record['File Size'])  # Extract keys as a tuple
        seconds_str = record['Time'].replace('seconds', '').strip()  # Remove 'seconds' and strip spaces
        seconds = float(seconds_str)  # Convert to float
        
        grouped_data[keys].append(seconds)

    # calculate mean
    mean_results = {}
    for keys, times in grouped_data.items():
        mean_time = statistics.mean(times)
        mean_results[keys] = mean_time

    result_list = [{'Data':key[0], 'Parity':key[1], 'File Size': key[2], 'Time Taken': value} for key, value in mean_results.items()]
    return result_list



def draw_plot():
    df = pd.read_csv('benchmark.csv')
    print(df.head())

    fig, ax = plt.subplots()

    groups = df.groupby(['Data', 'Parity', 'File Size'])
    for key, group in groups:
        label = f"({key[0]}, {key[1]}, {key[2]})"
        ax.plot(group.index, group['Time Taken'], marker='o', linestyle='-', label=label)

    ax.set_xlabel('Configuration combination of data, parity and size')
    ax.set_ylabel('Time Taken In seconds')
    ax.set_title('Time Taken for Different Configurations')

    plt.xticks(ticks=range(len(groups)), labels=[f"({key[0]}, {key[1]}, {key[2]})" for key, _ in groups], rotation=45, ha='right')


    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5) )
    plt.tight_layout()
    plt.savefig('plot.png', dpi=300)  



if __name__ == "__main__":
    # get value from terminal
    try:
        data = int(sys.argv[1])
        parity = int(sys.argv[2])
    except Exception as e:
        print("Please provide data and parity as command line arguments")
        print("Example: python3 main.py 2 2")
        exit(1)

    cases = generate_data_parity(data, parity)
    cases= cases * 2
    cases.sort()
    total_result=   []
    for case in cases:
        result = create_allocation_upload_file(data=case[0], parity=case[1])
        total_result.extend(result)

    # calculate for mean
        
    final_result = mean_data(total_result)
    with open("benchmark.csv", "w") as file:
        writer = csv.DictWriter(file, fieldnames=["Data", "Parity", "File Size", "Time Taken"])
        writer.writeheader()
        writer.writerows(final_result)

    # call draw plot
    draw_plot()
