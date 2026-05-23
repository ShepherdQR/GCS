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
using gcs::kernel::ReportMessage;
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

struct NumericTaskValidationReport {
    bool valid = true;
    bool context_version_matches = true;
    bool active_variables_exist = true;
    bool active_equations_exist = true;
    bool active_variables_within_context = true;
    bool active_equations_within_context = true;
    bool boundary_variables_are_active = true;
    bool tolerances_valid = true;
    bool solve_limits_valid = true;
    std::vector<ReportMessage> messages;
};

struct ResidualBlock {
    ConstraintId constraint_id;
    int offset = 0;
    int dimension = 0;
    std::vector<double> residuals;
};

struct EquationAssembly {
    bool valid = false;
    int variable_dimension = 0;
    int residual_dimension = 0;
    std::vector<EntityId> variable_order;
    std::vector<ConstraintId> equation_order;
    std::vector<double> residual_vector;
    std::vector<ResidualBlock> residual_blocks;
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

gcs::kernel::ContractResult<NumericTaskValidationReport> validate_task(
    const NumericTask& task);
gcs::kernel::ContractResult<EquationAssembly> assemble_equations(
    const NumericTask& task,
    const constraints::ConstraintCatalog& catalog);
gcs::kernel::ContractResult<EquationAssembly> assemble_equations(const NumericTask& task);
NumericReport solve_local(const NumericTask& task);

}
