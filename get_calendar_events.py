import asyncio
from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.item.calendars.item.events.events_request_builder import EventsRequestBuilder
from datetime import datetime, timedelta, timezone
import os

async def get_calendar_events():
    try:
        credential = ClientSecretCredential(
            tenant_id=os.environ.get('MICROSOFT_TENANT_ID'),
            client_id=os.environ.get('MICROSOFT_CLIENT_ID'),
            client_secret=os.environ.get('MICROSOFT_CLIENT_SECRET')
        )
        scopes = ["https://graph.microsoft.com/.default"]
        client = GraphServiceClient(credentials=credential, scopes=scopes)

        # Get the first user's ID
        users = await client.users.get()
        user_id = users.value[0].id

        # Get all calendars for the user
        calendars = await client.users.by_user_id(user_id).calendars.get()

        # Set time range for events (e.g., next 30 days)
        now = datetime.now(timezone.utc)
        end = now + timedelta(days=365)

        for calendar in calendars.value:
            print(f"\nCalendar: {calendar.name}")
            print(f"ID: {calendar.id}")

            # Set up query parameters
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

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        if hasattr(e, 'error'):
            print(f"Error details: {e.error}")
    finally:
        await credential.close()

async def main():
    await get_calendar_events()

if __name__ == "__main__":
    asyncio.run(main())
