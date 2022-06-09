#include <iostream>
#include <fstream>
#include <sstream>

class ParseException : public std::exception {
    std::string why;
public:
    ParseException(std::string const & why) : why(why) {}
    virtual const char * what() { return why.c_str(); }
};

std::string_view parseProof(std::string const & proofString) {
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

    std::cout << "Found a proof string for logic `" << proofString.substr(logicStart, logicEnd - logicStart) << '`' << std::endl;

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
    if (argc == 1) {
        std::cout << "Usage: " << argv[0] << " <proof-file>" << std::endl;
        return 1;
    }
    std::ifstream t(argv[1]);
    std::stringstream buffer;
    buffer << t.rdbuf();
    std::string proofString = buffer.str();
    auto proof = parseProof(proofString);
    std::cout << proof << std::endl;
}