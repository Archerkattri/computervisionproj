import pandas as pd
import sys

def search_csv(file_path, search_label):
    df = pd.read_csv(file_path)
    print("DataFrame contents:")
    print(df)

    # Debug: Print all labels
    print("Available labels:", df['label'].tolist())

    matches = df[df['label'].str.lower() == search_label.lower()]

    if matches.empty:
        print(f"No matches found for '{search_label}'")
        return None
    else:
        print(f"Matches found for '{search_label}':")
        results = []
        for index, row in matches.iterrows():
            results.append(row['box'])  # Collect box data
            print(f"Box: {row['box']}")
        return results  # Return list of boxes


if __name__ == "__main__":
    # Get file path and search label from command line arguments
    if len(sys.argv) != 3:
        print("Usage: python search_csv.py <file_path> <search_label>")
        sys.exit(1)

    file_path = sys.argv[1]
    search_label = sys.argv[2]

    # Search the CSV file
    boxes = search_csv(file_path, search_label)

    # If boxes found, print them
    if boxes:
        print("Bounding boxes:", boxes)
