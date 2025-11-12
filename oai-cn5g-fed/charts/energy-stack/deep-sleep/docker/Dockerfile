# Dockerfile for FlexRIC Deep-Sleep xApp
FROM ubuntu:22.04 AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    cmake \
    g++ \
    git \
    libsctp-dev \
    libconfig-dev \
    libyaml-cpp-dev \
    ninja-build \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Clone and build FlexRIC
WORKDIR /build
RUN git clone https://github.com/flexric/flexric.git
WORKDIR /build/flexric
RUN mkdir build && cd build && \
    cmake .. -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DENABLE_MAC_SM=ON \
    -DENABLE_KPM_SM=ON \
    -DENABLE_RC_SM=ON && \
    ninja

# Build the Deep-Sleep xApp
WORKDIR /build/xapp
COPY flexric_xapp_deep_sleep.cpp .
COPY CMakeLists.txt .

# CMakeLists.txt content
RUN cat > CMakeLists.txt << 'EOF'
cmake_minimum_required(VERSION 3.15)
project(flexric_xapp_deep_sleep)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Threads REQUIRED)

# FlexRIC paths
set(FLEXRIC_DIR /build/flexric)
set(FLEXRIC_BUILD_DIR ${FLEXRIC_DIR}/build)

include_directories(
    ${FLEXRIC_DIR}/src
    ${FLEXRIC_DIR}/src/xApp
    ${FLEXRIC_DIR}/src/sm/mac_sm
    ${FLEXRIC_DIR}/src/sm/kpm_sm_v2.02
    ${FLEXRIC_DIR}/src/sm/rc_sm
    ${FLEXRIC_BUILD_DIR}/src
)

link_directories(
    ${FLEXRIC_BUILD_DIR}/src/xApp
    ${FLEXRIC_BUILD_DIR}/src/sm
    ${FLEXRIC_BUILD_DIR}/src/lib
)

add_executable(flexric_xapp_deep_sleep flexric_xapp_deep_sleep.cpp)

target_link_libraries(flexric_xapp_deep_sleep
    xapp_api
    mac_sm
    kpm_sm_v2_02
    rc_sm
    e2ap
    sctp
    pthread
    config
    yaml-cpp
)
EOF

RUN mkdir build && cd build && \
    cmake .. && \
    make

# Runtime image
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    libsctp1 \
    libconfig9 \
    libyaml-cpp0.7 \
    iproute2 \
    iputils-ping \
    tcpdump \
    && rm -rf /var/lib/apt/lists/*

# Copy built artifacts
COPY --from=builder /build/flexric/build/src/xApp/lib*.so* /usr/local/lib/
COPY --from=builder /build/flexric/build/src/sm/lib*.so* /usr/local/lib/
COPY --from=builder /build/flexric/build/src/lib/lib*.so* /usr/local/lib/
COPY --from=builder /build/xapp/build/flexric_xapp_deep_sleep /app/

# Update library cache
RUN ldconfig

WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD pgrep flexric_xapp_deep_sleep || exit 1

ENTRYPOINT ["/app/flexric_xapp_deep_sleep"]