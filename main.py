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

total_data_parity_max = 40

def generate_random_file(index):
    files = os.listdir()
    files = [file for file in files if file.startswith("dummy")]

    if len(files) == 0:
        raise Exception("No files generated by generate_test_files.py. Please run generate_test_files.py first")
    
    return files[index], os.path.getsize(files[index])

def create_allocation(data, parity, lock):
    if data + parity > total_data_parity_max:
        return "Data + Parity should be less than 46"
    command = "./zbox newallocation   --data {} --parity {} --lock {} --size 4294967296".format(data, parity, lock)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print("Output:", result.stdout)
    if "Error" in result.stdout:
        raise Exception(result.stdout)
    allocationId = result.stdout.split(" ")[-1].strip()
    logging.info( "Allocation :{} created with data: {} and parity: {}".format(allocationId, data, parity))
    return allocationId


def generate_data_parity(data, parity,max_blobbers=total_data_parity_max):
    base_data=data
    base_parity = parity
    cases = []

    for i in range(1, max_blobbers):
        if data+parity <= max_blobbers:
            cases.append((data, parity))
            data = base_data * (i+1)
            parity = base_parity * (i+1)
    return cases


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

def create_allocation_upload_file(data, parity, lock=10):
    appended_data =[]
    allocationId = create_allocation(data, parity, lock=lock)
    

    files = os.listdir()
    files = [file for file in files if file.startswith("dummy")]

    for i in range(1,len(files)+1):
        filename, size_in_bytes = generate_random_file(i-1)
        start = time.time()

        logging.info(f"Using File Generated {filename} of size {size_in_bytes} bytes  started at : {start}")
        try:
            logging.info(f"Uploading file {filename} of size {size_in_bytes} bytes")
            upload_file(allocationId, filename, filename)
            end = time.time()
            logger.info(f"Time when file upload completed:  {end}")
            logger.info(f"Time taken to write file:  {end - start}")

            row = {
                "Data": data,
                "Parity": parity,
                "File Size": float(size_in_bytes/ (1024 ** 2)),
                "Time": str(float(end - start)) + "seconds",
                # "Allocation": allocationId,
            }
            appended_data.append(row)
        except Exception as e:
            logging.error(f"Benchmarking Failed with error: {str(e)}")
            break

    return appended_data

# main method 
def mean_data(res):
    grouped_data = defaultdict(list)

    for record in res:
        keys = (record['Data'], record['Parity'], record['File Size'])  # Extract keys as a tuple
        seconds_str = record['Time'].replace('seconds', '').strip()  # Remove 'seconds' and strip spaces
        seconds = float(seconds_str)   # Convert to float
        grouped_data[keys].append(seconds)

    # calculate mean
    mean_results = {}
    for keys, times in grouped_data.items():
        mean_time = statistics.mean(times)
        mean_results[keys] = mean_time

    result_list = [{'Data':key[0], 'Parity':key[1], 'File Size': key[2],  'Mean Time Taken': str(value) + 'seconds'} for key, value in mean_results.items()]
    return result_list



def draw_plot(data, parity):
    df = pd.read_csv(f"benchmark{data}-{parity}.csv")
    print(df.head())

    fig, ax = plt.subplots(figsize=(30, 20))

    groups = df.groupby(['Data', 'Parity', 'File Size'])
    for key, group in groups:
        label = f"({key[0]}, {key[1]}, {key[2]})"
        ax.plot(group.index, group['Mean Time Taken'], marker='o', linestyle='-', label=label)

    ax.set_xlabel('Configuration combination of data, parity and size')
    ax.set_ylabel('Time Taken In seconds')
    ax.set_title('Time Taken for Different Configurations')

    plt.xticks(ticks=range(len(groups)), labels=[f"({key[0]}, {key[1]}, {key[2]})" for key, _ in groups], rotation=45, ha='right')


    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5) )
    # plt.tight_layout()
    plt.savefig(f'images/plot{data}-{parity}.png', dpi=100)  



if __name__ == "__main__":
    # get value from terminal
    lock = 10
    try:
        data = int(sys.argv[1])
        parity = int(sys.argv[2])
        lock= int(sys.argv[3])
        repeat = int(sys.argv[4])
        try:
            max = sys.argv[5]
        except Exception as e:
            max = None

        if data < 1 or parity < 1:
            raise Exception("Data and Parity should be greater than 1")
        # if data and parity is greater than 10  range should start from 10 onwards similarly if > 20 then 20 onwards
        min = data-2

    except Exception as e:
        print("Please provide data , parity, used for data parity exapnsion lock, repeat as command line arguments")
        print("Example: python3 main.py 2 2 10 1")
        exit(1)
    
    if max:
        cases = generate_data_parity(data, parity, max_blobbers=int(max))
    else:
        cases=generate_data_parity(data, parity )

    cases= cases * repeat
    cases.sort()
    total_result=   []
    quit=False
    for case in cases:
        try:
            result = create_allocation_upload_file(data=case[0], parity=case[1], lock=lock)
            total_result.extend(result)
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            # quit other execution
            quit=True
            break

    # calculate for mean
    if quit is False:
        final_result = mean_data(total_result)

        sorted_result = sorted(final_result, key=lambda x: (x['Data'], x['Parity'], x['File Size']))
        with open(f"benchmark{data}-{parity}.csv", "w") as file:
            writer = csv.DictWriter(file, fieldnames=["Data", "Parity", "File Size", "Mean Time Taken"])
            writer.writeheader()
            writer.writerows(sorted_result)

        # call draw plot
        draw_plot(data,parity=parity)
