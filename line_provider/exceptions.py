from fastapi import HTTPException, status


class BettingExceptions(HTTPException):
    status_code: int = ...
    detail: str = ...

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class EventIsNotExists(BettingExceptions):
    status_code = status.HTTP_404_NOT_FOUND
    detail = 'Событие не существует'
