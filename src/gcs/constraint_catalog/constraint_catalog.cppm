module;

#include <string>
#include <vector>

export module gcs.constraint_catalog;

export import gcs.kernel;

export namespace gcs::constraints {

using gcs::kernel::ConstraintDraft;
using gcs::kernel::ConstraintId;
using gcs::kernel::ConstraintKind;
using gcs::kernel::EntityId;
using gcs::kernel::GeometryKind;
using gcs::kernel::ModelSnapshot;
using gcs::kernel::ReportMessage;
using gcs::kernel::StageReport;

enum class ConstraintParameterKind {
    none,
    length,
    angle_radians,
};

enum class ConstraintEvaluatorPolicy {
    algebraic,
    finite_difference_baseline,
};

struct EntitySignatureTerm {
    std::string role;
    std::vector<GeometryKind> allowed_kinds;
    bool requires_nonzero_direction = false;
};

struct ConstraintParameterSchema {
    ConstraintParameterKind kind = ConstraintParameterKind::none;
    bool scalar_required = false;
    double default_value = 0.0;
    double min_value = 0.0;
    double max_value = 0.0;
};

struct ConstraintDefinition {
    ConstraintKind kind = ConstraintKind::coincident;
    std::string name;
    std::string catalog_version = "builtin-0.1";
    int min_entity_count = 0;
    int max_entity_count = 0;
    int residual_dimension = 0;
    int generic_dof_effect = 0;
    bool requires_distinct_rigid_sets = true;
    ConstraintParameterSchema parameter_schema;
    std::vector<EntitySignatureTerm> entity_signature;
    ConstraintEvaluatorPolicy evaluator_policy = ConstraintEvaluatorPolicy::finite_difference_baseline;
    std::vector<std::string> degeneracy_codes;
};

struct ConstraintCatalog {
    std::string version = "builtin-0.1";
    std::vector<ConstraintDefinition> definitions;
};

struct ConstraintValidationInput {
    ModelSnapshot model;
    ConstraintDraft constraint;
};

struct ConstraintValidationReport {
    bool valid = false;
    ConstraintDefinition definition;
    std::vector<ReportMessage> messages;
};

using ConstraintValidationResult = ConstraintValidationReport;

struct ResidualEvaluationRequest {
    ModelSnapshot model;
    ConstraintId constraint_id;
};

struct DegeneracyProbeRequest {
    ModelSnapshot model;
    ConstraintId constraint_id;
};

struct DegeneracyReport {
    bool degenerate = false;
    std::string code;
    std::string message;
    std::vector<EntityId> entity_ids;
    std::vector<ConstraintId> constraint_ids;
};

struct ResidualEvaluationResult {
    bool valid = false;
    ConstraintDefinition definition;
    std::vector<double> residuals;
    DegeneracyReport degeneracy_report;
};

struct JacobianEvaluationRequest {
    ModelSnapshot model;
    ConstraintId constraint_id;
    double finite_difference_step = 1.0e-6;
};

struct JacobianEvaluationResult {
    bool valid = false;
    ConstraintDefinition definition;
    int row_count = 0;
    int column_count = 0;
    std::vector<EntityId> entity_ids;
    std::vector<int> entity_parameter_dimensions;
    std::vector<double> values;
    DegeneracyReport degeneracy_report;
};

struct FiniteDifferenceCheckRequest {
    ModelSnapshot model;
    ConstraintId constraint_id;
    double finite_difference_step = 1.0e-6;
    double tolerance = 1.0e-6;
};

struct JacobianCheckReport {
    bool valid = false;
    bool passed = false;
    double max_abs_error = 0.0;
    JacobianEvaluationResult analytic_jacobian;
    JacobianEvaluationResult finite_difference_jacobian;
};

const ConstraintCatalog& builtin_catalog();
const std::vector<ConstraintDefinition>& builtin_definitions();
const ConstraintDefinition* find_definition(const ConstraintCatalog& catalog,
                                            ConstraintKind kind);
const ConstraintDefinition* find_definition(ConstraintKind kind);
int residual_dimension(ConstraintKind kind);
int generic_dof_effect(ConstraintKind kind);

ConstraintValidationResult validate_constraint(const ConstraintValidationInput& input);
gcs::kernel::ContractResult<ConstraintValidationReport> validate_constraint(
    const ConstraintCatalog& catalog,
    const ModelSnapshot& snapshot,
    ConstraintId constraint_id);
StageReport validate_model_constraints(const ModelSnapshot& model);

gcs::kernel::ContractResult<DegeneracyReport> probe_degeneracy(
    const ConstraintCatalog& catalog,
    DegeneracyProbeRequest request);
gcs::kernel::ContractResult<ResidualEvaluationResult> evaluate_residual(
    const ConstraintCatalog& catalog,
    ResidualEvaluationRequest request);
gcs::kernel::ContractResult<JacobianEvaluationResult> evaluate_jacobian(
    const ConstraintCatalog& catalog,
    JacobianEvaluationRequest request);
gcs::kernel::ContractResult<JacobianCheckReport> check_jacobian(
    const ConstraintCatalog& catalog,
    FiniteDifferenceCheckRequest request);

}
