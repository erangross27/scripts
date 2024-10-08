"""
This script retrieves calendar events from Microsoft Graph API for a user's calendars.

It uses the Microsoft Authentication Library (MSAL) for authentication and the Microsoft Graph SDK
for Python to interact with the Graph API. The script performs the following main tasks:

1. Authenticates the user using MSAL, either by retrieving a token from cache or initiating a device flow.
2. Retrieves the user's calendars.
3. For each calendar, fetches events within a specified time range (next 365 days by default).
4. Displays information about each calendar and its events.

The script requires the following environment variables to be set:
- MICROSOFT_CLIENT_ID: The client ID for the Microsoft application.

Dependencies:
- asyncio
- webbrowser
- msal
- msgraph
- azure.core.credentials

Usage:
Run the script directly to fetch and display calendar events for the authenticated user.
"""

import asyncio
import webbrowser
from msal import PublicClientApplication
from msgraph import GraphServiceClient
from msgraph.generated.users.item.calendars.item.events.events_request_builder import EventsRequestBuilder
from datetime import datetime, timedelta, timezone
import os
import time
from azure.core.credentials import AccessToken

# Custom TokenCredential class to handle access tokens
class TokenCredential:
    def __init__(self, access_token, expires_on):
        self.token = AccessToken(access_token, expires_on)

    def get_token(self, *scopes, **kwargs):
        return self.token

async def get_calendar_events():
    try:
        # Set up the MSAL client
        client_id = os.environ.get('MICROSOFT_CLIENT_ID')
        authority = f"https://login.microsoftonline.com/common"
        scopes = ["https://graph.microsoft.com/.default"]

        app = PublicClientApplication(client_id, authority=authority)

        # Attempt to get a token from the cache
        accounts = app.get_accounts()
        result = None
        if accounts:
            result = app.acquire_token_silent(scopes, account=accounts[0])

        if not result:
            # If no token in cache, open browser for user to sign in
            flow = app.initiate_device_flow(scopes=scopes)
            print(flow['message'])
            webbrowser.open(flow['verification_uri'])

            # Poll for token with increased timeout
            timeout = 300  # 5 minutes
            interval = 5  # Check every 5 seconds
            start_time = time.time()

            while True:
                result = app.acquire_token_by_device_flow(flow, timeout=timeout)
                if 'access_token' in result:
                    break
                if time.time() - start_time > timeout:
                    print("Authentication timed out. Please try again.")
                    return
                time.sleep(interval)

        if "access_token" in result:
            # Create a TokenCredential instance
            credential = TokenCredential(result['access_token'], result['expires_in'])

            # Create the Graph client
            client = GraphServiceClient(credentials=credential)

            # Get the first user's ID
            users = await client.users.get()
            user_id = users.value[0].id

            # Get all calendars for the user
            calendars = await client.users.by_user_id(user_id).calendars.get()

            # Set time range for events (e.g., next 365 days)
            now = datetime.now(timezone.utc)
            end = now + timedelta(days=365)

            # Iterate through each calendar
            for calendar in calendars.value:
                print(f"\nCalendar: {calendar.name}")
                print(f"ID: {calendar.id}")

                # Set up query parameters for events
                query_params = EventsRequestBuilder.EventsRequestBuilderGetQueryParameters(
                    filter=f"start/dateTime ge '{now.isoformat()}' and end/dateTime le '{end.isoformat()}'",
                    orderby=["start/dateTime"],
                    select=["subject", "start", "end", "isAllDay"],
                    top=10
                )

                # Set up request configuration
                request_config = EventsRequestBuilder.EventsRequestBuilderGetRequestConfiguration(
                    query_parameters=query_params
                )

                # Get events for this calendar
                events = await client.users.by_user_id(user_id).calendars.by_calendar_id(calendar.id).events.get(
                    request_configuration=request_config
                )

                # Display events if any are found
                if events.value:
                    print("Events:")
                    for event in events.value:
                        print(f"  Subject: {event.subject}")
                        print(f"  Start: {event.start.date_time}")
                        print(f"  End: {event.end.date_time}")
                        print(f"  All Day: {event.is_all_day}")
                        print("  ---")
                else:
                    print("No events found in the specified time range.")
        else:
            # Handle authentication errors
            print(result.get("error"))
            print(result.get("error_description"))
            print(result.get("correlation_id"))

    except Exception as e:
        # Handle general exceptions
        print(f"An error occurred: {str(e)}")
        if hasattr(e, 'error'):
            print(f"Error details: {e.error}")

async def main():
    # Main function to run the calendar events retrieval
    await get_calendar_events()

if __name__ == "__main__":
    # Run the main function using asyncio
    asyncio.run(main())
