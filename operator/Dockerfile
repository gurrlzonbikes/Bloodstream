FROM python:3.12-slim
WORKDIR /operator
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bloodstream ./bloodstream
COPY main.py .
ENV PYTHONUNBUFFERED=1
EXPOSE 8080 9091
CMD ["python", "main.py"]
