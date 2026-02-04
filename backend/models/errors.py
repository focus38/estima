class LLMError(Exception):
    stage: str

    def __init__(self, stage: str, message: str):
        self.stage = stage
        super().__init__(message)

class JobError(Exception):
    stage: str

    def __init__(self, stage: str, message: str):
        self.stage = stage
        super().__init__(message)