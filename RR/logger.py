try:
    import psutil
except ImportError:
    print("psutil is not installed. Please install it by running 'pip install psutil'")
    exit(1)

import subprocess
import time
import logging
import argparse

def parse_args():
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(description="Monitor a process's CPU and memory usage.")
    parser.add_argument("script", help="The Python script to monitor (e.g., main.py)")
    parser.add_argument("--logfile", default="usage.log", help="Log file to store the results (default: usage.log)")
    parser.add_argument("--interval", type=int, default=1, help="Interval in seconds between measurements (default: 1s)")
    return parser.parse_args()

def monitor_process(pid, interval):
    """Monitors the given process and logs its CPU and memory usage."""
    logger = logging.getLogger(__name__)
    try:
        process = psutil.Process(pid)
        while process.is_running():
            cpu_percent = process.cpu_percent(interval=interval)
            memory_usage_bytes = process.memory_info().rss
            logger.info(f"CPU: {cpu_percent}%, Memory: {memory_usage_bytes} bytes")
            time.sleep(interval)  # Log every `interval` seconds

    except psutil.NoSuchProcess:
        logger.error(f"Process with PID {pid} not found.")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")

def start_process(command):
    try:
        return subprocess.Popen(command)
    except Exception as e:
        logger.exception(f"An error occurred while starting the process: {e}")
        return None

if __name__ == "__main__":
    args = parse_args()

    # Setup logging
    logging.basicConfig(
        filename=args.logfile,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    try:
        process_to_monitor = start_process(["python", args.script])
        if process_to_monitor:
            monitor_process(process_to_monitor.pid, args.interval)
    except FileNotFoundError:
        logger.error(f"{args.script} not found.")
    except KeyboardInterrupt:
        logger.info("Monitoring interrupted by user.")
        process_to_monitor.terminate()
        process_to_monitor.wait()
        logger.info("Process terminated.")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
