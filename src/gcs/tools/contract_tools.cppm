module;

#include <string>
#include <vector>

export module gcs.contract_tools;

export import gcs.kernel;

export namespace gcs::tools {

using gcs::kernel::ContextSnapshot;
using gcs::kernel::ModelSnapshot;
using gcs::kernel::ReportMessage;

enum class FixtureKind {
    two_point_distance,
    unsatisfied_two_point_distance,
    two_component_distance,
    missing_entity_reference,
};

struct FixtureBuildRequest {
    FixtureKind kind = FixtureKind::two_point_distance;
    int deterministic_seed = 0;
};

struct FixtureProvenance {
    std::string fixture_id;
    std::string generator = "gcs.contract_tools";
    int deterministic_seed = 0;
    std::string schema_version = "gcs-0.3";
};

struct FixtureBundle {
    ModelSnapshot model;
    ContextSnapshot whole_context;
    FixtureProvenance provenance;
};

struct InvariantCheckRequest {
    ModelSnapshot model;
    ContextSnapshot context;
};

struct InvariantReport {
    bool valid = true;
    int entity_count = 0;
    int constraint_count = 0;
    int context_entity_count = 0;
    int context_constraint_count = 0;
    std::vector<ReportMessage> messages;
};

struct GoldenReportRequest {
    FixtureBundle fixture;
    std::string report_name;
};

struct GoldenReport {
    std::string report_name;
    std::string digest_algorithm = "fnv1a64";
    std::string digest;
    std::string canonical_summary;
};

struct ModuleImport {
    std::string module;
    std::string imported_module;
};

struct DependencyAuditRequest {
    std::vector<ModuleImport> imports;
};

struct DependencyViolation {
    std::string module;
    std::string imported_module;
    std::string code;
};

struct DependencyAuditReport {
    bool valid = true;
    std::vector<DependencyViolation> violations;
};

ModelSnapshot make_two_point_distance_model();
ModelSnapshot make_unsatisfied_two_point_distance_model();
ModelSnapshot make_two_component_distance_model();
ModelSnapshot make_missing_entity_reference_model();
ContextSnapshot make_whole_context_for(const ModelSnapshot& model);
gcs::kernel::ContractResult<FixtureBundle> build_fixture(FixtureBuildRequest request);
gcs::kernel::ContractResult<InvariantReport> check_invariants(
    InvariantCheckRequest request);
gcs::kernel::ContractResult<GoldenReport> write_golden_report(GoldenReportRequest request);
gcs::kernel::ContractResult<DependencyAuditReport> audit_module_dependencies(
    DependencyAuditRequest request);

}
