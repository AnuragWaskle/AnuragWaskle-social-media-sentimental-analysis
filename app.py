from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from flask_cors import CORS
from textblob import TextBlob
import sys
import codecs
import requests

# Force UTF-8 encoding for stdout and stderr
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Replace with your YouTube API key
youtube_api_key = "AIzaSyBRW9BZNG3Wo92OSux-YUpFDjUtdPzPJvs"

# Your Gemini API key
gemini_api_key = "AIzaSyBqR-ysQdHSH5R75O4ulhSBCYOl63KYaPs"

# Replace this with the actual Gemini API endpoint
gemini_api_url = "https://gemini-api-url.com/summarize"  # Replace with real Gemini API URL

@app.route('/analyze', methods=['POST'])
def analyze_sentiment():
    data = request.json
    search_query = data.get('query')

    if not search_query:
        return jsonify({'error': 'Query parameter is required.'}), 400

    try:
        youtube = build('youtube', 'v3', developerKey=youtube_api_key)

        # Search for videos related to the user-provided query
        search_response = youtube.search().list(
            q=search_query,
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
                        # Append comments after encoding to UTF-8
                        comments.append(comment.encode('utf-8', 'ignore').decode('utf-8'))  
            except HttpError as e:
                error_details = e._get_reason()
                if "commentsDisabled" in error_details:
                    print(f"Comments are disabled for video {video_id}. Skipping this video.")
                else:
                    print(f"An error occurred while fetching comments for video {video_id}: {e}")
                continue

        if not comments:
            return jsonify({'error': 'No comments found for the query.'}), 404

        # Sentiment Analysis
        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for comment in comments:
            analysis = TextBlob(comment)
            polarity = analysis.sentiment.polarity

            if polarity > 0:
                positive_count += 1
            elif polarity < 0:
                negative_count += 1
            else:
                neutral_count += 1

        # Summarize the sentiments
        total_comments = positive_count + negative_count + neutral_count
        sentiment_summary = {
            'total_comments': total_comments,
            'positive': positive_count,
            'negative': negative_count,
            'neutral': neutral_count
        }

        # Impact Summary
        if positive_count > negative_count and positive_count > neutral_count:
            impact_summary = "Overall positive sentiment indicates optimism."
        elif negative_count > positive_count and negative_count > neutral_count:
            impact_summary = "Overall negative sentiment indicates widespread concern."
        else:
            impact_summary = "Mixed or neutral sentiment indicates balanced opinions."

        # Summarizing Comments using Gemini API
        try:
            gemini_response = requests.post(
                gemini_api_url,
                headers={'Authorization': f'Bearer {gemini_api_key}'},
                json={'comments': comments},  # Send comments for summarization
                verify=False  # Bypass SSL verification
            )

            gemini_summary = gemini_response.json().get('summary', 'Could not summarize the comments.')
        except Exception as e:
            print(f"Error connecting to Gemini API: {e}")
            gemini_summary = "Error summarizing the comments."

        return jsonify({
            'comments': comments,
            'sentiment_summary': sentiment_summary,
            'impact_summary': impact_summary,
            'summary': gemini_summary  # Add the summary to the response
        })

    except HttpError as e:
        return jsonify({'error': f'An error occurred while connecting to YouTube: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
