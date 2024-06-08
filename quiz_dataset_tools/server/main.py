from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from quiz_dataset_tools.server.models.tests import GetTestsRequest, GetTestsResponse
from quiz_dataset_tools.server.models.questions import (
    GetQuestionsRequest,
    GetQuestionsResponse,
)
from quiz_dataset_tools.server.models.texts import (
    UpdateTextRequest,
    UpdateTextResponse,
)
from quiz_dataset_tools.server.service import DatabaseService

service = DatabaseService(
    "/Users/d.vasilyev/Workspace/quiz-dataset-tools/output/tx/prebuild/data"
)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/tests/get")
async def get_tests(req: GetTestsRequest) -> GetTestsResponse:
    return service.get_tests(req)


@app.post("/questions/get")
async def get_questions(req: GetQuestionsRequest) -> GetQuestionsResponse:
    return service.get_questions(req)


@app.post("/text/update")
async def update_text(req: UpdateTextRequest) -> UpdateTextResponse:
    return service.update_text(req)
