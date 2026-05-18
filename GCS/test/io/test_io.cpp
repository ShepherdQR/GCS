#include "test_framework.h"
#include "gcs/io/io.h"
#include <fstream>
#include <cstdio>

using namespace gcs;

static const std::string test_dir = "test/io/";

static void writeTestFile(const std::string& path, const std::string& content) {
    std::ofstream out(path);
    out << content;
    out.close();
}

static bool managersEqual(const Manager& a, const Manager& b) {
    if (a.rigidSets.size() != b.rigidSets.size()) return false;
    if (a.geometries.size() != b.geometries.size()) return false;
    if (a.constraints.size() != b.constraints.size()) return false;

    for (size_t i = 0; i < a.rigidSets.size(); ++i) {
        if (a.rigidSets[i].id != b.rigidSets[i].id) return false;
        if (a.rigidSets[i].geometryIds != b.rigidSets[i].geometryIds) return false;
    }
    for (size_t i = 0; i < a.geometries.size(); ++i) {
        if (a.geometries[i].id != b.geometries[i].id) return false;
        if (a.geometries[i].type != b.geometries[i].type) return false;
        if (a.geometries[i].rigidSetId != b.geometries[i].rigidSetId) return false;
        for (int k = 0; k < 6; ++k) {
            if (std::abs(a.geometries[i].v[k] - b.geometries[i].v[k]) > 1e-10) return false;
        }
    }
    for (size_t i = 0; i < a.constraints.size(); ++i) {
        if (a.constraints[i].id != b.constraints[i].id) return false;
        if (a.constraints[i].type != b.constraints[i].type) return false;
        if (a.constraints[i].geometryIds != b.constraints[i].geometryIds) return false;
        if (std::abs(a.constraints[i].value - b.constraints[i].value) > 1e-10) return false;
    }
    return true;
}

void test_io_read_valid_file() {
    Manager m;
    io::readGraph(m, test_dir + "basic_5g_2c.txt");
    GCS_ASSERT_EQ(m.rigidSets.size(), size_t(3), "IO01: rigidSets count");
    GCS_ASSERT_EQ(m.geometries.size(), size_t(5), "IO01: geometries count");
    GCS_ASSERT_EQ(m.constraints.size(), size_t(2), "IO01: constraints count");
}

void test_io_read_missing_file() {
    Manager m;
    io::readGraph(m, "nonexistent_file_12345.txt");
    GCS_ASSERT_EQ(m.rigidSets.size(), size_t(0), "IO02: missing file rigidSets empty");
    GCS_ASSERT_EQ(m.geometries.size(), size_t(0), "IO02: missing file geometries empty");
    GCS_ASSERT_EQ(m.constraints.size(), size_t(0), "IO02: missing file constraints empty");
}

void test_io_read_rigidsets() {
    Manager m;
    io::readGraph(m, test_dir + "basic_5g_2c.txt");
    GCS_ASSERT_EQ(m.rigidSets.size(), size_t(3), "IO03: rigidSets size 3");
    GCS_ASSERT_EQ(m.rigidSets[0].id, 0, "IO03: rigidSet[0] id");
    GCS_ASSERT_EQ(m.rigidSets[1].id, 1, "IO03: rigidSet[1] id");
    GCS_ASSERT_EQ(m.rigidSets[2].id, 2, "IO03: rigidSet[2] id");
}

void test_io_read_geometry_types() {
    Manager m;
    io::readGraph(m, test_dir + "basic_5g_2c.txt");
    GCS_ASSERT_EQ(m.geometries[0].type, GeometryType::Point, "IO04: geom 0 Point");
    GCS_ASSERT_EQ(m.geometries[1].type, GeometryType::Point, "IO04: geom 1 Point");
    GCS_ASSERT_EQ(m.geometries[2].type, GeometryType::Point, "IO04: geom 2 Point");
    GCS_ASSERT_EQ(m.geometries[3].type, GeometryType::Line, "IO04: geom 3 Line");
    GCS_ASSERT_EQ(m.geometries[4].type, GeometryType::Plane, "IO04: geom 4 Plane");
}

void test_io_read_geometry_params() {
    Manager m;
    io::readGraph(m, test_dir + "basic_5g_2c.txt");
    GCS_ASSERT_NEAR(m.geometries[1].v[0], 1.0, 1e-10, "IO05: geom 1 v[0]=1");
    GCS_ASSERT_NEAR(m.geometries[2].v[1], 1.0, 1e-10, "IO05: geom 2 v[1]=1");
}

void test_io_read_constraint_types() {
    Manager m;
    io::readGraph(m, test_dir + "basic_5g_2c.txt");
    GCS_ASSERT_EQ(m.constraints[0].type, ConstraintType::Coincident, "IO06: constr 0 Coincident");
    GCS_ASSERT_EQ(m.constraints[1].type, ConstraintType::Distance, "IO06: constr 1 Distance");
}

void test_io_read_constraint_values() {
    Manager m;
    io::readGraph(m, test_dir + "basic_5g_2c.txt");
    GCS_ASSERT_NEAR(m.constraints[0].value, 0.0, 1e-10, "IO07: constr 0 value");
    GCS_ASSERT_NEAR(m.constraints[1].value, 1.5, 1e-10, "IO07: constr 1 value");
}

void test_io_read_constraint_geometry_ids() {
    Manager m;
    io::readGraph(m, test_dir + "basic_5g_2c.txt");
    GCS_ASSERT_EQ(m.constraints[0].geometryIds.size(), size_t(2), "IO08: constr 0 geomIds size");
    GCS_ASSERT_EQ(m.constraints[0].geometryIds[0], 0, "IO08: constr 0 geomIds[0]");
    GCS_ASSERT_EQ(m.constraints[0].geometryIds[1], 2, "IO08: constr 0 geomIds[1]");
}

void test_io_dump_round_trip() {
    Manager m1;
    io::readGraph(m1, test_dir + "basic_5g_2c.txt");

    std::string tmpIn = "test_io_roundtrip_in.txt";
    {
        std::ofstream out(tmpIn);
        out << m1.rigidSets.size() << "\n";
        for (size_t i = 0; i < m1.rigidSets.size(); ++i) {
            if (i) out << ' ';
            out << m1.rigidSets[i].id;
        }
        out << "\n";
        out << m1.geometries.size() << "\n";
        for (const auto& g : m1.geometries) {
            out << g.id << ' ' << static_cast<int>(g.type) << ' ' << g.rigidSetId << "\n";
        }
        out << m1.constraints.size() << "\n";
        for (const auto& c : m1.constraints) {
            out << c.id << ' ' << static_cast<int>(c.type) << ' ' << c.geometryIds.size();
            for (int gid : c.geometryIds) out << ' ' << gid;
            out << "\n";
        }
        out << "\n";
        for (const auto& g : m1.geometries) {
            out << g.id;
            for (int k = 0; k < 6; ++k) out << ' ' << g.v[k];
            out << "\n";
        }
        out << "\n";
        for (const auto& c : m1.constraints) {
            out << c.id << ' ' << c.value << "\n";
        }
        out.close();
    }

    Manager m2;
    io::readGraph(m2, tmpIn);
    GCS_ASSERT(managersEqual(m1, m2), "IO09: round-trip managers equal");

    std::remove(tmpIn.c_str());
}

void test_io_dump_empty_path() {
    Manager m;
    RigidSet rs; rs.id = 0;
    m.rigidSets.push_back(rs);
    io::dumpGraph(m, "");
    GCS_ASSERT(true, "IO10: dumpGraph empty path no crash");
}

void test_io_print_summary() {
    Manager m;
    RigidSet rs; rs.id = 0;
    m.rigidSets.push_back(rs);
    Geometry g; g.id = 0; g.type = GeometryType::Point; g.rigidSetId = 0;
    for (int i = 0; i < 6; ++i) g.v[i] = 0;
    m.geometries.push_back(g);
    io::printSummary(m);
    GCS_ASSERT(true, "IO11: printSummary no crash");
}

int main() {
    std::cout << "=== IO Interface Tests ===\n\n";

    test_io_read_valid_file();
    test_io_read_missing_file();
    test_io_read_rigidsets();
    test_io_read_geometry_types();
    test_io_read_geometry_params();
    test_io_read_constraint_types();
    test_io_read_constraint_values();
    test_io_read_constraint_geometry_ids();
    test_io_dump_round_trip();
    test_io_dump_empty_path();
    test_io_print_summary();

    GCS_TEST_SUMMARY();
}
