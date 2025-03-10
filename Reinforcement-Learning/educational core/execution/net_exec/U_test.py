import asyncio
import logging
import json
import subprocess
import urllib.request
import urllib.error
import ssl
import hashlib
import shelve

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CommandCache:
    def __init__(self, filename="command_cache.db"):
        self.filename = filename

    def get(self, key):
        with shelve.open(self.filename) as cache:
            return cache.get(key, None)

    def set(self, key, value):
        with shelve.open(self.filename) as cache:
            cache[key] = value

cache = CommandCache()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def load_config(filepath="config.json"):
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"Config file {filepath} not found.")
        return {}
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in config file {filepath}.")
        return {}
async def run_ssh_command(host, username, command, timeout=10):
    cache_key = f"ssh-{host}-{username}-{command}-{timeout}"
    cached_result = cache.get(cache_key)
    if cached_result:
        logging.info(f"Cache hit for SSH command on {host}")
        return cached_result

    async def ssh_task():
        try:
            ssh_command = f"ssh -o StrictHostKeyChecking=no {username}@{host} '{command}'"
            result = await asyncio.to_thread(subprocess.run, ssh_command, shell=True, capture_output=True, text=True, timeout=timeout)
            output = result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            logging.error(f"SSH timeout on {host}")
            output = f"Error: Timeout on {host}"
        except Exception as e:
            logging.error(f"SSH error on {host}: {e}")
            output = f"Error: {e}"
        
        cache.set(cache_key, output)
        return output

    return await ssh_task()

async def run_rest_command(url, payload, timeout=10):
    cache_key = f"rest-{url}-{json.dumps(payload, sort_keys=True)}-{timeout}"
    cached_result = cache.get(cache_key)
    if cached_result:
        logging.info(f"Cache hit for REST API call to {url}")
        return cached_result

    try:
        data = json.dumps(payload).encode('utf-8')
        request = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
        context = ssl.create_default_context()
        
        async def fetch():
            with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
                result = response.read().decode()
                logging.info(f"REST API call to {url} successful")
                cache.set(cache_key, result)
                return result
        
        return await asyncio.to_thread(fetch)
    except urllib.error.URLError as e:
        logging.error(f"REST API error on {url}: {e}")
        return f"Error: {e}"
    except Exception as e:
        logging.error(f"Unexpected error on {url}: {e}")
        return f"Error: {e}"

async def main():
    config = load_config()
    if not config:
        return

    tasks = []

    ssh_targets = config.get("ssh_targets", [])
    for target in ssh_targets:
        tasks.append(run_ssh_command(target['host'], target['username'], target['command'], target.get('timeout', 10)))

    rest_targets = config.get("rest_targets", [])
    for target in rest_targets:
        tasks.append(run_rest_command(target['url'], target['payload'], target.get('timeout', 10)))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            logging.error(f"Task failed: {result}")
        else:
            logging.info(f"Result: {result}")
            print(result)

if __name__ == "__main__":
    asyncio.run(main())
