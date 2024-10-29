# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the datasets.
songs_df = pd.read_csv('./data/songs.csv')
tcc_ceds_music_df = pd.read_csv('./data/tcc_ceds_music.csv')


def main():
    # 1. Check for Missing Values in each column.
    print("Missing values in songs.csv:")
    print(songs_df.isnull().sum())

    print("\nMissing values in tcc_ceds_music.csv:")
    print(tcc_ceds_music_df.isnull().sum())

    # 2. Check for Duplicates.
    duplicate_songs = tcc_ceds_music_df.duplicated(
        subset=['track_name', 'artist_name']).sum()
    print(f"Duplicate song-artist pairs: {duplicate_songs}")

    # 3. Display Summary Statistics. Just to identify outliers - extremly high or low values.
    # And to see the difference between the two datasets.
    print("\nSummary statistics for songs.csv:")
    print(songs_df.describe())

    print("\nSummary statistics for tcc_ceds_music.csv:")
    print(tcc_ceds_music_df.describe())

    # 4. Visualize Feature Distributions.
    plt.figure(figsize=(15, 10))  # width and height in inches.

    # Songs.csv Key Features.
    # Normalize the ranges to 0 and 1.
    songs_df['bpm'] = songs_df['bpm'] / 100
    plt.subplot(2, 3, 1)
    songs_df['bpm'].plot(kind='hist', bins=30, color='skyblue',
                         edgecolor='black', title='BPM Distribution')

    plt.subplot(2, 3, 2)
    songs_df['dnce'] = songs_df['dnce'] / 100
    songs_df['dnce'].plot(kind='hist', bins=30, color='orange',
                          edgecolor='black', title='Danceability Distribution')

    songs_df['val'] = songs_df['val'] / 100
    plt.subplot(2, 3, 3)
    songs_df['val'].plot(kind='hist', bins=30, color='green',
                         edgecolor='black', title='Valence Distribution')

    # TCC CEDS Music Key Features.
    plt.subplot(2, 3, 4)
    tcc_ceds_music_df['danceability'].plot(
        kind='hist', bins=30, color='purple', edgecolor='black', title='Danceability (TCC CEDS)')

    plt.subplot(2, 3, 5)
    tcc_ceds_music_df['energy'].plot(
        kind='hist', bins=30, color='red', edgecolor='black', title='Energy Distribution (TCC CEDS)')

    plt.subplot(2, 3, 6)
    tcc_ceds_music_df['acousticness'].plot(
        kind='hist', bins=30, color='teal', edgecolor='black', title='Acousticness Distribution (TCC CEDS)')

    plt.tight_layout()
    plt.show()

    # 5. Correlation Analysis
    # Calculate the correlation matrix for both datasets
    songs_correlation = songs_df[[
        'bpm', 'nrgy', 'dnce', 'dB', 'val', 'acous', 'spch', 'pop']].corr()
    tcc_ceds_music_correlation = tcc_ceds_music_df[[
        'danceability', 'loudness', 'acousticness', 'instrumentalness', 'valence', 'energy', 'sadness', 'feelings', 'romantic']].corr()

    # Plot the correlation heatmaps.
    plt.figure(figsize=(16, 6))

    plt.subplot(1, 2, 1)
    sns.heatmap(songs_correlation, annot=True, cmap='coolwarm')
    plt.title('Correlation Matrix for Songs.csv')

    plt.subplot(1, 2, 2)
    sns.heatmap(tcc_ceds_music_correlation, annot=True, cmap='coolwarm')
    plt.title('Correlation Matrix for TCC CEDS Music.csv')

    plt.tight_layout()
    plt.show()

    # 6. Genre Analysis: Visualize the Distribution of Genres.
    plt.figure(figsize=(12, 6))
    tcc_ceds_music_df['genre'].value_counts().plot(
        kind='bar', color='royalblue', edgecolor='black')
    plt.title('Distribution of Genres in TCC CEDS Music Dataset')
    plt.xlabel('Genre')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.show()

    # 7. Scatter Plot for Key Relationships.
    # Relationship between Energy and Danceability in tcc_ceds_music.csv.
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=tcc_ceds_music_df, x='energy', y='danceability', hue='energy',
                    palette='viridis', alpha=0.6, legend=None)
    plt.title('Energy vs Danceability')
    plt.xlabel('Energy')
    plt.ylabel('Danceability')
    plt.show()


if __name__ == '__main__':
    main()
