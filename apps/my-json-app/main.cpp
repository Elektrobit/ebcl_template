#include <iostream>
#include <json/json.h>

int main() {
    // Create a JSON object
    std::cout << "Exemplary application linked with jsoncpp" \
	   " library to parse a structure into json document" << std::endl;
    Json::Value root;
    root["name"] = "John Doe";
    root["age"] = 30;
    root["city"] = "New York";

    // Serialize the JSON object to a string
    Json::StreamWriterBuilder builder;
    const std::string jsonStr = Json::writeString(builder, root);

    // Print the serialized JSON string
    std::cout << jsonStr << std::endl;

    return 0;
}

