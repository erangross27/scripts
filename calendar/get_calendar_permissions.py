"""
This script retrieves calendars and their permissions for a user using the Microsoft Graph API.

It uses Azure AD authentication with a ClientSecretCredential to access the Graph API.
The script performs the following operations:
1. Authenticates with Azure AD using environment variables for tenant ID, client ID, and client secret.
2. Retrieves the first user from the list of users in the Azure AD tenant.
3. Fetches all calendars for the retrieved user.
4. For each calendar, it prints the calendar name and ID.
5. Retrieves and prints the permissions for each calendar, including the permission ID, email address (if available), and role.

The script uses asynchronous programming with asyncio for efficient API interactions.

Requirements:
- Azure AD application with appropriate permissions
- Environment variables set for MICROSOFT_TENANT_ID, MICROSOFT_CLIENT_ID, and MICROSOFT_CLIENT_SECRET
- Python packages: azure-identity, msgraph-sdk

Usage:
Run the script directly to execute the calendar and permission retrieval process.

Note: Exception handling is implemented to catch and print any errors that occur during execution.
"""

import asyncio
from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient
import os

async def get_calendars_and_permissions():
    try:
        # Initialize the ClientSecretCredential with Azure AD credentials
        credential = ClientSecretCredential(
            tenant_id=os.environ.get('MICROSOFT_TENANT_ID'),
            client_id=os.environ.get('MICROSOFT_CLIENT_ID'),
            client_secret=os.environ.get('MICROSOFT_CLIENT_SECRET')
        )
        # Define the scope for Microsoft Graph API
        scopes = ["https://graph.microsoft.com/.default"]
        # Create a GraphServiceClient instance
        client = GraphServiceClient(credentials=credential, scopes=scopes)

        # Retrieve the first user's ID from the list of users
        users = await client.users.get()
        user_id = users.value[0].id

        # Get all calendars for the user
        calendars = await client.users.by_user_id(user_id).calendars.get()

        # Iterate through each calendar
        for calendar in calendars.value:
            print(f"\nCalendar: {calendar.name}")
            print(f"ID: {calendar.id}")

            # Get permissions for the current calendar
            permissions = await client.users.by_user_id(user_id).calendars.by_calendar_id(calendar.id).calendar_permissions.get()

            # Check if there are any permissions for the calendar
            if permissions.value:
                print("Permissions:")
                # Iterate through each permission
                for permission in permissions.value:
                    print(f"  ID: {permission.id}")
                    # Check if email address is available and print it
                    if hasattr(permission, 'email_address') and permission.email_address:
                        print(f"  Email: {permission.email_address.address}")
                    print(f"  Role: {permission.role}")
                    print("  ---")
            else:
                print("No specific permissions found for this calendar.")

    except Exception as e:
        # Handle any exceptions that occur during execution
        print(f"An error occurred: {str(e)}")
        if hasattr(e, 'error'):
            print(f"Error details: {e.error}")
    finally:
        # Ensure the credential is closed after use
        await credential.close()

async def main():
    # Call the function to get calendars and permissions
    await get_calendars_and_permissions()

if __name__ == "__main__":
    # Run the main function asynchronously
    asyncio.run(main())
