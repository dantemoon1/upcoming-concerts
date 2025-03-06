import os
from dotenv import load_dotenv
import requests
from datetime import datetime
import time

# Load environment variables
load_dotenv()

artists = ['Rebecca Black', "Nessa Barrett", "Taylor Swift"]

def parse_event(event):
    """Extract relevant information from a single event"""
    try:
        venue = event['_embedded']['venues'][0]
        
        artists = []
        if '_embedded' in event and 'attractions' in event['_embedded']:
            artists = [attr['name'] for attr in event['_embedded']['attractions']]
        
        return {
            'name': event['name'],
            'artists': artists,  #can be a list of artists
            'date': event['dates']['start']['localDate'],
            'time': event['dates']['start']['localTime'],
            'venue': venue['name'],
            'city': venue['city']['name'],
            'state': venue['state']['stateCode'],
            'ticket_url': event['url'],
            'status': event['dates']['status']['code']
        }
    except KeyError as e:
        print(f"Warning: Missing data in event: {e}")
        return None

def get_events(response):
    """Parse the API response and return list of events"""
    data = response.json()
    
    # Check if we have any events
    if '_embedded' not in data or 'events' not in data['_embedded']:
        return []
    
    events = []
    for event in data['_embedded']['events']:
        parsed_event = parse_event(event)
        if parsed_event:  # Only add if parsing was successful
            events.append(parsed_event)
    
    # Sort by date
    events.sort(key=lambda x: x['date'])
    return events

def get_artist_events(artist, api_key, dma_id=324):
    """Get events for a specific artist"""
    base_url = "https://app.ticketmaster.com/discovery/v2/events.json"
    
    #fix for spaces in artist name
    artist_query = artist.replace(" ", "+")
    
    url = f"{base_url}?size=5&keyword={artist_query}&dmaId={dma_id}&apikey={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return get_events(response)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching events for {artist}: {e}")
        return []

# Use environment variable for API key
API_KEY = os.getenv('TICKETMASTER_API_KEY')

# Add error handling for missing API key
if not API_KEY:
    raise ValueError("Missing TICKETMASTER_API_KEY environment variable")

# Get events for all artists
all_events = []
for artist in artists:
    print(f"\nSearching for events by {artist}...")
    artist_events = get_artist_events(artist, API_KEY)
    all_events.extend(artist_events)
    time.sleep(0.5)  # Add a 0.5 second delay between requests

# Sort all events by date
all_events.sort(key=lambda x: x['date'])

# Print results
if not all_events:
    print("\nNo events found for any artist")
else:
    print(f"\nFound {len(all_events)} total events:")
    for event in all_events:
        print(f"\nEvent: {event['name']}")
        if event['artists']:
            print(f"Artists: {', '.join(event['artists'])}")
        print(f"Date: {event['date']} at {event['time']}")
        print(f"Venue: {event['venue']} in {event['city']}, {event['state']}")
        print(f"Status: {event['status']}")
        print(f"Tickets: {event['ticket_url']}")
        print("-" * 50)