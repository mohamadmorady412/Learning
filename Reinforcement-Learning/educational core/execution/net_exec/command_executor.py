import asyncio
import logging
import subprocess
import urllib.request
import urllib.error
import ssl
import json
from cache_manager import cache

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
