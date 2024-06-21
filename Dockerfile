FROM python:3.12

WORKDIR /app

COPY requirements.txt setup.py .
COPY quiz_dataset_tools ./quiz_dataset_tools

RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install .

EXPOSE 8000

CMD ["uvicorn", "quiz_dataset_tools.server.main:app", "--host", "0.0.0.0"]
