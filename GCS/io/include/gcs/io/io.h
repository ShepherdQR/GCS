#pragma once

#include "gcs/core/core.h"
#include <string>

namespace gcs {
namespace io {

void readGraph(Manager& m, const std::string& path);
void readGraphJSON(Manager& m, const std::string& path);
void dumpGraph(const Manager& m, const std::string& inputPath);
void dumpGraphJSON(const Manager& m, const std::string& inputPath);
void dumpGraphLocal(const Manager& m, const std::string& inputPath);
void displayGraph(const std::string& graphFile);
void printSummary(const Manager& m);

}
}
