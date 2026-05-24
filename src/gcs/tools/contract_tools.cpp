module;

#include <cstdint>
#include <iomanip>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

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
        case FixtureKind::under_constrained_free_point:
            return "under_constrained_free_point";
        case FixtureKind::over_constrained_duplicate_distance:
            return "over_constrained_duplicate_distance";
        case FixtureKind::redundant_distance_pair: return "redundant_distance_pair";
        case FixtureKind::inconsistent_distance_pair: return "inconsistent_distance_pair";
        case FixtureKind::singular_coincident_points: return "singular_coincident_points";
        case FixtureKind::gluing_obstruction_pair: return "gluing_obstruction_pair";
        case FixtureKind::boundary_frozen_distance: return "boundary_frozen_distance";
        case FixtureKind::tolerated_multi_residual_distance:
            return "tolerated_multi_residual_distance";
        case FixtureKind::separator_chain_distance: return "separator_chain_distance";
    }
    return "unknown";
}

FixtureClass fixture_class(FixtureKind kind) {
    switch (kind) {
        case FixtureKind::two_point_distance:
        case FixtureKind::unsatisfied_two_point_distance:
        case FixtureKind::two_component_distance:
            return FixtureClass::valid;
        case FixtureKind::missing_entity_reference: return FixtureClass::invalid;
        case FixtureKind::under_constrained_free_point:
            return FixtureClass::under_constrained;
        case FixtureKind::over_constrained_duplicate_distance:
            return FixtureClass::over_constrained;
        case FixtureKind::redundant_distance_pair: return FixtureClass::redundant;
        case FixtureKind::inconsistent_distance_pair: return FixtureClass::inconsistent;
        case FixtureKind::singular_coincident_points: return FixtureClass::singular;
        case FixtureKind::gluing_obstruction_pair:
            return FixtureClass::gluing_obstruction;
        case FixtureKind::boundary_frozen_distance:
            return FixtureClass::boundary_frozen;
        case FixtureKind::tolerated_multi_residual_distance:
            return FixtureClass::tolerance_edge;
        case FixtureKind::separator_chain_distance:
            return FixtureClass::separator;
    }
    return FixtureClass::invalid;
}

FixtureExpectation fixture_expectation(FixtureKind kind) {
    FixtureExpectation expectation;
    switch (kind) {
        case FixtureKind::two_point_distance:
        case FixtureKind::two_component_distance:
            expectation.expected_status = kernel::SolveStatus::solved;
            expectation.evidence_phase = "kernel.validation";
            break;
        case FixtureKind::unsatisfied_two_point_distance:
            expectation.expected_status = kernel::SolveStatus::inconsistent;
            expectation.expected_report_codes = {"diagnostics.residual_conflict"};
            expectation.evidence_phase = "diagnostics.residual_analysis";
            break;
        case FixtureKind::missing_entity_reference:
            expectation.expected_status = kernel::SolveStatus::invalid_model;
            expectation.expected_report_codes = {"kernel.missing_entity"};
            expectation.evidence_phase = "kernel.validation";
            break;
        case FixtureKind::under_constrained_free_point:
            expectation.expected_status = kernel::SolveStatus::under_constrained;
            expectation.expected_report_codes = {"diagnostics.numeric_rank_under_constrained"};
            expectation.evidence_phase = "diagnostics.rank";
            break;
        case FixtureKind::over_constrained_duplicate_distance:
            expectation.expected_status = kernel::SolveStatus::over_constrained;
            expectation.expected_report_codes = {
                "diagnostics.overconstrained_redundancy_candidate"};
            expectation.evidence_phase = "diagnostics.redundancy";
            break;
        case FixtureKind::redundant_distance_pair:
            expectation.expected_status = kernel::SolveStatus::redundant;
            expectation.expected_report_codes = {
                "diagnostics.redundant_duplicate_distance"};
            expectation.evidence_phase = "diagnostics.redundancy";
            break;
        case FixtureKind::inconsistent_distance_pair:
            expectation.expected_status = kernel::SolveStatus::inconsistent;
            expectation.expected_report_codes = {"diagnostics.residual_conflict"};
            expectation.evidence_phase = "diagnostics.residual_analysis";
            break;
        case FixtureKind::singular_coincident_points:
            expectation.expected_status = kernel::SolveStatus::numerically_singular;
            expectation.expected_report_codes = {
                "constraint.degenerate_zero_distance_direction"};
            expectation.evidence_phase = "constraint_catalog.residual";
            break;
        case FixtureKind::gluing_obstruction_pair:
            expectation.expected_status = kernel::SolveStatus::inconsistent;
            expectation.expected_report_codes = {
                "gluing.boundary_projection_mismatch"};
            expectation.evidence_phase = "diagnostics.gluing";
            break;
        case FixtureKind::boundary_frozen_distance:
            expectation.expected_status = kernel::SolveStatus::under_constrained;
            expectation.expected_report_codes = {
                "diagnostics.numeric_rank_under_constrained"};
            expectation.evidence_phase = "numeric.boundary_frozen_rank";
            break;
        case FixtureKind::tolerated_multi_residual_distance:
            expectation.expected_status = kernel::SolveStatus::solved;
            expectation.evidence_phase = "numeric.max_abs_residual_tolerance";
            break;
        case FixtureKind::separator_chain_distance:
            expectation.expected_status = kernel::SolveStatus::under_constrained;
            expectation.evidence_phase = "decomposition.separator_chain";
            break;
    }
    return expectation;
}

std::vector<FixtureKind> default_fixture_kinds(bool include_negative) {
    std::vector<FixtureKind> kinds = {
        FixtureKind::two_point_distance,
        FixtureKind::two_component_distance,
        FixtureKind::boundary_frozen_distance,
        FixtureKind::tolerated_multi_residual_distance,
        FixtureKind::separator_chain_distance,
    };
    if (!include_negative) return kinds;
    kinds.push_back(FixtureKind::unsatisfied_two_point_distance);
    kinds.push_back(FixtureKind::missing_entity_reference);
    kinds.push_back(FixtureKind::under_constrained_free_point);
    kinds.push_back(FixtureKind::over_constrained_duplicate_distance);
    kinds.push_back(FixtureKind::redundant_distance_pair);
    kinds.push_back(FixtureKind::inconsistent_distance_pair);
    kinds.push_back(FixtureKind::singular_coincident_points);
    kinds.push_back(FixtureKind::gluing_obstruction_pair);
    return kinds;
}

kernel::EntityDraft make_point(std::uint64_t entity_id,
                               std::uint64_t rigid_set_id,
                               double x,
                               double y,
                               double z) {
    kernel::EntityDraft point;
    point.id = kernel::EntityId{entity_id};
    point.kind = kernel::GeometryKind::point;
    point.rigid_set_id = kernel::RigidSetId{rigid_set_id};
    point.parameters.dimension = kernel::geometry_dof(point.kind);
    point.parameters.values[0] = x;
    point.parameters.values[1] = y;
    point.parameters.values[2] = z;
    return point;
}

kernel::ConstraintDraft make_distance(std::uint64_t constraint_id,
                                      std::uint64_t first_entity_id,
                                      std::uint64_t second_entity_id,
                                      double value) {
    kernel::ConstraintDraft distance;
    distance.id = kernel::ConstraintId{constraint_id};
    distance.kind = kernel::ConstraintKind::distance;
    distance.entity_ids = {
        kernel::EntityId{first_entity_id},
        kernel::EntityId{second_entity_id},
    };
    distance.value = value;
    return distance;
}

std::string join_report_codes(const std::vector<std::string>& codes) {
    std::ostringstream output;
    for (std::size_t index = 0; index < codes.size(); ++index) {
        if (index != 0) output << ",";
        output << codes[index];
    }
    return output.str();
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
           << fixture.provenance.fixture_class << "|"
           << fixture.provenance.generator << "|"
           << fixture.provenance.deterministic_seed << "|"
           << fixture.model.schema_version << "|"
           << kernel::to_string(fixture.expectation.expected_status) << "|"
           << fixture.expectation.evidence_phase << "|"
           << join_report_codes(fixture.expectation.expected_report_codes) << "|"
           << fixture.model.entities.size() << "|"
           << fixture.model.constraints.size() << "|"
           << fixture.whole_context.entity_ids.size() << "|"
           << fixture.whole_context.constraint_ids.size();
    return output.str();
}

std::string corpus_summary(const std::vector<FixtureBundle>& fixtures, int seed) {
    std::ostringstream output;
    output << "fixture_corpus|gcs.contract_tools|" << seed << "|"
           << fixtures.size();
    for (const auto& fixture : fixtures) {
        output << "\n" << golden_summary(fixture);
    }
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

ModelSnapshot make_under_constrained_free_point_model() {
    ModelSnapshot model;
    model.rigid_sets.push_back(
        kernel::RigidSetDraft{kernel::RigidSetId{0}, {kernel::EntityId{0}}});
    model.entities.push_back(make_point(0, 0, 0.0, 0.0, 0.0));
    return model;
}

ModelSnapshot make_over_constrained_duplicate_distance_model() {
    ModelSnapshot model = make_two_point_distance_model();
    for (std::uint64_t constraint_id = 1; constraint_id < 7; ++constraint_id) {
        model.constraints.push_back(make_distance(constraint_id, 0, 1, 1.0));
    }
    return model;
}

ModelSnapshot make_redundant_distance_pair_model() {
    ModelSnapshot model = make_two_point_distance_model();
    model.constraints.push_back(make_distance(1, 0, 1, 1.0));
    return model;
}

ModelSnapshot make_inconsistent_distance_pair_model() {
    ModelSnapshot model = make_two_point_distance_model();
    model.constraints.push_back(make_distance(1, 0, 1, 2.0));
    return model;
}

ModelSnapshot make_singular_coincident_points_model() {
    ModelSnapshot model = make_two_point_distance_model();
    model.entities[1].parameters.values[0] = 0.0;
    model.constraints[0].value = 0.0;
    return model;
}

ModelSnapshot make_gluing_obstruction_pair_model() {
    return make_two_point_distance_model();
}

ModelSnapshot make_boundary_frozen_distance_model() {
    ModelSnapshot model = make_two_point_distance_model();
    model.solve_intent.fixed_entity_ids = {kernel::EntityId{0}};
    return model;
}

ModelSnapshot make_tolerated_multi_residual_distance_model() {
    ModelSnapshot model = make_two_component_distance_model();
    model.entities[1].parameters.values[0] = 1.0 + 0.75e-8;
    model.entities[3].parameters.values[0] = 11.0 + 0.75e-8;
    return model;
}

ModelSnapshot make_separator_chain_distance_model() {
    ModelSnapshot model;
    model.rigid_sets.push_back(
        kernel::RigidSetDraft{kernel::RigidSetId{0}, {kernel::EntityId{0}}});
    model.rigid_sets.push_back(
        kernel::RigidSetDraft{kernel::RigidSetId{1}, {kernel::EntityId{1}}});
    model.rigid_sets.push_back(
        kernel::RigidSetDraft{kernel::RigidSetId{2}, {kernel::EntityId{2}}});

    model.entities.push_back(make_point(0, 0, 0.0, 0.0, 0.0));
    model.entities.push_back(make_point(1, 1, 1.0, 0.0, 0.0));
    model.entities.push_back(make_point(2, 2, 2.0, 0.0, 0.0));

    model.constraints.push_back(make_distance(0, 0, 1, 1.0));
    model.constraints.push_back(make_distance(1, 1, 2, 1.0));
    return model;
}

ContextSnapshot make_whole_context_for(const ModelSnapshot& model) {
    return kernel::make_whole_model_context(model);
}

std::string to_string(FixtureKind kind) {
    return fixture_id(kind);
}

std::string to_string(FixtureClass fixture_class) {
    switch (fixture_class) {
        case FixtureClass::valid: return "valid";
        case FixtureClass::invalid: return "invalid";
        case FixtureClass::under_constrained: return "under_constrained";
        case FixtureClass::over_constrained: return "over_constrained";
        case FixtureClass::redundant: return "redundant";
        case FixtureClass::inconsistent: return "inconsistent";
        case FixtureClass::singular: return "singular";
        case FixtureClass::gluing_obstruction: return "gluing_obstruction";
        case FixtureClass::boundary_frozen: return "boundary_frozen";
        case FixtureClass::tolerance_edge: return "tolerance_edge";
        case FixtureClass::separator: return "separator";
    }
    return "unknown";
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
        case FixtureKind::under_constrained_free_point:
            result.payload.model = make_under_constrained_free_point_model();
            break;
        case FixtureKind::over_constrained_duplicate_distance:
            result.payload.model = make_over_constrained_duplicate_distance_model();
            break;
        case FixtureKind::redundant_distance_pair:
            result.payload.model = make_redundant_distance_pair_model();
            break;
        case FixtureKind::inconsistent_distance_pair:
            result.payload.model = make_inconsistent_distance_pair_model();
            break;
        case FixtureKind::singular_coincident_points:
            result.payload.model = make_singular_coincident_points_model();
            break;
        case FixtureKind::gluing_obstruction_pair:
            result.payload.model = make_gluing_obstruction_pair_model();
            break;
        case FixtureKind::boundary_frozen_distance:
            result.payload.model = make_boundary_frozen_distance_model();
            break;
        case FixtureKind::tolerated_multi_residual_distance:
            result.payload.model = make_tolerated_multi_residual_distance_model();
            break;
        case FixtureKind::separator_chain_distance:
            result.payload.model = make_separator_chain_distance_model();
            break;
    }

    result.payload.whole_context = make_whole_context_for(result.payload.model);
    result.payload.provenance.fixture_id = fixture_id(request.kind);
    result.payload.provenance.fixture_class =
        to_string(fixture_class(request.kind));
    result.payload.provenance.deterministic_seed = request.deterministic_seed;
    result.payload.provenance.schema_version = result.payload.model.schema_version;
    result.payload.expectation = fixture_expectation(request.kind);
    return result;
}

gcs::kernel::ContractResult<GeneratedCorpus> generate_corpus(
    CorpusGenerationRequest request) {
    kernel::ContractResult<GeneratedCorpus> result;
    result.report = kernel::make_stage_report("contract_tools.generate_corpus");

    std::vector<FixtureKind> kinds = request.fixture_kinds.empty()
                                        ? default_fixture_kinds(request.include_negative)
                                        : std::move(request.fixture_kinds);

    for (std::size_t index = 0; index < kinds.size(); ++index) {
        auto fixture = build_fixture(
            FixtureBuildRequest{kinds[index],
                                request.deterministic_seed + static_cast<int>(index)});
        result.payload.fixtures.push_back(std::move(fixture.payload));
        for (auto message : fixture.report.messages) {
            kernel::append_report_message(result.report, std::move(message));
        }
    }

    result.payload.golden_report.report_name = "fixture_corpus";
    result.payload.golden_report.canonical_summary =
        corpus_summary(result.payload.fixtures, request.deterministic_seed);
    result.payload.golden_report.digest =
        digest_hex(result.payload.golden_report.canonical_summary);
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
