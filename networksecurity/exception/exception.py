import sys
from networksecurity.logging import logger

# Custom exception class inheriting from Python's base Exception
class NetworkSecurityException(Exception):
    def __init__(self, error_message, error_details: sys):
        # Store the original raw error message
        self.error_message = error_message
        
        # Extract traceback object from the current execution context via sys.exc_info()
        _, _, exc_tb = error_details.exc_info()
        
        # Line number where the failure originated
        self.lineno = exc_tb.tb_lineno
        # Absolute file path of the script where the error occurred
        self.file_name = exc_tb.tb_frame.f_code.co_filename 
    
    # Custom string representation returned when printing the exception or reading traceback logs
    def __str__(self):
        return "Error occured in python script name [{0}] line number [{1}] error message [{2}]".format(
            self.file_name, self.lineno, str(self.error_message)
        )
        
if __name__ == '__main__':
    try:
        # Log entry when entering the block
        logger.logging.info("Enter the try block")
        # Trigger an intentional ZeroDivisionError
        a = 1 / 0
        print("This will not be printed", a)
    except Exception as e:
        # Wrap the base error with file name, line number, and details, then re-raise
        raise NetworkSecurityException(e, sys)