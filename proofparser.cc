#include <iostream>
#include <fstream>
#include <sstream>
#include <cassert>
#include "base64.h"

class ParseException : public std::exception {
    std::string why;
public:
    explicit ParseException(std::string && why) : why(std::move(why)) {}
    const char * what() const noexcept override { return why.c_str(); }
};

enum class status_t { sat, unsat, unknown };

std::pair<status_t, std::string_view> getStatusFromProof(std::string_view const proofString) {
    auto firstLeadingNonWhitespace = proofString.find_first_not_of(" \t\n\r");
    if (firstLeadingNonWhitespace == std::string::npos) {
        // The input is empty or has only whitespaces
        throw ParseException("Error: empty or whitespace-only input");
    }
    auto firstTrailingWhitespaceOrParenthesis = proofString.find_first_of(" \t\n\r(", firstLeadingNonWhitespace);
    auto endOfInterestingStringIndex = firstTrailingWhitespaceOrParenthesis == std::string::npos ? proofString.size() : firstTrailingWhitespaceOrParenthesis;

    auto startIter = &proofString[firstLeadingNonWhitespace];
    auto endIter = &proofString[endOfInterestingStringIndex];

    auto status = std::string_view(startIter, endIter-startIter);
    auto remainingString = std::string_view(proofString.data() + endOfInterestingStringIndex);
    if (status == std::string_view("sat")) {
        return {status_t::sat, proofString.data() + firstTrailingWhitespaceOrParenthesis};
    } else if (status == std::string_view("unsat")) {
        return {status_t::unsat, remainingString};
    } else if (status == std::string_view("unknown")) {
        return {status_t::unknown, remainingString};
    } else {
        throw ParseException("Error: unrecognizable status");
    }
}

std::pair<std::string_view,std::string_view> getLogicFromProof(std::string_view const proofString) {
    auto initPos = proofString.find("(proof ");
    if (initPos == std::string::npos) {
        return {{}, {}};
    }

    auto logicStart = proofString.find_first_not_of(" \t", initPos + sizeof("(proof"));
    if (logicStart == std::string::npos) {
        throw ParseException("Error: logic not found");
    }

    auto logicEnd = proofString.find_first_of(" \t", logicStart);
    if (logicEnd == std::string::npos) {
        throw ParseException("Error: unterminated logic string");
    }

    return {proofString.substr(logicStart, logicEnd - logicStart), proofString.data() + logicEnd};
}

std::string_view parseProof(std::string_view const proofString) {

    auto proofStart = proofString.find_first_not_of(" \t\n\r");

    if (proofStart == std::string::npos) {
        return {}; // proof not found
    }

    if (proofString[proofStart] != '|') {
        throw ParseException("Error: excepting `|`");
    }

    auto proofEnd = proofString.find_first_of('|', proofStart+1);

    if (proofEnd == std::string::npos) {
        throw ParseException("Error: unterminated proof");
    }

    return {proofString.data() + proofStart + 1, proofEnd - 1 - proofStart};
}

int main(int argc, char ** argv) {
    if (argc != 4 || std::string(argv[1]) == "-h") {
        std::cerr << "Proofparser -- Extract base64-encoded compressed trail from the opensmt trail format\n\n";
        std::cerr << "Usage: " << argv[0] << " -o <output-proof> <trail-file>\n" << std::endl;
        return 1;
    }
    if (argv[1] != std::string("-o")) {
        std::cerr << "Unknown option: " << argv[1] << std::endl;
        return 1;
    }
    std::ifstream t(argv[3]);
    std::stringstream buffer;
    buffer << t.rdbuf();
    auto bufferString = buffer.str();
    try {
        auto [status, trailEnvelope] = getStatusFromProof(bufferString);
        if (status == status_t::unknown) {
            std::cout << "unknown" << std::endl;
        } else if (status == status_t::sat) {
            std::cout << "sat" << std::endl;
        } else {
            assert(status == status_t::unsat);
            auto [logic, trail] = getLogicFromProof(trailEnvelope);
            if (logic.empty() and trail.empty()) {
                std::cout << "unknown" << std::endl;
            } else {
                auto strippedTrail = parseProof(trail);
                if (strippedTrail.empty()) {
                    std::cout << "unknown" << std::endl;
                }
                std::string decodedProof = base64_decode(strippedTrail);
                std::ofstream decodedProofFile(argv[2]);
                decodedProofFile << decodedProof;
                decodedProofFile.close();
                std::cout << "unsat" << ' ' << logic << std::endl;
            }
        }
    } catch (ParseException & e) {
        std::cout << "invalid\n" << e.what() << std::endl;
        return 1;
    } catch (Base64Exception & e) {
        std::cout << "invalid\n" << e.what() << std::endl;
        return 1;
    }
}