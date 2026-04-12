class PushTripToQueueError(Exception):
    def __init__(self, message: str = "Failed to push Trip to queue."):
        super().__init__(message)
