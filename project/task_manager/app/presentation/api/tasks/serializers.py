from pydantic import BaseModel


class CreateTaskRequest(BaseModel):
    task_id: str
    description: str
    assignee_id: str
