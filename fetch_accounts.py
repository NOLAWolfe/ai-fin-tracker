import os

from dotenv import load_dotenv
from plaid import ApiClient, Configuration, Environment
from plaid.api import plaid_api
# Import the explicit Model objects needed for Plaid's new SDK style
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.sandbox_public_token_create_request_options import SandboxPublicTokenCreateRequestOptions
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

# 1. Load Environment Variables
load_dotenv()

# --- Plaid Initialization ---
# The client must be configured with a Configuration object
configuration=Configuration(
    host=Environment.Sandbox,
    api_key={
        'clientId': os.getenv('PLAID_CLIENT_ID'),
        'secret': os.getenv('PLAID_SECRET'),
        'plaidVersion':'2020-09-14'
    }
)

# Use the configuration to create the API client and a specific Plaid API instance
api_client = ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

# --- Define Constants ---
INSTITUTION_ID = os.getenv('PLAID_INSTITUTION_ID')
ACCESS_TOKEN = None
PRODUCTS = [p.strip() for p in os.getenv('PLAID_PRODUCTS').split(',')]
# --- Core Functionality ---

def create_link_token():
  try:
    pt_request = SandboxPublicTokenCreateRequest(
      institution_id=INSTITUTION_ID,
      initial_products=[Products('transactions')]
    )
    pt_response = client.sandbox_public_token_create(pt_request)
    # The generated public_token can now be
    # exchanged for an access_token
    exchange_request = ItemPublicTokenExchangeRequest(
        public_token=pt_response['public_token'],
    )
    
    # print(f'  -> Public Token Created: {public_token}')
    exchange_response = client.item_public_token_exchange(exchange_request)
    
    exchange_token = exchange_response['access_token']
    print(f"  -> Exchange Token Created: {exchange_token}")
  except Exception as e:
        print(f"Error Generating token: {e}")
        return None

def fetch_and_display_accounts(access_token):
    """
    Step 3: Use the permanent access_token to fetch and display account balances.
    """
    if not access_token:
        print("\nCannot fetch accounts: Access Token is missing.")
        return

    print("\n3. Fetching Accounts and Balances...")
    
    # 3a. Request to get accounts
    accounts_request = AccountsGetRequest(access_token=access_token)
    
    try:
        accounts_response = client.accounts_get(accounts_request)
        accounts = accounts_response['accounts']

        print(f"\n✅ SUCCESS: Found {len(accounts)} accounts:")
        print("---------------------------------------------")
        
        for account in accounts:
            balance = account['balances']['available'] if account['balances']['available'] else account['balances']['current']
            print(f"  Account Name: {account['name']} ({account['subtype'].capitalize()})")
            print(f"  Balance:      ${balance:,.2f}")
            print("---")
            
    except Exception as e:
        print(f"Error fetching accounts: {e}")


if __name__ == '__main__':
    # Execute the three steps in order
    token = create_link_token()
    # fetch_and_display_accounts(token)
