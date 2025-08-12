import logging
from.etl.pipeline import run_pipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    run_pipeline()

if __name__ == "__main__":
    main()

