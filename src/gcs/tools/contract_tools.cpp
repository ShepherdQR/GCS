module;

#include <cstdint>
#include <iomanip>
#include <sstream>
#include <string>
#include <utility>

module gcs.contract_tools;

import gcs.kernel;

namespace gcs::tools {

namespace kernel = gcs::kernel;

namespace {

std::string fixture_id(FixtureKind kind) {
    switch (kind) {
        case FixtureKind::two_point_distance: return "two_point_distance";
        case FixtureKind::unsatisfied_two_point_distance:
            return "unsatisfied_two_point_distance";
        case FixtureKind::two_component_distance: return "two_component_distance";
        case FixtureKind::missing_entity_reference: return "missing_entity_reference";
    }
    return "unknown";
}

std::uint64_t fnv1a64(const std::string& bytes) {
    std::uint64_t hash = 1469598103934665603ULL;
    for (unsigned char byte : bytes) {
        hash ^= static_cast<std::uint64_t>(byte);
        hash *= 1099511628211ULL;
    }
    return hash;
}

std::string digest_hex(const std::string& bytes) {
    std::ostringstream output;
    output << std::hex << std::setw(16) << std::setfill('0') << fnv1a64(bytes);
    return output.str();
}

std::string golden_summary(const FixtureBundle& fixture) {
    std::ostringstream output;
    output << fixture.provenance.fixture_id << "|"
           << fixture.provenance.generator << "|"
           << fixture.provenance.deterministic_seed << "|"
           << fixture.model.schema_version << "|"
           << fixture.model.entities.size() << "|"
           << fixture.model.constraints.size() << "|"
           << fixture.whole_context.entity_ids.size() << "|"
           << fixture.whole_context.constraint_ids.size();
    return output.str();
}

bool is_lower_solver_module(const std::string& module) {
    return module == "gcs.kernel" ||
           module == "gcs.constraint_catalog" ||
           module == "gcs.incidence_graph" ||
           module == "gcs.decomposition_planner" ||
           module == "gcs.numeric_engine" ||
           module == "gcs.diagnostics";
}

bool is_boundary_or_runtime_module(const std::string& imported_module) {
    return imported_module == "gcs.session_runtime" ||
           imported_module == "gcs.io_adapters" ||
           imported_module == "gcs.viewer_bridge";
}

}  // namespace

ModelSnapshot make_two_point_distance_model() {
    ModelSnapshot model;
    model.rigid_sets.push_back(
        kernel::RigidSetDraft{kernel::RigidSetId{0}, {kernel::EntityId{0}}});
    model.rigid_sets.push_back(
        kernel::RigidSetDraft{kernel::RigidSetId{1}, {kernel::EntityId{1}}});

    kernel::EntityDraft first;
    first.id = kernel::EntityId{0};
    first.kind = kernel::GeometryKind::point;
    first.rigid_set_id = kernel::RigidSetId{0};
    first.parameters.dimension = kernel::geometry_dof(first.kind);
    first.parameters.values[0] = 0.0;
    first.parameters.values[1] = 0.0;
    first.parameters.values[2] = 0.0;

    kernel::EntityDraft second;
    second.id = kernel::EntityId{1};
    second.kind = kernel::GeometryKind::point;
    second.rigid_set_id = kernel::RigidSetId{1};
    second.parameters.dimension = kernel::geometry_dof(second.kind);
    second.parameters.values[0] = 1.0;
    second.parameters.values[1] = 0.0;
    second.parameters.values[2] = 0.0;

    model.entities.push_back(first);
    model.entities.push_back(second);

    kernel::ConstraintDraft distance;
    distance.id = kernel::ConstraintId{0};
    distance.kind = kernel::ConstraintKind::distance;
    distance.entity_ids = {kernel::EntityId{0}, kernel::EntityId{1}};
    distance.value = 1.0;
    model.constraints.push_back(distance);
    return model;
}

ModelSnapshot make_unsatisfied_two_point_distance_model() {
    ModelSnapshot model = make_two_point_distance_model();
    model.entities[1].parameters.values[0] = 2.0;
    return model;
}

ModelSnapshot make_two_component_distance_model() {
    ModelSnapshot model = make_two_point_distance_model();

    model.rigid_sets.push_back(
        kernel::RigidSetDraft{kernel::RigidSetId{2}, {kernel::EntityId{2}}});
    model.rigid_sets.push_back(
        kernel::RigidSetDraft{kernel::RigidSetId{3}, {kernel::EntityId{3}}});

    kernel::EntityDraft third;
    third.id = kernel::EntityId{2};
    third.kind = kernel::GeometryKind::point;
    third.rigid_set_id = kernel::RigidSetId{2};
    third.parameters.dimension = kernel::geometry_dof(third.kind);
    third.parameters.values[0] = 10.0;

    kernel::EntityDraft fourth;
    fourth.id = kernel::EntityId{3};
    fourth.kind = kernel::GeometryKind::point;
    fourth.rigid_set_id = kernel::RigidSetId{3};
    fourth.parameters.dimension = kernel::geometry_dof(fourth.kind);
    fourth.parameters.values[0] = 11.0;

    model.entities.push_back(third);
    model.entities.push_back(fourth);

    kernel::ConstraintDraft second_distance;
    second_distance.id = kernel::ConstraintId{1};
    second_distance.kind = kernel::ConstraintKind::distance;
    second_distance.entity_ids = {kernel::EntityId{2}, kernel::EntityId{3}};
    second_distance.value = 1.0;
    model.constraints.push_back(second_distance);
    return model;
}

ModelSnapshot make_missing_entity_reference_model() {
    ModelSnapshot model = make_two_point_distance_model();
    model.constraints.push_back(kernel::ConstraintDraft{
        kernel::ConstraintId{7},
        kernel::ConstraintKind::distance,
        {kernel::EntityId{0}, kernel::EntityId{999}},
        1.0});
    return model;
}

ContextSnapshot make_whole_context_for(const ModelSnapshot& model) {
    return kernel::make_whole_model_context(model);
}

gcs::kernel::ContractResult<FixtureBundle> build_fixture(FixtureBuildRequest request) {
    kernel::ContractResult<FixtureBundle> result;
    result.report = kernel::make_stage_report("contract_tools.build_fixture");

    switch (request.kind) {
        case FixtureKind::two_point_distance:
            result.payload.model = make_two_point_distance_model();
            break;
        case FixtureKind::unsatisfied_two_point_distance:
            result.payload.model = make_unsatisfied_two_point_distance_model();
            break;
        case FixtureKind::two_component_distance:
            result.payload.model = make_two_component_distance_model();
            break;
        case FixtureKind::missing_entity_reference:
            result.payload.model = make_missing_entity_reference_model();
            break;
    }

    result.payload.whole_context = make_whole_context_for(result.payload.model);
    result.payload.provenance.fixture_id = fixture_id(request.kind);
    result.payload.provenance.deterministic_seed = request.deterministic_seed;
    result.payload.provenance.schema_version = result.payload.model.schema_version;
    return result;
}

gcs::kernel::ContractResult<InvariantReport> check_invariants(
    InvariantCheckRequest request) {
    kernel::ContractResult<InvariantReport> result;
    result.report = kernel::make_stage_report("contract_tools.check_invariants");

    auto model_validation = kernel::validate_model(request.model);
    auto context_validation = kernel::validate_context(request.model, request.context);

    result.payload.entity_count = static_cast<int>(request.model.entities.size());
    result.payload.constraint_count = static_cast<int>(request.model.constraints.size());
    result.payload.context_entity_count =
        static_cast<int>(request.context.entity_ids.size());
    result.payload.context_constraint_count =
        static_cast<int>(request.context.constraint_ids.size());

    for (auto message : model_validation.report.messages) {
        result.payload.messages.push_back(message);
        kernel::append_report_message(result.report, std::move(message));
    }
    for (auto message : context_validation.report.messages) {
        result.payload.messages.push_back(message);
        kernel::append_report_message(result.report, std::move(message));
    }
    result.payload.valid = model_validation.payload.valid &&
                           context_validation.payload.valid;
    return result;
}

gcs::kernel::ContractResult<GoldenReport> write_golden_report(GoldenReportRequest request) {
    kernel::ContractResult<GoldenReport> result;
    result.report = kernel::make_stage_report("contract_tools.write_golden_report");

    result.payload.report_name = std::move(request.report_name);
    result.payload.canonical_summary = golden_summary(request.fixture);
    result.payload.digest = digest_hex(result.payload.canonical_summary);
    return result;
}

gcs::kernel::ContractResult<DependencyAuditReport> audit_module_dependencies(
    DependencyAuditRequest request) {
    kernel::ContractResult<DependencyAuditReport> result;
    result.report = kernel::make_stage_report("contract_tools.audit_module_dependencies");

    for (const auto& import : request.imports) {
        if (is_lower_solver_module(import.module) &&
            is_boundary_or_runtime_module(import.imported_module)) {
            result.payload.valid = false;
            result.payload.violations.push_back(
                DependencyViolation{
                    import.module,
                    import.imported_module,
                    "tools.dependency.forbidden_boundary_import"});
            kernel::append_report_message(
                result.report,
                kernel::make_report_message(
                    kernel::ReportSeverity::error,
                    kernel::ReportCode{"tools.dependency.forbidden_boundary_import"},
                    "Lower solver modules must not import runtime, IO, or viewer boundaries."));
        }
    }

    return result;
}

}
