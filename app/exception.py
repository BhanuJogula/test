class AppException(Exception):
    def __init__(
        self, 
        message, 
        event: str, 
        customer_message: str = 'an error occurred',
        exception: Exception|None = None,
        status_code: int = 512,
        data: dict|None = None
    ):
        super().__init__(message)

        self.data = data or {}
        self.customer_message = customer_message
        self.event = event
        self.exception = exception
        self.status_code = status_code
        
         