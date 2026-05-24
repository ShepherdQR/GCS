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
using gcs::kernel::ParameterVector;
using gcs::kernel::ProposedState;
using gcs::kernel::ReportMessage;
using gcs::kernel::SolveStatus;
using gcs::kernel::StageReport;
using gcs::kernel::StateVersionId;
using gcs::kernel::TolerancePolicy;

struct SolveLimits {
    int max_iterations = 25;
    double trust_region_radius = 1.0;
    double damping = 1.0e-6;
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
    bool active_equation_entities_are_active = true;
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
    double norm = 0.0;
    double max_abs_value = 0.0;
};

struct ResidualReport {
    int dimension = 0;
    double norm = 0.0;
    double max_abs_value = 0.0;
    std::vector<ResidualBlock> blocks;
};

struct JacobianBlock {
    ConstraintId constraint_id;
    int row_offset = 0;
    int row_count = 0;
    int column_offset = 0;
    int column_count = 0;
    std::vector<EntityId> entity_ids;
    std::vector<int> entity_column_offsets;
    std::vector<int> entity_parameter_dimensions;
    std::vector<double> values;
};

struct JacobianReport {
    bool valid = false;
    int row_count = 0;
    int column_count = 0;
    std::vector<JacobianBlock> blocks;
    std::vector<double> values;
};

struct EquationAssembly {
    bool valid = false;
    int variable_dimension = 0;
    int residual_dimension = 0;
    std::vector<EntityId> variable_order;
    std::vector<ConstraintId> equation_order;
    std::vector<double> residual_vector;
    std::vector<ResidualBlock> residual_blocks;
    JacobianReport jacobian_report;
};

struct RankConditionReport {
    int variable_dimension = 0;
    int free_variable_dimension = 0;
    int frozen_variable_dimension = 0;
    int residual_dimension = 0;
    int rank_estimate = 0;
    int nullity_estimate = 0;
    bool under_constrained = false;
    bool over_constrained = false;
    bool numerically_singular = false;
    bool condition_estimate_available = false;
    double condition_estimate = 0.0;
};

struct BoundaryVariableReport {
    EntityId entity_id;
    bool active = false;
    bool unchanged = true;
    ParameterVector before;
    ParameterVector after;
};

struct IterationTraceEntry {
    int iteration = 0;
    std::string phase;
    double residual_norm = 0.0;
    double step_norm = 0.0;
    bool accepted = false;
};

struct IterationTrace {
    StateVersionId base_version;
    std::vector<IterationTraceEntry> entries;
};

struct NumericReport {
    SolveStatus result_code = SolveStatus::not_run;
    LocalSection local_section;
    ProposedState proposed_state;
    EquationAssembly equation_assembly;
    ResidualReport residual_report;
    RankConditionReport rank_condition_report;
    std::vector<BoundaryVariableReport> boundary_variables;
    IterationTrace iteration_trace;
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
