from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Replace with your YouTube API key
api_key = "AIzaSyBd8oa2qjhZZrDSg9TXHTmCj-ek_gd9Ce0"

try:
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Search for videos related to the Ukraine-Russia war
    search_response = youtube.search().list(
        q="Ukraine Russia war",
        part="id",
        type="video",
        maxResults=5
    ).execute()

    # Get video IDs from search results
    video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]

    # Fetch comments from the videos
    comments = []
    for video_id in video_ids:
        try:
            response = youtube.commentThreads().list(
                videoId=video_id,
                part="snippet",
                maxResults=10
            ).execute()

            for item in response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet'].get('textDisplay')
                if comment:
                    comments.append(comment)
        except HttpError as e:
            print(f"An error occurred: {e}")
            continue

    # Display the comments
    print("Fetched Comments:")
    for comment in comments:
        print(comment)

except HttpError as e:
    print(f"An error occurred while connecting to YouTube: {e}")