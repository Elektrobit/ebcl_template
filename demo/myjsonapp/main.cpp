#include <iostream>
#include <json/json.h>
#include <cstdlib>

int main() {
    
    for (int i = 0; i < 100; ++i) {
        std::cout << "Iteration " << i + 1 << ": Exemplary application linked with jsoncpp" \
            " library to parse a structure into json document" << std::endl;

        Json::Value root;
        root["name"] = "John Doe";
        root["age"] = 30;
        root["city"] = "New York";

        Json::StreamWriterBuilder builder;
        const std::string jsonStr = Json::writeString(builder, root);

        std::cout << "Serialized JSON: " << jsonStr << std::endl;

        std::cout << "Sleeping for 10 seconds..." << std::endl;
        std::system("sleep 10");
    }

    return 0;
}
