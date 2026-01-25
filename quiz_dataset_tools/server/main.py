from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from quiz_dataset_tools.server.models.tests import GetTestsRequest, GetTestsResponse
from quiz_dataset_tools.server.models.questions import (
    GetQuestionsRequest,
    GetQuestionsResponse,
)
from quiz_dataset_tools.server.models.texts import (
    UpdateTextRequest,
    UpdateTextResponse,
    SearchTestMimicTextsRequest,
    SearchTestMimicTextsResponse,
)
from quiz_dataset_tools.server.models.text_warnings import (
    GetTextWarningsRequest,
    GetTextWarningsResponse,
)
from quiz_dataset_tools.server.services.database import DatabaseService
from quiz_dataset_tools.server.services.mimic import MimicService

database_service = DatabaseService(
    "/Users/gz/Workspace/quiz-dataset-tools/output/domains"
)

mimic_service = MimicService(
    database_service,
    [database_service.get_data_dir("fl"), database_service.get_data_dir("ny")],
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for domain in database_service.get_domains():
    domain_data_dir = database_service.get_data_dir(domain)
    domain_images_dir = f"{domain_data_dir}/images"
    app.mount(f"/images/{domain}", StaticFiles(directory=domain_images_dir))

@app.post("/tests/get")
async def get_tests(req: GetTestsRequest) -> GetTestsResponse:
    return database_service.get_tests(req)


@app.post("/questions/get")
async def get_questions(req: GetQuestionsRequest) -> GetQuestionsResponse:
    return database_service.get_questions(req)


@app.post("/text/update")
async def update_text(req: UpdateTextRequest) -> UpdateTextResponse:
    return database_service.update_text(req)


@app.post("/text_warnings/get")
async def get_text_warnings(req: GetTextWarningsRequest) -> GetTextWarningsResponse:
    return database_service.get_text_warnings(req)


@app.post("/mimic_text/search")
async def search_mimic_text(
    req: SearchTestMimicTextsRequest,
) -> SearchTestMimicTextsResponse:
    return mimic_service.search_test_texts(req)
