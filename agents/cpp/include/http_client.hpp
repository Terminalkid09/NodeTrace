#pragma once
#include <string>

class HttpClient {
public:
    std::string post(const std::string& url, const std::string& body);
};