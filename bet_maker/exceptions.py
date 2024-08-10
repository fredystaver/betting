from fastapi import HTTPException, status


class BettingExceptions(HTTPException):
    status_code: int = ...
    detail: str = ...

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class EventIsClosed(BettingExceptions):
    status_code = status.HTTP_409_CONFLICT
    detail = 'Событие закрыто для ставок'
