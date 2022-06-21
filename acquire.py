import requests
import pandas as pd
import os

def get_items(resource):
    """Returns a list of dfs for each page that the api has
    for a particular resource.
    
    resource = either 'items', 'stores', or 'sales'
    
    returns a list of dfs
    """

    # create empty list to store each page of data
    dfs = []
    base_url = 'https://python.zgulde.net/'

    # just wanting to get max page to set the loop up for the 
    # correct number of iterations
    response = requests.get(f'https://python.zgulde.net/api/v1/{resource}')
    max_pages = response.json()['payload']['max_page']
    
    # loop for the amount of pages available
    for x in range(1, max_pages+1):
        
        # just easier to read when making the endpoint url
        page=x
        
        # create a generic url_endpoint that can be used with page
        # number and resource type
        url_endpoint = f'/api/v1/{resource}?page={page}'
        response = requests.get(base_url + url_endpoint)
        
        # show what page we're on, and whether the response was ok
        print(f'page {x}, response ok: {response.ok}')
        
        # append the df to a list of all dfs for this resource, 
        # to be concatenated later.
        dfs.append(pd.DataFrame(response.json()['payload'][resource]))

    # return the list of pages as dfs
    return dfs

def create_df(list_of_dfs):
    """ creates a single df out of list of dfs
    
    list_of_dfs = a list of dfs to be concatenated vertically,
    intended to be the output of the get_items function"""
    
    # instantiate empty df to be concatenated onto
    total_df = pd.DataFrame()
    
    # concatenates each df from list to make a single
    # df
    for df in list_of_dfs:
        total_df = pd.concat([total_df, df])

    # returns single concatenated df
    return total_df


def all_resource_dfs(list_of_resources):
    """Uses a list of resources to request information to turn
    into dataframes. A dictionary is made to hold the resulting 
    dfs, using the name of the resource as the key
    
    list_of_resources = list of resources to be acquired from this 
    specific api.
    """

    # empty dict to hold all total dfs for every resource in
    # the input list
    all_dfs = {}

    # gets list of dfs for each resource, then makes a total
    # df for each resource. Entered into the dictionary
    # using the resource name as key and the total df for that
    # resource as the value.
    for resource in list_of_resources:
        resource_dfs = get_items(resource)
        all_dfs[resource] = (create_df(resource_dfs))
        
    # returns total df for each resource
    return all_dfs

def resource_dfs_to_csv(resource_df_dict):
    """
    Writes all dfs in the resource_df_dict to csv,
    using the key of the entry as the file name.

    resource_df_dict = dict holding different resources as keys
    and the total df for that resource as a value.
    """
    for key, value in resource_df_dict.items():
        value.to_csv(f'{key}.csv')

    sales = resource_df_dict['sales']
    stores = resource_df_dict['stores']
    items = resource_df_dict['items']

    total = sales.merge(right=items, how='left', left_on='item', right_on='item_id' )
    total = sales.merge(right=stores, how='left', left_on='store', right_on='store_id')

    total.to_csv('total_df.csv')

    return total


def ignore_first(df):
    '''Ignores first 'Unnamed: 0' column when reading csv'''
    return df[df.columns[1:]]
        
def load_all_data():
    """return all three csvs
    returns sales, stores, items"""
    sales = ignore_first(pd.read_csv('sales.csv'))
    stores = ignore_first(pd.read_csv('stores.csv'))
    items = ignore_first(pd.read_csv('items.csv'))

    return sales, stores, items

def acquire_open_power_systems_data():
    """ uses url to grab csv for open power systems if csv
    does not already exist"""
    filename = 'open_pwr_sys_data.csv'

    if os.path.isfile(filename):
        return ignore_first(pd.read_csv(filename))
    else:
        url = 'https://raw.githubusercontent.com/jenfly/opsd/master/opsd_germany_daily.csv'
        data = pd.read_csv(url)
        data.to_csv(filename)
    
        return data

def acquire_sales_stores_items_data():
    # list of all resources to make dfs out of 
    list_of_resources = ['items', 'stores', 'sales']
    filename = 'total_df.csv'

    if os.path.isfile(filename):
        return ignore_first(pd.read_csv(filename))
    else:
        # create resource_dict to then be written to csv
        resource_dict = all_resource_dfs(list_of_resources)
        return resource_dfs_to_csv(resource_dict)
    

    

    
