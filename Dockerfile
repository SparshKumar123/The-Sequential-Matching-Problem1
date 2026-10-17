FROM python:3.12.7-slim
WORKDIR /app
COPY wheelhouse/ /wheelhouse/
COPY requirements.txt ./
RUN python -m pip install --no-index --find-links=/wheelhouse -r requirements.txt \
    && rm -rf /wheelhouse
COPY kit.py policy.py ./
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER 65534:65534
ENTRYPOINT ["python", "policy.py"]
