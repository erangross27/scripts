import asyncio
from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.item.calendar.calendar_view.calendar_view_request_builder import CalendarViewRequestBuilder
from datetime import datetime, timedelta, timezone
import os

async def get_calendar_info():
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

        # Get the user's calendar
        calendar = await client.users.by_user_id(user_id).calendar.get()

        print(f"Calendar Information for user {user_id}:")
        print(f"Name: {calendar.name}")
        print(f"Can Edit: {calendar.can_edit}")
        print(f"Can Share: {calendar.can_share}")
        print(f"Can View Private Items: {calendar.can_view_private_items}")
        print(f"Is Default Calendar: {calendar.is_default_calendar}")
        print(f"Is Removable: {calendar.is_removable}")
        print(f"Color: {calendar.color}")

        # Get events from the calendar (including holidays)
        now = datetime.now(timezone.utc)
        end = now + timedelta(days=365)  # Get events for the next year

        query_params = CalendarViewRequestBuilder.CalendarViewRequestBuilderGetQueryParameters(
            start_date_time=now.isoformat(),
            end_date_time=end.isoformat(),
            select=["subject", "start", "end", "isAllDay"],
            top=100,
            filter="isAllDay eq true",
            orderby=["start/dateTime"]
        )

        request_config = CalendarViewRequestBuilder.CalendarViewRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )

        events = await client.users.by_user_id(user_id).calendar.calendar_view.get(request_configuration=request_config)

        print("\nUpcoming Holidays and All-Day Events:")
        for event in events.value:
            if event.is_all_day:
                start_date = event.start.date_time.split('T')[0] if event.start.date_time else "N/A"
                end_date = event.end.date_time.split('T')[0] if event.end.date_time else "N/A"
                print(f"Subject: {event.subject}")
                print(f"Start: {start_date}")
                print(f"End: {end_date}")
                print("---")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        if hasattr(e, 'error'):
            print(f"Error details: {e.error}")
    finally:
        await credential.close()

async def main():
    await get_calendar_info()

if __name__ == "__main__":
    # Ensure UTF-8 encoding for console output
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    asyncio.run(main())
