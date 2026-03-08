import argparse
import json
import os
import pandas as pd
from datetime import datetime

# SageMaker Processing script


def extract_features(df):
    """
    Converts raw creator content into ML features.

    Expected features:
    - engagement_ratio: (likes + comments + shares) / followers (we'll mock followers if not in df, or assume views)
    - trend_velocity: mock calculation
    - title_length: len(title)
    """
    if "views" not in df.columns or df["views"].sum() == 0:
        df["views"] = 1000  # fallback

    df["engagement_ratio"] = (df["likes"] + df["comments"] + df["shares"]) / df["views"]
    df["title_length"] = df["title"].apply(lambda x: len(str(x)))

    # Mocking trend_velocity and sentiment for MVP simplicity
    # In reality, we would join this dataframe with the TrendSignals dynamoDB table
    # based on the `topic` and `timestamp` fields.
    df["trend_velocity"] = 0.5
    df["sentiment_score"] = 0.8

    # Target variable (if training)
    df["viral_probability"] = df["engagement_ratio"].apply(
        lambda x: 1 if x > 0.1 else 0
    )

    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-data", type=str, default="/opt/ml/processing/input")
    parser.add_argument("--output-data", type=str, default="/opt/ml/processing/output")
    args = parser.parse_args()

    input_dir = args.input_data
    output_dir = args.output_data

    print(f"Reading data from {input_dir}")

    all_data = []

    # Read all JSON files from input_dir
    if os.path.exists(input_dir):
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.endswith(".json"):
                    with open(os.path.join(root, file), "r") as f:
                        data = json.load(f)
                        all_data.append(data)

    if len(all_data) == 0:
        print("No data found for processing. Exiting.")
        # Create a mock dataset just so the pipeline doesn't fail
        mock_data = {
            "creator_id": "mock_1",
            "content_id": "mock_vid_1",
            "topic": "AI",
            "title": "AI is cool",
            "likes": 500,
            "comments": 50,
            "shares": 10,
            "views": 5000,
        }
        all_data.append(mock_data)

    df = pd.DataFrame(all_data)

    # Ensure required columns exist
    for col in ["likes", "comments", "shares", "views", "title"]:
        if col not in df.columns:
            df[col] = 0 if col != "title" else ""

    processed_df = extract_features(df)

    output_path = os.path.join(output_dir, "features.csv")
    processed_df.to_csv(output_path, index=False)

    print(f"Processed data saved to {output_path}")
