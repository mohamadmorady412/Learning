import concurrent.futures
import logging

MAX_CONCURRENT_TASKS = 2 # TODO...

def run_task(func, *args, **kwargs):
    logging.info(f"Starting task: {func.__name__} with args={args} kwargs={kwargs}")
    try:
        result = func(*args, **kwargs)
        logging.info(f"Finished task: {func.__name__} with result={result}")
    except Exception as e:
        logging.error(f"Task {func.__name__} failed with error: {e}")
        result = None
    return result

def execute_tasks_parallel(tasks, max_concurrent_tasks=2, use_threads=False):
    executor_class = concurrent.futures.ThreadPoolExecutor if use_threads else concurrent.futures.ProcessPoolExecutor

    with executor_class(max_workers=max_concurrent_tasks) as executor:
        futures = {executor.submit(run_task, func, *args, **kwargs): (func.__name__, args, kwargs)
                   for func, args, kwargs in tasks}
        
        for future in concurrent.futures.as_completed(futures):
            func_name, args, kwargs = futures[future]
            try:
                result = future.result()
                logging.info(f"Task {func_name} with args={args} completed with result={result}")
            except Exception as e:
                logging.error(f"Task {func_name} with args={args} failed with error: {e}")
