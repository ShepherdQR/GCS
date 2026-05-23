module;

#include <string>
#include <vector>

export module gcs.contract_tools;

export import gcs.kernel;

export namespace gcs::tools {

using gcs::kernel::ContextSnapshot;
using gcs::kernel::ModelSnapshot;
using gcs::kernel::ReportMessage;
using gcs::kernel::SolveStatus;

enum class FixtureKind {
    two_point_distance,
    unsatisfied_two_point_distance,
    two_component_distance,
    missing_entity_reference,
    under_constrained_free_point,
    over_constrained_duplicate_distance,
    redundant_distance_pair,
    inconsistent_distance_pair,
    singular_coincident_points,
    gluing_obstruction_pair,
};

enum class FixtureClass {
    valid,
    invalid,
    under_constrained,
    over_constrained,
    redundant,
    inconsistent,
    singular,
    gluing_obstruction,
};

struct FixtureBuildRequest {
    FixtureKind kind = FixtureKind::two_point_distance;
    int deterministic_seed = 0;
};

struct FixtureProvenance {
    std::string fixture_id;
    std::string fixture_class = "valid";
    std::string generator = "gcs.contract_tools";
    int deterministic_seed = 0;
    std::string schema_version = "gcs-0.3";
};

struct FixtureExpectation {
    SolveStatus expected_status = SolveStatus::not_run;
    std::vector<std::string> expected_report_codes;
    std::string evidence_phase = "unspecified";
};

struct FixtureBundle {
    ModelSnapshot model;
    ContextSnapshot whole_context;
    FixtureProvenance provenance;
    FixtureExpectation expectation;
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

struct CorpusGenerationRequest {
    std::vector<FixtureKind> fixture_kinds;
    int deterministic_seed = 0;
    bool include_negative = true;
};

struct GeneratedCorpus {
    std::vector<FixtureBundle> fixtures;
    GoldenReport golden_report;
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
ModelSnapshot make_under_constrained_free_point_model();
ModelSnapshot make_over_constrained_duplicate_distance_model();
ModelSnapshot make_redundant_distance_pair_model();
ModelSnapshot make_inconsistent_distance_pair_model();
ModelSnapshot make_singular_coincident_points_model();
ModelSnapshot make_gluing_obstruction_pair_model();
ContextSnapshot make_whole_context_for(const ModelSnapshot& model);
std::string to_string(FixtureKind kind);
std::string to_string(FixtureClass fixture_class);
gcs::kernel::ContractResult<FixtureBundle> build_fixture(FixtureBuildRequest request);
gcs::kernel::ContractResult<GeneratedCorpus> generate_corpus(
    CorpusGenerationRequest request);
gcs::kernel::ContractResult<InvariantReport> check_invariants(
    InvariantCheckRequest request);
gcs::kernel::ContractResult<GoldenReport> write_golden_report(GoldenReportRequest request);
gcs::kernel::ContractResult<DependencyAuditReport> audit_module_dependencies(
    DependencyAuditRequest request);

}
