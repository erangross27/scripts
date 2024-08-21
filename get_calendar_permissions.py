import asyncio
from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient
import os

async def get_calendars_and_permissions():
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

        for calendar in calendars.value:
            print(f"\nCalendar: {calendar.name}")
            print(f"ID: {calendar.id}")

            # Get permissions for this calendar
            permissions = await client.users.by_user_id(user_id).calendars.by_calendar_id(calendar.id).calendar_permissions.get()

            if permissions.value:
                print("Permissions:")
                for permission in permissions.value:
                    print(f"  ID: {permission.id}")
                    if hasattr(permission, 'email_address') and permission.email_address:
                        print(f"  Email: {permission.email_address.address}")
                    print(f"  Role: {permission.role}")
                    print("  ---")
            else:
                print("No specific permissions found for this calendar.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        if hasattr(e, 'error'):
            print(f"Error details: {e.error}")
    finally:
        await credential.close()

async def main():
    await get_calendars_and_permissions()

if __name__ == "__main__":
    asyncio.run(main())
