cmake_minimum_required(VERSION 3.16)
project(nodetrace_agent_cpp)

set(CMAKE_CXX_STANDARD 20)

find_package(CURL REQUIRED)

include_directories(include)
include_directories(${CURL_INCLUDE_DIRS})

add_executable(nodetrace-agent
    src/main.cpp
    src/agent.cpp
    src/config.cpp
    src/logger.cpp
    src/http_client.cpp
    src/heartbeat_service.cpp
)

target_link_libraries(nodetrace-agent ${CURL_LIBRARIES})