#include "io/io.h"
#include <iostream>
#include <fstream>
#include <algorithm>
#include <sstream>
#include <cmath>

namespace gcs {
namespace io {

namespace {

struct JsonValue {
    enum Type { Null, Bool, Number, String, Array, Object };
    Type type = Null;
    bool boolVal = false;
    double numVal = 0.0;
    std::string strVal;
    std::vector<JsonValue> arrVal;
    std::vector<std::pair<std::string, JsonValue>> objVal;

    const JsonValue* get(const std::string& key) const {
        if (type != Object) return nullptr;
        for (auto& p : objVal) {
            if (p.first == key) return &p.second;
        }
        return nullptr;
    }

    double asNumber(double def = 0.0) const {
        if (type == Number) return numVal;
        return def;
    }

    int asInt(int def = 0) const {
        if (type == Number) return (int)numVal;
        return def;
    }

    const std::string& asString() const {
        static const std::string empty;
        return type == String ? strVal : empty;
    }

    size_t size() const {
        return type == Array ? arrVal.size() : (type == Object ? objVal.size() : 0);
    }

    const JsonValue& operator[](size_t idx) const {
        static const JsonValue nullVal;
        if (type == Array && idx < arrVal.size()) return arrVal[idx];
        return nullVal;
    }
};

class JsonParser {
public:
    JsonParser(const std::string& input) : src_(input), pos_(0) {}

    JsonValue parse() {
        skipWS();
        return parseValue();
    }

private:
    std::string src_;
    size_t pos_;

    char peek() { return pos_ < src_.size() ? src_[pos_] : '\0'; }
    char advance() { return pos_ < src_.size() ? src_[pos_++] : '\0'; }

    void skipWS() {
        while (pos_ < src_.size() && (src_[pos_] == ' ' || src_[pos_] == '\t' ||
               src_[pos_] == '\n' || src_[pos_] == '\r')) {
            pos_++;
        }
    }

    bool expect(char c) {
        skipWS();
        if (peek() == c) { advance(); return true; }
        return false;
    }

    JsonValue parseValue() {
        skipWS();
        if (pos_ >= src_.size()) return JsonValue();

        char c = peek();
        if (c == '{') return parseObject();
        if (c == '[') return parseArray();
        if (c == '"') return parseString();
        if (c == 't' || c == 'f') return parseBool();
        if (c == 'n') return parseNull();
        return parseNumber();
    }

    JsonValue parseObject() {
        JsonValue v;
        v.type = JsonValue::Object;
        advance();
        skipWS();
        if (peek() == '}') { advance(); return v; }

        while (true) {
            skipWS();
            JsonValue keyVal = parseString();
            skipWS();
            expect(':');
            JsonValue val = parseValue();
            v.objVal.push_back({keyVal.strVal, val});
            skipWS();
            if (peek() == ',') { advance(); continue; }
            if (peek() == '}') { advance(); break; }
            break;
        }
        return v;
    }

    JsonValue parseArray() {
        JsonValue v;
        v.type = JsonValue::Array;
        advance();
        skipWS();
        if (peek() == ']') { advance(); return v; }

        while (true) {
            v.arrVal.push_back(parseValue());
            skipWS();
            if (peek() == ',') { advance(); continue; }
            if (peek() == ']') { advance(); break; }
            break;
        }
        return v;
    }

    JsonValue parseString() {
        JsonValue v;
        v.type = JsonValue::String;
        advance();
        while (pos_ < src_.size() && src_[pos_] != '"') {
            if (src_[pos_] == '\\') {
                pos_++;
                if (pos_ < src_.size()) {
                    char esc = src_[pos_];
                    if (esc == 'n') v.strVal += '\n';
                    else if (esc == 't') v.strVal += '\t';
                    else if (esc == '\\') v.strVal += '\\';
                    else if (esc == '"') v.strVal += '"';
                    else if (esc == '/') v.strVal += '/';
                    else v.strVal += esc;
                }
            } else {
                v.strVal += src_[pos_];
            }
            pos_++;
        }
        if (pos_ < src_.size()) pos_++;
        return v;
    }

    JsonValue parseNumber() {
        JsonValue v;
        v.type = JsonValue::Number;
        size_t start = pos_;
        if (peek() == '-') pos_++;
        while (pos_ < src_.size() && (src_[pos_] >= '0' && src_[pos_] <= '9')) pos_++;
        if (pos_ < src_.size() && src_[pos_] == '.') {
            pos_++;
            while (pos_ < src_.size() && (src_[pos_] >= '0' && src_[pos_] <= '9')) pos_++;
        }
        if (pos_ < src_.size() && (src_[pos_] == 'e' || src_[pos_] == 'E')) {
            pos_++;
            if (pos_ < src_.size() && (src_[pos_] == '+' || src_[pos_] == '-')) pos_++;
            while (pos_ < src_.size() && (src_[pos_] >= '0' && src_[pos_] <= '9')) pos_++;
        }
        v.numVal = std::stod(src_.substr(start, pos_ - start));
        return v;
    }

    JsonValue parseBool() {
        JsonValue v;
        v.type = JsonValue::Bool;
        if (src_.compare(pos_, 4, "true") == 0) {
            v.boolVal = true;
            pos_ += 4;
        } else if (src_.compare(pos_, 5, "false") == 0) {
            v.boolVal = false;
            pos_ += 5;
        }
        return v;
    }

    JsonValue parseNull() {
        JsonValue v;
        v.type = JsonValue::Null;
        if (src_.compare(pos_, 4, "null") == 0) pos_ += 4;
        return v;
    }
};

class JsonWriter {
public:
    void writeStartObject() {
        if (!afterKey_) beforeElement();
        afterKey_ = false;
        oss_ << "{";
        indent_++;
        firstStack_.push_back(true);
    }
    void writeEndObject() {
        indent_--;
        if (!isFirstInCurrent()) newline();
        oss_ << "}";
        if (!firstStack_.empty()) firstStack_.pop_back();
    }
    void writeStartArray() {
        if (!afterKey_) beforeElement();
        afterKey_ = false;
        oss_ << "[";
        indent_++;
        firstStack_.push_back(true);
    }
    void writeEndArray() {
        indent_--;
        if (!isFirstInCurrent()) newline();
        oss_ << "]";
        if (!firstStack_.empty()) firstStack_.pop_back();
    }

    void writeKey(const std::string& key) {
        beforeElement();
        newline();
        oss_ << "\"" << escapeStr(key) << "\": ";
        afterKey_ = true;
    }

    void writeValue(int v) { oss_ << v; afterKey_ = false; }
    void writeValue(double v) {
        if (v == std::floor(v) && std::abs(v) < 1e15) {
            oss_ << (long long)v;
        } else {
            char buf[64];
            std::snprintf(buf, sizeof(buf), "%.15g", v);
            oss_ << buf;
        }
        afterKey_ = false;
    }
    void writeValue(const std::string& v) { oss_ << "\"" << escapeStr(v) << "\""; afterKey_ = false; }
    void writeValue(bool v) { oss_ << (v ? "true" : "false"); afterKey_ = false; }
    void writeNull() { oss_ << "null"; afterKey_ = false; }

    void writeArrayValue(int v) { beforeElement(); oss_ << v; }
    void writeArrayValue(double v) {
        beforeElement();
        if (v == std::floor(v) && std::abs(v) < 1e15) {
            oss_ << (long long)v;
        } else {
            char buf[64];
            std::snprintf(buf, sizeof(buf), "%.15g", v);
            oss_ << buf;
        }
    }

    void writeKeyValue(const std::string& key, int v) {
        writeKey(key);
        writeValue(v);
    }
    void writeKeyValue(const std::string& key, double v) {
        writeKey(key);
        writeValue(v);
    }
    void writeKeyValue(const std::string& key, const std::string& v) {
        writeKey(key);
        writeValue(v);
    }

    std::string str() const { return oss_.str(); }

private:
    std::ostringstream oss_;
    int indent_ = 0;
    bool afterKey_ = false;
    std::vector<bool> firstStack_;

    bool isFirstInCurrent() const { return firstStack_.empty() ? true : firstStack_.back(); }
    void markWritten() { if (!firstStack_.empty()) firstStack_.back() = false; }
    void beforeElement() {
        if (!isFirstInCurrent()) oss_ << ",";
        markWritten();
    }

    void newline() {
        oss_ << "\n";
        for (int i = 0; i < indent_; i++) oss_ << "  ";
    }

    static std::string escapeStr(const std::string& s) {
        std::string out;
        for (char c : s) {
            if (c == '"') out += "\\\"";
            else if (c == '\\') out += "\\\\";
            else if (c == '\n') out += "\\n";
            else if (c == '\t') out += "\\t";
            else out += c;
        }
        return out;
    }
};

}

static void writeJsonValue(std::ostream& out, const JsonValue& v);

void readGraph(Manager& m, const std::string& path) {
    std::ifstream in(path);
    if (!in) {
        std::cerr << "Failed to open '" << path << "'\n";
        return;
    }

    int numRigid;
    if (!(in >> numRigid)) {
        std::cerr << "Failed to read number of rigid sets\n";
        return;
    }
    for (int i = 0; i < numRigid; ++i) {
        int id; in >> id;
        RigidSet rs; rs.id = id;
        m.rigidSets.push_back(rs);
    }

    int numGeom; in >> numGeom;
    for (int i = 0; i < numGeom; ++i) {
        Geometry g;
        int typeInt;
        in >> g.id >> typeInt >> g.rigidSetId;
        g.type = static_cast<GeometryType>(typeInt);
        for (int k = 0; k < 6; ++k) g.v[k] = 0.0;
        m.geometries.push_back(g);
        auto* rs = m.findRigidSet(g.rigidSetId);
        if (rs) rs->geometryIds.push_back(g.id);
    }

    int numConst; in >> numConst;
    for (int i = 0; i < numConst; ++i) {
        Constraint c;
        int typeInt, numConn = 0;
        in >> c.id >> typeInt >> numConn;
        c.type = static_cast<ConstraintType>(typeInt);
        c.value = 0.0;
        for (int j = 0; j < numConn; ++j) {
            int gid; in >> gid;
            c.geometryIds.push_back(gid);
        }
        m.constraints.push_back(c);
    }

    for (size_t i = 0; i < m.geometries.size(); ++i) {
        int id; in >> id;
        auto* g = m.findGeometry(id);
        if (!g) {
            std::cerr << "Geometry id " << id << " not found in parameters\n";
            return;
        }
        for (int k = 0; k < 6; ++k) in >> g->v[k];
    }

    for (size_t i = 0; i < m.constraints.size(); ++i) {
        int id; double val; in >> id >> val;
        auto* c = m.findConstraint(id);
        if (!c) {
            std::cerr << "Constraint id " << id << " not found in parameters\n";
            return;
        }
        c->value = val;
    }
}

void readGraphJSON(Manager& m, const std::string& path) {
    std::ifstream in(path);
    if (!in) {
        std::cerr << "Failed to open '" << path << "'\n";
        return;
    }
    std::stringstream ss;
    ss << in.rdbuf();
    std::string content = ss.str();

    JsonParser parser(content);
    JsonValue root = parser.parse();

    const JsonValue* rsArr = root.get("rigid_sets");
    if (rsArr && rsArr->type == JsonValue::Array) {
        for (size_t i = 0; i < rsArr->size(); i++) {
            const JsonValue& rsVal = (*rsArr)[i];
            RigidSet rs;
            rs.id = rsVal.get("id") ? rsVal.get("id")->asInt() : 0;
            const JsonValue* gids = rsVal.get("geometry_ids");
            if (gids && gids->type == JsonValue::Array) {
                for (size_t j = 0; j < gids->size(); j++) {
                    rs.geometryIds.push_back((*gids)[j].asInt());
                }
            }
            m.rigidSets.push_back(rs);
        }
    }

    const JsonValue* geomArr = root.get("geometries");
    if (geomArr && geomArr->type == JsonValue::Array) {
        for (size_t i = 0; i < geomArr->size(); i++) {
            const JsonValue& gVal = (*geomArr)[i];
            Geometry g;
            g.id = gVal.get("id") ? gVal.get("id")->asInt() : 0;
            g.type = static_cast<GeometryType>(gVal.get("type") ? gVal.get("type")->asInt() : 0);
            g.rigidSetId = gVal.get("rigid_set_id") ? gVal.get("rigid_set_id")->asInt() : 0;
            for (int k = 0; k < 6; ++k) g.v[k] = 0.0;
            const JsonValue* vArr = gVal.get("v");
            if (vArr && vArr->type == JsonValue::Array) {
                for (int k = 0; k < 6 && k < (int)vArr->size(); k++) {
                    g.v[k] = (*vArr)[k].asNumber();
                }
            }
            m.geometries.push_back(g);
            auto* rs = m.findRigidSet(g.rigidSetId);
            if (rs && std::find(rs->geometryIds.begin(), rs->geometryIds.end(), g.id) == rs->geometryIds.end()) {
                rs->geometryIds.push_back(g.id);
            }
        }
    }

    const JsonValue* constArr = root.get("constraints");
    if (constArr && constArr->type == JsonValue::Array) {
        for (size_t i = 0; i < constArr->size(); i++) {
            const JsonValue& cVal = (*constArr)[i];
            Constraint c;
            c.id = cVal.get("id") ? cVal.get("id")->asInt() : 0;
            c.type = static_cast<ConstraintType>(cVal.get("type") ? cVal.get("type")->asInt() : 0);
            c.value = cVal.get("value") ? cVal.get("value")->asNumber() : 0.0;
            const JsonValue* gids = cVal.get("geometry_ids");
            if (gids && gids->type == JsonValue::Array) {
                for (size_t j = 0; j < gids->size(); j++) {
                    c.geometryIds.push_back((*gids)[j].asInt());
                }
            }
            m.constraints.push_back(c);
        }
    }

    const JsonValue* histArr = root.get("history");
    if (histArr && histArr->type == JsonValue::Array) {
        for (size_t i = 0; i < histArr->size(); i++) {
            const JsonValue& hVal = (*histArr)[i];
            HistoryAction ha;
            ha.action = hVal.get("action") ? hVal.get("action")->asString() : "";
            const JsonValue* payload = hVal.get("payload");
            if (payload) {
                std::ostringstream payloadSS;
                writeJsonValue(payloadSS, *payload);
                ha.payload = payloadSS.str();
            }
            m.history.push_back(ha);
        }
    }
}

static void writeJsonValue(std::ostream& out, const JsonValue& v) {
    switch (v.type) {
        case JsonValue::Null: out << "null"; break;
        case JsonValue::Bool: out << (v.boolVal ? "true" : "false"); break;
        case JsonValue::Number: out << v.numVal; break;
        case JsonValue::String: out << "\"" << v.strVal << "\""; break;
        case JsonValue::Array:
            out << "[";
            for (size_t i = 0; i < v.arrVal.size(); i++) {
                if (i) out << ",";
                writeJsonValue(out, v.arrVal[i]);
            }
            out << "]";
            break;
        case JsonValue::Object:
            out << "{";
            for (size_t i = 0; i < v.objVal.size(); i++) {
                if (i) out << ",";
                out << "\"" << v.objVal[i].first << "\":";
                writeJsonValue(out, v.objVal[i].second);
            }
            out << "}";
            break;
    }
}

void dumpGraph(const Manager& m, const std::string& inputPath) {
    if (inputPath.empty()) {
        return;
    }

    std::string base = inputPath;
    size_t pos = base.find_last_of("/\\");
    if (pos != std::string::npos) base = base.substr(pos + 1);
    size_t dot = base.find_last_of('.');
    if (dot != std::string::npos) base = base.substr(0, dot);

    std::string outName = base + "_graph.txt";
    std::string outDir;
    size_t lastSlash = inputPath.find_last_of("/\\");
    if (lastSlash != std::string::npos) {
        outDir = inputPath.substr(0, lastSlash + 1);
    }
    std::ofstream out(outDir + outName);

    if (!out) {
        std::cerr << "Failed to open output graph file: " << outName << "\n";
        return;
    }

    out << m.rigidSets.size() << "\n";
    for (size_t i = 0; i < m.rigidSets.size(); ++i) {
        if (i) out << ' ';
        out << m.rigidSets[i].id;
    }
    out << "\n";

    out << m.geometries.size() << "\n";
    for (const auto &g : m.geometries) {
        out << g.id << ' ' << static_cast<int>(g.type) << ' ' << g.rigidSetId << "\n";
    }

    out << m.constraints.size() << "\n";
    for (const auto &c : m.constraints) {
        out << c.id << ' ' << static_cast<int>(c.type) << ' ' << c.geometryIds.size();
        for (int gid : c.geometryIds) out << ' ' << gid;
        out << "\n";
    }

    out << "\n";
    for (const auto &g : m.geometries) {
        out << g.id;
        for (int k = 0; k < 6; ++k) out << ' ' << g.v[k];
        out << "\n";
    }

    out << "\n";
    for (const auto &c : m.constraints) {
        out << c.id << ' ' << c.value << "\n";
    }

    out.close();
    std::cout << "Dumped graph to: " << outName << "\n";
}

void dumpGraphJSON(const Manager& m, const std::string& inputPath) {
    if (inputPath.empty()) return;

    std::string base = inputPath;
    size_t pos = base.find_last_of("/\\");
    if (pos != std::string::npos) base = base.substr(pos + 1);
    size_t dot = base.find_last_of('.');
    if (dot != std::string::npos) base = base.substr(0, dot);

    std::string outName = base + "_graph.json";
    std::string outDir;
    size_t lastSlash = inputPath.find_last_of("/\\");
    if (lastSlash != std::string::npos) {
        outDir = inputPath.substr(0, lastSlash + 1);
    }
    std::ofstream out(outDir + outName);
    if (!out) {
        std::cerr << "Failed to open output JSON file: " << outName << "\n";
        return;
    }

    JsonWriter w;
    w.writeStartObject();

    w.writeKeyValue("format_version", 1);

    w.writeKey("rigid_sets");
    w.writeStartArray();
    for (const auto& rs : m.rigidSets) {
        w.writeStartObject();
        w.writeKeyValue("id", rs.id);
        w.writeKey("geometry_ids");
        w.writeStartArray();
        for (int gid : rs.geometryIds) w.writeArrayValue(gid);
        w.writeEndArray();
        w.writeEndObject();
    }
    w.writeEndArray();

    w.writeKey("geometries");
    w.writeStartArray();
    for (const auto& g : m.geometries) {
        w.writeStartObject();
        w.writeKeyValue("id", g.id);
        w.writeKeyValue("type", static_cast<int>(g.type));
        w.writeKeyValue("rigid_set_id", g.rigidSetId);
        w.writeKey("v");
        w.writeStartArray();
        for (int k = 0; k < 6; k++) w.writeArrayValue(g.v[k]);
        w.writeEndArray();
        w.writeEndObject();
    }
    w.writeEndArray();

    w.writeKey("constraints");
    w.writeStartArray();
    for (const auto& c : m.constraints) {
        w.writeStartObject();
        w.writeKeyValue("id", c.id);
        w.writeKeyValue("type", static_cast<int>(c.type));
        w.writeKey("geometry_ids");
        w.writeStartArray();
        for (int gid : c.geometryIds) w.writeArrayValue(gid);
        w.writeEndArray();
        w.writeKeyValue("value", c.value);
        w.writeEndObject();
    }
    w.writeEndArray();

    w.writeKey("history");
    w.writeStartArray();
    for (const auto& h : m.history) {
        w.writeStartObject();
        w.writeKeyValue("action", h.action);
        w.writeKey("payload");
        if (!h.payload.empty()) {
            w.writeValue(h.payload);
        } else {
            w.writeStartObject();
            w.writeEndObject();
        }
        w.writeEndObject();
    }
    w.writeEndArray();

    w.writeEndObject();

    out << w.str() << "\n";
    out.close();
    std::cout << "Dumped graph to: " << outName << "\n";
}

void printSummary(const Manager& m) {
    std::cout << "Rigid Sets (" << m.rigidSets.size() << "):\n";
    for (auto &rs : m.rigidSets) {
        std::cout << "  RS id=" << rs.id << " geometries:";
        for (int gid : rs.geometryIds) std::cout << ' ' << gid;
        std::cout << '\n';
    }
    std::cout << "Geometries (" << m.geometries.size() << "):\n";
    for (auto &g : m.geometries) {
        std::cout << "  G id=" << g.id << " type=" << typeNameGeometry(g.type)
                  << " rs=" << g.rigidSetId << " values:";
        for (int k = 0; k < 6; ++k) std::cout << ' ' << g.v[k];
        std::cout << '\n';
    }
    std::cout << "Constraints (" << m.constraints.size() << "):\n";
    for (auto &c : m.constraints) {
        std::cout << "  C id=" << c.id << " type=" << typeNameConstraint(c.type) << " connects:";
        for (int gid : c.geometryIds) std::cout << ' ' << gid;
        std::cout << " value=" << c.value << "\n";
    }
    if (!m.history.empty()) {
        std::cout << "History (" << m.history.size() << "):\n";
        for (const auto& h : m.history) {
            std::cout << "  " << h.action << ": " << h.payload << "\n";
        }
    }
}

}
}
