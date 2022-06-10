#include <iostream>
#include <fstream>
#include <sstream>
#include "base64.h"

class ParseException : public std::exception {
    std::string why;
public:
    explicit ParseException(std::string && why) : why(std::move(why)) {}
    const char * what() const noexcept override { return why.c_str(); }
};

std::pair<std::string,unsigned long> getLogicFromProof(std::string const & proofString) {
    auto initPos = proofString.find("(proof ");
    if (initPos == std::string::npos) {
        throw ParseException("Error: proof not found");
    }

    auto logicStart = proofString.find_first_not_of(" \t", initPos + sizeof("(proof"));
    if (logicStart == std::string::npos) {
        throw ParseException("Error: logic not found");
    }

    auto logicEnd = proofString.find_first_of(" \t", logicStart);
    if (logicEnd == std::string::npos) {
        throw ParseException("Error: unterminated logic string");
    }

    return {proofString.substr(logicStart, logicEnd - logicStart), logicEnd};
}

std::string_view parseProof(std::string && proofString) {

    auto [logic, logicEnd] = getLogicFromProof(proofString);

    auto proofStart = proofString.find_first_not_of(" \t", logicEnd);

    if (proofStart == std::string::npos){
        throw ParseException("Error: logic not found");
    }

    if (proofString[proofStart] != '|') {
        throw ParseException("Error: excepting `|`");
    }

    auto proofEnd = proofString.find_first_of('|', proofStart+1);

    if (proofEnd == std::string::npos) {
        throw ParseException("Error: unterminated proof");
    }

    return {proofString.c_str()+proofStart+1, proofEnd-1-proofStart};
}

int main(int argc, char ** argv) {
    if (argc != 3 || std::string(argv[1]) == "-h") {
        std::cerr << "Proofparser -- Extract base64-encoded compressed trail from the opensmt trail format\n\n";
        std::cerr << "Usage: " << argv[0] << " [-t | -l] <trail-file>\n";
        std::cerr << "     -t   - print the trail\n";
        std::cerr << "     -l   - print only the logic and not the trail\n" << std::endl;
        return 1;
    }
    if (argv[1] != std::string("-t") and argv[1] != std::string("-l")) {
        std::cerr << "Unknown option: " << argv[1] << std::endl;
        return 1;
    }
    std::ifstream t(argv[2]);
    std::stringstream buffer;
    buffer << t.rdbuf();
    try {
        if (std::string(argv[1]) == "-l") {
            auto [logic, pos] = getLogicFromProof(buffer.str());
            std::cout << logic << std::endl;
        } else if (std::string(argv[1]) =="-t") {
            std::string decodedProof = base64_decode(parseProof(buffer.str()));
            std::cout << decodedProof;
        } else {
            assert(false);
        }
    } catch (ParseException & e) {
        std::cerr << e.what() << std::endl;
        return 1;
    }
}