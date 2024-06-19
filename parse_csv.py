import csv
import pandas as pd
import matplotlib.pyplot as plt

def draw_plot(data, parity):
    df = pd.read_csv(f"benchmark{data}-{parity}.csv")
    df = df.drop(columns=['Allocation'])
    df['Mean Time Taken'] = df['Mean Time Taken'].str.replace('seconds', '').astype(float)
    df['Key'] = df.apply(lambda row: f"({row['Data']}, {row['Parity']}, {row['File Size']})", axis=1)
    fig, ax = plt.subplots(figsize=(30, 20))
    ax.plot(df['Key'], df['Mean Time Taken'], marker='o', linestyle='-')
    ax.set_xlabel('Configuration combination of Data, Parity, and File Size')
    ax.set_ylabel('Time Taken in Seconds')
    ax.set_title('Time Taken for Different Configurations')

    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    plt.savefig(f'images/plot{data}-{parity}.png', dpi=100)

draw_plot(10, 10)
