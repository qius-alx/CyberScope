# src/osint/core/concurrency.py
import concurrent.futures
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from osint.core.config import settings
from osint.core.logger import logger

def run_concurrently(fn, items, task_description="Processing..."):
    """
    Runs a function concurrently on a list of items with a progress bar.

    Args:
        fn: The function to execute. It must accept one argument from the items list.
        items: A list of items to be processed by the function.
        task_description: A description for the progress bar.

    Returns:
        A list of non-None results from the function executions.
    """
    results = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        transient=True,
    ) as progress:
        task = progress.add_task(description=task_description, total=len(items))

        with concurrent.futures.ThreadPoolExecutor(max_workers=settings.threads) as executor:
            future_to_item = {executor.submit(fn, item): item for item in items}

            for future in concurrent.futures.as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as exc:
                    # Log the exception for the specific item
                    logger.debug(f'Task for "{item}" generated an exception: {exc}')
                finally:
                    progress.update(task, advance=1)

    return results
