FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libssl-dev \
    python3 \
    golang-go \
    rustc \
    openjdk-17-jdk \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /sandbox


CMD ["/bin/bash"]