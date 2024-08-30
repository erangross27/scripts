"""
This script retrieves calendar events for the authenticated user using Microsoft Graph API.

It uses DeviceCodeCredential for authentication and fetches events for the next 7 days.
The script prints out the subject, start time, and end time for each event found.

Required environment variables:
- MICROSOFT_CLIENT_ID: The client ID for your Microsoft application
- MICROSOFT_TENANT_ID: The tenant ID (defaults to 'common' if not set)

Dependencies:
- asyncio
- os
- logging
- datetime
- msgraph
- azure.identity

The main functionality is implemented in the get_calendar_events() async function,
which authenticates the user, retrieves their calendar events, and prints the details.

Usage:
Run this script directly to fetch and display calendar events for the next 7 days.
"""

import asyncio
import os
import logging
from datetime import datetime, timedelta, timezone
from msgraph import GraphServiceClient
from azure.identity import DeviceCodeCredential
from msgraph.generated.users.users_request_builder import UsersRequestBuilder

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def get_calendar_events():
    try:
        client_id = os.environ.get('MICROSOFT_CLIENT_ID')
        tenant_id = os.environ.get('MICROSOFT_TENANT_ID', 'common')

        # Initialize the DeviceCodeCredential
        credential = DeviceCodeCredential(
            client_id=client_id,
            tenant_id=tenant_id,
            user_prompt=lambda x: print(x)
        )

        # Define the scopes
        scopes = ["https://graph.microsoft.com/.default"]

        # Initialize the Graph client
        client = GraphServiceClient(credentials=credential, scopes=scopes)

        # Get the current user's information
        me = await client.me.get()
        user_id = me.id

        # Calculate the date range for events (next 7 days)
        now = datetime.now(timezone.utc)
        end_date = now + timedelta(days=7)

        # Fetch calendar events
        events = await client.users.by_user_id(user_id).calendar.events.get(
            top=50,  # Limit the number of events
            select=["subject", "start", "end"],
            filter=f"start/dateTime ge '{now.isoformat()}' and end/dateTime le '{end_date.isoformat()}'",
            orderby=["start/dateTime ASC"]
        )

        # Process and print events
        if events.value:
            for event in events.value:
                print(f"Event: {event.subject}")
                print(f"Start: {event.start.date_time}")
                print(f"End: {event.end.date_time}")
                print("---")
        else:
            print("No events found in the specified time range.")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        if hasattr(e, 'error'):
            logger.error(f"Error details: {e.error}")
        raise

async def main():
    try:
        await get_calendar_events()
    except Exception as e:
        logger.exception("An error occurred during execution:")

if __name__ == "__main__":
    asyncio.run(main())
