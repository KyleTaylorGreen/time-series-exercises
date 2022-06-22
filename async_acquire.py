import acquire
import trio
import asks
import time

# worker function for each url to grab response
# asynchronously.
async def worker(s, url):
    """ fetches html asynchronously 
    s = session created by asks.Session

    url = url to be fetched

    retries = number of attempted retries if the
    connection fails.

    timeout = number of seconds before stopping 
    attempts to connect to url.

    returns json of page if connection is successful.
    """
    try:
        r = await s.get(url[1], retries=10)
        print(url[0])
        return r.json()
    except:
        print('request not handled in time.')
    print(url[0])

# creates session with connection limit, iterates
# through list of urls to to get responses.
async def main(url_list):
    s = asks.Session(connections=200)
    async with trio.open_nursery() as nursery:
        for url in url_list:
            nursery.start_soon(worker,s, url)

# creates list of urls + index and sends them to asynchronous
# main function

def request_all_urls_comparison():
    urls = [[i, url] for i, url in enumerate(acquire.all_urls())]

    #urls = [[i, 'http://serebii.net'] for i in range(150)]
    start = time.perf_counter()
    connections=200
    retries=10
    print('hello')
    trio.run(main, urls)
    
    async_end = time.perf_counter() - start
    
    sync_start = time.perf_counter()
    sequential = acquire.all_resource_dfs(['items', 'sales', 'stores'])
    sync_end = time.perf_counter() - sync_start

    print(f"Async time to complete: {async_end}")
    print(f'synchronous time to end: {sync_end}')


if __name__ == '__main__':
    request_all_urls_comparison()