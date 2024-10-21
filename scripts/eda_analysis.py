# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the datasets.
songs_df = pd.read_csv('.\\data\\songs.csv')
tcc_ceds_music_df = pd.read_csv('.\\data\\tcc_ceds_music.csv')

# 1. Check for Missing Values in each column.
print("Missing values in songs.csv:")
print(songs_df.isnull().sum())

print("\nMissing values in tcc_ceds_music.csv:")
print(tcc_ceds_music_df.isnull().sum())

# 2. Display Summary Statistics. Just to identify outliers - extremely high or low values. 
# And to see the difference between the two datasets.
print("\nSummary statistics for songs.csv:")
print(songs_df.describe())

print("\nSummary statistics for tcc_ceds_music.csv:")
print(tcc_ceds_music_df.describe())

# 3. Visualize Feature Distributions
plt.figure(figsize=(15, 10))  # width and height in inches.

# Songs.csv Key Features
# Normalize the ranges to 0 and 1.
songs_df['bpm'] = songs_df['bpm'] / 100
plt.subplot(2, 3, 1)
songs_df['bpm'].plot(kind='hist', bins=30, color='skyblue', edgecolor='black', title='BPM Distribution')

plt.subplot(2, 3, 2)
songs_df['dnce'] = songs_df['dnce'] / 100
songs_df['dnce'].plot(kind='hist', bins=30, color='orange', edgecolor='black', title='Danceability Distribution')

songs_df['val'] = songs_df['val'] / 100
plt.subplot(2, 3, 3)
songs_df['val'].plot(kind='hist', bins=30, color='green', edgecolor='black', title='Valence Distribution')

# TCC CEDS Music Key Features
plt.subplot(2, 3, 4)
tcc_ceds_music_df['danceability'].plot(kind='hist', bins=30, color='purple', edgecolor='black', title='Danceability (TCC CEDS)')

plt.subplot(2, 3, 5)
tcc_ceds_music_df['energy'].plot(kind='hist', bins=30, color='red', edgecolor='black', title='Energy Distribution (TCC CEDS)')

plt.subplot(2, 3, 6)
tcc_ceds_music_df['acousticness'].plot(kind='hist', bins=30, color='teal', edgecolor='black', title='Acousticness Distribution (TCC CEDS)')

plt.tight_layout()
plt.show()
