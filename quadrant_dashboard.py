from dotenv import load_dotenv
import dash
from dash import dcc, html, dash_table
import dash.dependencies as dd
import pandas as pd
import psycopg2
import os
from contract_web3 import get_token_balance


# Load environment variables from .env file
load_dotenv()

# Replace with your own PostgreSQL connection information
POSTGRES_HOST =  os.getenv("POSTGRES_HOST") 
POSTGRES_DBNAME = os.getenv("POSTGRES_DBNAME")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_PORT=os.getenv("DB_PORT")


# Establish a connection to the database
conn = psycopg2.connect(
    dbname=POSTGRES_DBNAME,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST
)

#Retrieve nfts for user wallet
def getNftsByWallet(wallet_address):
    # Create a cursor object
    cur = conn.cursor()

    try:
        # Prepare a query
        query = f"SELECT token_uri FROM nfts WHERE recipient_wallet = %s"

        # Execute the query
        cur.execute(query, (wallet_address,))

        # Fetch all rows
        token_uris = cur.fetchall()

        # Convert the result into a flat list
        token_uris = [item[0] for item in token_uris]
        # print('token_uris', token_uris)
    except Exception as e:
        print(f"Error: {e}")
        token_uris = []

    return token_uris




def query_data(table_name):
    # Create a cursor object
    cur = conn.cursor()
    try:
        # Execute a query
        cur.execute(f'SELECT * FROM {table_name}')

        # Fetch data from the cursor
        rows = cur.fetchall()

        # Get the column names from the cursor description
        column_names = [desc[0] for desc in cur.description]

        # Create a pandas DataFrame from the fetched data
        df = pd.DataFrame(rows, columns=column_names)

        # # Check if the table is 'quad_users' and add token balance column
        # if table_name == 'quad_users':
        #     contract_address = "0x7E9B6041a9F845cd4790C97a01ef4dD1aFEC316A"
        #     df['token_balance'] = df['wallet_address'].apply(get_token_balance, args=(contract_address,))

    except Exception as e:
        print(f"Error: {e}")
        df = pd.DataFrame()

    return df
    

# Create a Dash application
app = dash.Dash(__name__)
# Set the page title
app.title = "Quadrant NFT Distribution Dashboard"

# Define the layout
app.layout = html.Div([
    html.H2(
        'Quadrant NFT Distribution Dashboard', 
        style={
            'textAlign': 'center', 
            'color': 'green'
        }
    ),
    html.Div(
        [html.H3('QUAD Token Balance: ', style={'textAlign': 'center', 'color': 'blue','display': 'inline'}),
         html.H3(id='token-balance', style={'textAlign': 'center', 'color': 'blue','display': 'inline'})],
        style={'textAlign': 'center'}
    ),
    html.H4('Users'),
    dash_table.DataTable(
        id='users-table',
        columns=[{"name": i, "id": i} for i in query_data('quad_users').columns] + [{"name": "token_uris", "id": "token_uris"}],
        data=query_data('quad_users').to_dict('records'),
        style_cell={'textAlign': 'left','minWidth': '50px', 'width': '50px'},
        style_header={'textAlign': 'left','fontWeight': 'bold','color': 'blue'},
        style_cell_conditional=[
            {'if': {'column_id': 'token_uris'},
           
            'textOverflow': 'ellipsis',
            'maxWidth': '200px'},
        ],
        #dangerously_allow_html=True, # Add this line

    ),
    html.H4('NFT Distributions'),
    dash_table.DataTable(
        id='nft-table',
        columns=[{"name": i, "id": i} for i in query_data('nfts').columns],
        data=query_data('nfts').to_dict('records'),
        style_cell={'textAlign': 'left'},
        style_header={'textAlign': 'left','fontWeight': 'bold', 'color': 'blue'},
        style_table={'overflowX': 'scroll', 'overflowY': 'scroll', 'maxHeight': '500px', 'maxWidth': '100%'},
        page_action='native',
        page_current=0,
        page_size=10,

    ),
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # 10,000 milliseconds = 5 seconds
        n_intervals=0
    )
])

@app.callback(
    [dd.Output('users-table', 'data'), 
     dd.Output('nft-table', 'data'),
     dd.Output('token-balance', 'children')],
    [dd.Input('interval-component', 'n_intervals')]
)

def update_tables(n):
    users_df = query_data('quad_users')
    #print(users_df.head())

    # New: Apply the getNftsByWallet function to the wallet_address column in users_df
    users_df['token_uris'] = users_df['wallet_address'].apply(getNftsByWallet)
    # Convert token_uris list to string
    users_df['token_uris'] = users_df['token_uris'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
    



    nft_df = query_data('nfts')

    contract_owner_addr = os.getenv("contract_owner_addr")  
    contract_address = os.getenv("contract_address")  
    balance = get_token_balance(contract_owner_addr, contract_address)

    return users_df.to_dict('records'), nft_df.to_dict('records'), str(balance)


# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')