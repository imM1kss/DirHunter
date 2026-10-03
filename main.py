#imports
import asyncio
import aiohttp
import argparse
import sys

async def check_url(session, url, semaphore):
    
    '''Send an HTTP GET request to the URL'''

    async with semaphore:
        try:
            async with session.get(url, timeout=5, ssl=False) as response:
                status = response.status
                # filter the HTTP status codes we need
                if status in [200, 204, 301, 302, 307, 401, 403]:
                    color_code= "\033[92m" if status == 200 else "\033[93m"
                    reset = "\033[0m"
                    print(f"{color_code}[+] {status} | {url}{reset}")
        except asyncio.TimeoutError:
            pass #Ignore timeout errors
        except Exception as e:
            print(f"[-] Ошибка подключения к {url}: {e.__class__.__name__} - {e}")

async def main(url, wordlist_path, threads):
    # limit the count of connections (protection against crashes of our script and server DoS)
    semaphore = asyncio.Semaphore(threads)

    print(f"[*] Launching AioDirHunter. Target: {url}")
    print(f"[*] Threads: {threads}. Reading wordlist: {wordlist_path}...\n")

    try:
        with open(wordlist_path, 'r', encoding='utf-8') as file:
            paths = [line.strip() for line in file if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"[-] Error: File not found '{wordlist_path}'")
        sys.exit(1)

    # Configuring a connector to optimize connections
    connector = aiohttp.TCPConnector(limit=threads)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for path in paths:
            # Form the full URL
            url = f"{url.rstrip('/')}/{path.lstrip('/')}"
            tasks.append(asyncio.create_task(check_url(session, url, semaphore)))
        
        # Launch all tasks
        await asyncio.gather(*tasks)
        print("\n[*] Scanning completed.")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="AioDirHunter - Asynchronous Directory and File Brute Forcer")
    parser.add_argument("-u", "--url", required=True, help="Target URL (e.g., http://example.com)")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to the wordlist file (.txt)")
    parser.add_argument("-t", "--threads", type=int, default=50, help="Number of concurrent requests (default: 50)")

    args = parser.parse_args()

    # Launching the asynchronous event loop
    try:
        asyncio.run(main(args.url, args.wordlist, args.threads))
    except KeyboardInterrupt:
        print("\n[!] Scanning interrupted by user.")
        sys.exit(0)
