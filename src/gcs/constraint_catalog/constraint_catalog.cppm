module;

#include <string>
#include <vector>

export module gcs.constraint_catalog;

export import gcs.kernel;

export namespace gcs::constraints {

using gcs::kernel::ConstraintDraft;
using gcs::kernel::ConstraintId;
using gcs::kernel::ConstraintKind;
using gcs::kernel::ModelSnapshot;
using gcs::kernel::ReportMessage;
using gcs::kernel::StageReport;

struct ConstraintDefinition {
    ConstraintKind kind = ConstraintKind::coincident;
    std::string name;
    int min_entity_count = 0;
    int max_entity_count = 0;
    int residual_dimension = 0;
    int generic_dof_effect = 0;
    bool requires_distinct_rigid_sets = true;
};

struct ConstraintValidationInput {
    ModelSnapshot model;
    ConstraintDraft constraint;
};

struct ConstraintValidationResult {
    bool valid = false;
    ConstraintDefinition definition;
    std::vector<ReportMessage> messages;
};

const std::vector<ConstraintDefinition>& builtin_definitions();
const ConstraintDefinition* find_definition(ConstraintKind kind);
int residual_dimension(ConstraintKind kind);
int generic_dof_effect(ConstraintKind kind);
ConstraintValidationResult validate_constraint(const ConstraintValidationInput& input);
StageReport validate_model_constraints(const ModelSnapshot& model);

}
