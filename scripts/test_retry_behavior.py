from prefect import flow, task
import random

@task(retries=2, retry_delay_seconds=3)
def flaky_task():
    if random.random() < 0.7:
        raise ValueError("Simulated transient failure")
    return "success"

@flow
def retry_test_flow():
    result = flaky_task()
    print(f"Task result: {result}")

if __name__ == "__main__":
    retry_test_flow()