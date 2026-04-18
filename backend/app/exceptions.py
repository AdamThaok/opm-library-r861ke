from fastapi import HTTPException, status

class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Item not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class ConflictException(HTTPException):
    def __init__(self, detail: str = "Conflict in state transition or resource creation"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
