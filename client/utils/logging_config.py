import logging

def setup_logging(log_file="app.log"):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            #logging.FileHandler(log_file),  
            logging.StreamHandler() 
        ]
    )