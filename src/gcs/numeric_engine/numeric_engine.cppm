module;

#include <string>
#include <vector>

export module gcs.numeric_engine;

export import gcs.kernel;
export import gcs.constraint_catalog;

export namespace gcs::numeric {

using gcs::kernel::ConstraintId;
using gcs::kernel::ContextSnapshot;
using gcs::kernel::EntityId;
using gcs::kernel::GaugePolicy;
using gcs::kernel::LocalSection;
using gcs::kernel::ModelSnapshot;
using gcs::kernel::ProposedState;
using gcs::kernel::SolveStatus;
using gcs::kernel::StageReport;
using gcs::kernel::TolerancePolicy;

struct SolveLimits {
    int max_iterations = 25;
    double trust_region_radius = 1.0;
};

struct NumericTask {
    ModelSnapshot problem_snapshot;
    ContextSnapshot context_snapshot;
    std::vector<EntityId> active_variables;
    std::vector<ConstraintId> active_equations;
    std::vector<EntityId> boundary_variables;
    std::string parameterization = "default-manifold-retraction";
    TolerancePolicy tolerances;
    GaugePolicy gauge_policy;
    SolveLimits solve_limits;
};

struct NumericReport {
    SolveStatus result_code = SolveStatus::not_run;
    LocalSection local_section;
    ProposedState proposed_state;
    double initial_residual = 0.0;
    double final_residual = 0.0;
    double step_norm = 0.0;
    int rank_estimate = 0;
    double condition_estimate = 0.0;
    int iteration_count = 0;
    std::string failure_cause;
    StageReport stage_report;
};

NumericTask make_numeric_task(const ModelSnapshot& model,
                              const ContextSnapshot& context,
                              const std::vector<EntityId>& active_variables,
                              const std::vector<ConstraintId>& active_equations,
                              const GaugePolicy& gauge_policy);

NumericReport solve_local(const NumericTask& task);

}
