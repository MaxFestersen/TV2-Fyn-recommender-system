from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
import time

n_tests = range(100)

def run_session(test):
    driver = webdriver.Firefox()
    driver.get("http://localhost:8080")
    assert "Forside | TV2 Fyn" in driver.title
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(0.5)
    driver.close()

with ThreadPoolExecutor(max_workers=3) as executor:
    executor.map(run_session, n_tests)