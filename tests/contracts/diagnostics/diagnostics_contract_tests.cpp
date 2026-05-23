import gcs.contract_tools;
import gcs.diagnostics;
import gcs.kernel;
import gcs.numeric_engine;

#include <gtest/gtest.h>

#include <vector>

namespace {

namespace diagnostics = gcs::diagnostics;
namespace kernel = gcs::kernel;
namespace numeric = gcs::numeric;

numeric::NumericTask make_task_for_model(kernel::ModelSnapshot model) {
    auto context = gcs::tools::make_whole_context_for(model);
    return numeric::make_numeric_task(
        model,
        context,
        context.entity_ids,
        context.constraint_ids,
        kernel::GaugePolicy{});
}

diagnostics::DiagnosticOutput diagnose_after_local_solve(
    const kernel::ModelSnapshot& model,
    const numeric::NumericReport& numeric_report) {
    diagnostics::DiagnosticInput input;
    input.phase = diagnostics::DiagnosticPhase::post_local_solve;
    input.model = model;
    input.context = gcs::tools::make_whole_context_for(model);
    input.numeric_report = numeric_report;
    input.gauge_policy = kernel::GaugePolicy{};
    return diagnostics::diagnose(input);
}

bool has_evidence_code(const diagnostics::StatusPrecedenceTrace& trace,
                       const char* code) {
    for (const auto& evidence : trace.considered) {
        if (evidence.code == code) return true;
    }
    return false;
}

bool has_conflict_code(const diagnostics::GluingReport& report, const char* code) {
    for (const auto& conflict : report.conflict_sets) {
        if (conflict.code == code) return true;
    }
    return false;
}

kernel::LocalSection make_section(const kernel::ModelSnapshot& model,
                                  kernel::ContextId context_id,
                                  std::vector<kernel::EntityId> entity_ids) {
    kernel::LocalSection section;
    section.context_id = context_id;
    section.valid = true;
    section.entity_states = kernel::capture_entity_states(model, entity_ids);
    return section;
}

diagnostics::GluingInput make_projection_gluing_input(bool mismatch) {
    auto model = gcs::tools::make_two_point_distance_model();
    auto source = make_section(model, kernel::ContextId{1}, {kernel::EntityId{0}});
    auto target = make_section(model, kernel::ContextId{2}, {kernel::EntityId{0}});
    if (mismatch) {
        target.entity_states.front().parameters.values[0] += 1.0;
    }

    kernel::BoundaryProjection projection;
    projection.id = kernel::ProjectionId{7};
    projection.source_context_id = source.context_id;
    projection.target_context_id = target.context_id;
    projection.entity_ids = {kernel::EntityId{0}};
    projection.constraint_ids = {kernel::ConstraintId{0}};

    diagnostics::GluingInput input;
    input.model = model;
    input.local_sections = {source, target};
    input.boundary_projections = {projection};
    input.tolerances = model.tolerances;
    return input;
}

}  // namespace

TEST(DiagnosticsContract, DistinguishesStructuralDofFromNumericRank) {
    auto model = gcs::tools::make_two_point_distance_model();
    auto report = numeric::solve_local(make_task_for_model(model));

    auto output = diagnose_after_local_solve(model, report);

    EXPECT_EQ(output.status_code, kernel::SolveStatus::under_constrained);
    EXPECT_EQ(output.dof_report.parameter_dof, 6);
    EXPECT_EQ(output.dof_report.equation_dof, 1);
    EXPECT_EQ(output.dof_report.free_dof, 5);
    EXPECT_EQ(output.rank_report.structural_rank_estimate, 1);
    EXPECT_EQ(output.rank_report.numeric_rank_estimate, 1);
    EXPECT_EQ(output.rank_report.numeric_variable_dimension, 6);
    EXPECT_EQ(output.rank_report.numeric_residual_dimension, 1);
    EXPECT_EQ(output.rank_report.numeric_nullity_estimate, 5);
    EXPECT_TRUE(output.rank_report.numeric_under_constrained);
    EXPECT_TRUE(output.rank_report.condition_estimate_available);
}

TEST(DiagnosticsContract, PromotesNumericResidualBlocks) {
    auto model = gcs::tools::make_unsatisfied_two_point_distance_model();
    auto task = make_task_for_model(model);
    task.solve_limits.max_iterations = 0;
    auto report = numeric::solve_local(task);

    auto output = diagnose_after_local_solve(model, report);

    EXPECT_EQ(report.result_code, kernel::SolveStatus::failed);
    EXPECT_EQ(output.status_code, kernel::SolveStatus::failed);
    EXPECT_TRUE(output.residual_report.from_numeric_report);
    EXPECT_FALSE(output.residual_report.within_tolerance);
    EXPECT_EQ(output.residual_report.residual_dimension, 1);
    EXPECT_NEAR(output.residual_report.total_residual, 1.0, 1.0e-12);
    ASSERT_EQ(output.residual_report.constraints.size(), 1U);
    EXPECT_FALSE(output.residual_report.constraints.front().satisfied);
    EXPECT_EQ(output.residual_report.constraints.front().constraint_id.value, 0U);
    EXPECT_TRUE(has_evidence_code(output.status_precedence_trace,
                                  "diagnostics.numeric_result_status"));
    EXPECT_TRUE(has_evidence_code(output.status_precedence_trace,
                                  "diagnostics.residual_out_of_tolerance"));
}

TEST(DiagnosticsContract, StatusPrecedenceIsDeterministic) {
    auto result = diagnostics::resolve_status(
        diagnostics::StatusPrecedenceInput{
            {diagnostics::StatusEvidence{
                 kernel::SolveStatus::under_constrained,
                 "diagnostics.dof",
                 "under",
                 0},
             diagnostics::StatusEvidence{
                 kernel::SolveStatus::solved,
                 "diagnostics",
                 "solved",
                 0},
             diagnostics::StatusEvidence{
                 kernel::SolveStatus::invalid_model,
                 "kernel",
                 "invalid",
                 0}}});

    EXPECT_EQ(result.payload.resolved_status, kernel::SolveStatus::invalid_model);
    ASSERT_EQ(result.payload.considered.size(), 3U);
    EXPECT_EQ(result.payload.considered.front().priority, 60);
    EXPECT_EQ(result.payload.considered.back().priority, 100);
}

TEST(DiagnosticsContract, ConflictAndRedundancyPlaceholdersAreStructured) {
    auto model = gcs::tools::make_two_point_distance_model();
    auto report = numeric::solve_local(make_task_for_model(model));

    auto output = diagnose_after_local_solve(model, report);

    EXPECT_TRUE(output.conflict_sets.empty());
    EXPECT_TRUE(output.redundancy_sets.empty());
    EXPECT_FALSE(output.status_precedence_trace.considered.empty());
}

TEST(DiagnosticsContract, AcceptsCompatibleProjectedOverlap) {
    auto report = diagnostics::glue_local_sections(make_projection_gluing_input(false));

    EXPECT_TRUE(report.accepted);
    ASSERT_EQ(report.boundary_agreements.size(), 1U);
    EXPECT_TRUE(report.boundary_agreements.front().compatible);
    EXPECT_EQ(report.boundary_agreements.front().projection_id.value, 7U);
    EXPECT_NEAR(report.boundary_agreements.front().max_boundary_residual, 0.0, 1.0e-12);
    ASSERT_EQ(report.overlap_statuses.size(), 1U);
    EXPECT_TRUE(report.overlap_statuses.front().compatible);
}

TEST(DiagnosticsContract, RejectsMismatchedBoundaryProjection) {
    auto report = diagnostics::glue_local_sections(make_projection_gluing_input(true));

    EXPECT_FALSE(report.accepted);
    EXPECT_EQ(report.obstruction_report.code, "gluing.boundary_projection_mismatch");
    ASSERT_EQ(report.obstruction_report.projection_ids.size(), 1U);
    EXPECT_EQ(report.obstruction_report.projection_ids.front().value, 7U);
    ASSERT_EQ(report.obstruction_report.entity_ids.size(), 1U);
    EXPECT_EQ(report.obstruction_report.entity_ids.front().value, 0U);
    ASSERT_EQ(report.boundary_agreements.size(), 1U);
    EXPECT_FALSE(report.boundary_agreements.front().compatible);
    EXPECT_GT(report.boundary_agreements.front().max_boundary_residual, 0.0);
    EXPECT_TRUE(has_conflict_code(report, "gluing.boundary_projection_mismatch"));
}
