module;

#include <optional>
#include <string>
#include <vector>

export module gcs.diagnostics;

export import gcs.kernel;
export import gcs.numeric_engine;

export namespace gcs::diagnostics {

using gcs::kernel::BoundaryProjection;
using gcs::kernel::ConstraintId;
using gcs::kernel::ContextId;
using gcs::kernel::ContextSnapshot;
using gcs::kernel::CoverPlan;
using gcs::kernel::EntityId;
using gcs::kernel::GaugePolicy;
using gcs::kernel::LocalSection;
using gcs::kernel::ModelSnapshot;
using gcs::kernel::ProjectionId;
using gcs::kernel::ProposedState;
using gcs::kernel::ReportMessage;
using gcs::kernel::SolveStatus;
using gcs::kernel::StageReport;
using gcs::kernel::TolerancePolicy;

struct DofReport {
    int parameter_dof = 0;
    int equation_dof = 0;
    int gauge_dof = 0;
    int free_dof = 0;
    SolveStatus status = SolveStatus::not_run;
};

struct RankReport {
    int structural_rank_estimate = 0;
    int numeric_rank_estimate = 0;
    double condition_estimate = 0.0;
};

struct ConstraintResidual {
    ConstraintId constraint_id;
    double residual = 0.0;
    double tolerance = 0.0;
    bool satisfied = true;
};

struct ResidualReport {
    double total_residual = 0.0;
    double max_residual = 0.0;
    std::vector<ConstraintResidual> constraints;
};

struct ObstructionReport {
    bool present = false;
    std::string code;
    std::string message;
    std::vector<ContextId> context_ids;
    std::vector<EntityId> entity_ids;
    std::vector<ConstraintId> constraint_ids;
};

struct OverlapStatus {
    ProjectionId projection_id;
    bool compatible = true;
    double boundary_residual = 0.0;
    std::vector<EntityId> entity_ids;
};

struct GluingInput {
    ModelSnapshot model;
    CoverPlan cover_plan;
    std::vector<LocalSection> local_sections;
    std::vector<BoundaryProjection> boundary_projections;
    GaugePolicy gauge_policy;
    TolerancePolicy tolerances;
};

struct GluingReport {
    bool accepted = false;
    ProposedState proposed_global_state;
    std::vector<OverlapStatus> overlap_statuses;
    bool gauge_consistent = true;
    ObstructionReport obstruction_report;
    StageReport stage_report;
};

struct DiagnosticInput {
    ModelSnapshot model;
    std::optional<ContextSnapshot> context;
    std::optional<numeric::NumericReport> numeric_report;
    GaugePolicy gauge_policy;
};

struct DiagnosticOutput {
    SolveStatus status_code = SolveStatus::not_run;
    DofReport dof_report;
    RankReport rank_report;
    ResidualReport residual_report;
    GluingReport gluing_report;
    ObstructionReport obstruction_report;
    std::vector<ReportMessage> warnings;
};

DofReport analyze_dof(const ModelSnapshot& model,
                      const ContextSnapshot& context,
                      const GaugePolicy& gauge_policy);
DiagnosticOutput diagnose(const DiagnosticInput& input);
GluingReport glue_local_sections(const GluingInput& input);
ObstructionReport make_obstruction(std::string code, std::string message);

}
