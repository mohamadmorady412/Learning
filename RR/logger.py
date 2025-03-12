import subprocess
import psutil
import time
import logging

def monitor_process(pid):
    """Monitors the given process and logs its CPU and memory usage."""
    logger = logging.getLogger(__name__)
    try:
        process = psutil.Process(pid)
        while process.is_running():
            cpu_percent = process.cpu_percent(interval=1)
            memory_usage_bytes = process.memory_info().rss
            logger.info(f"CPU: {cpu_percent}%, Memory: {memory_usage_bytes} bytes")
            time.sleep(1)  # Log every second

    except psutil.NoSuchProcess:
        logger.error(f"Process with PID {pid} not found.")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")

if __name__ == "__main__":
    logging.basicConfig(
        filename="usage.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    try:
        process_to_monitor = subprocess.Popen(["python", "main.py"])
        monitor_process(process_to_monitor.pid)
    except FileNotFoundError:
        logger.error("main.py not found.")
    except KeyboardInterrupt:
        logger.info("Monitoring interrupted by user.")
        process_to_monitor.terminate()
        process_to_monitor.wait()
        logger.info("process terminated")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")