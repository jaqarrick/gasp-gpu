FROM nvidia/cuda:12.8.0-devel-ubuntu24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY requirements.txt requirements-dev.txt ./

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt
COPY . /workspace

ENV PATH="/workspace/bin:$PATH"

RUN python3 --version \
    && nvcc --version \
    && nvdisasm --version \
    && echo "All tools OK"
ENV PYTHONPATH="/workspace/src"
ENTRYPOINT ["python", "-m", "gasp"]