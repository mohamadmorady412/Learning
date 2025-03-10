import asyncio
import logging
from config_manager import load_config
from command_executor import run_ssh_command, run_rest_command


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
