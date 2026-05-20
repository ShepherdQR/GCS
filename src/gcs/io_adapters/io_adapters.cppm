module;

#include <string>

export module gcs.io_adapters;

export import gcs.kernel;

export namespace gcs::io {

void readGraph(Manager& m, const std::string& path);
void readGraphJSON(Manager& m, const std::string& path);
void dumpGraph(const Manager& m, const std::string& inputPath);
void dumpGraphJSON(const Manager& m, const std::string& inputPath);
void printSummary(const Manager& m);

}
