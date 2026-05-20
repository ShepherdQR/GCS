module;

#include <string>
#include <vector>

export module gcs.constraint_catalog;

export import gcs.kernel;

export namespace gcs::constraints {

struct ConstraintDefinition {
    ConstraintKind kind = ConstraintKind::Coincident;
    std::string name;
    int minEntityCount = 0;
    int maxEntityCount = 0;
    int residualDimension = 0;
    int genericDofEffect = 0;
    bool requiresDistinctRigidSets = true;
};

struct ConstraintValidationInput {
    ModelSnapshot model;
    ConstraintInstance constraint;
};

struct ConstraintValidationResult {
    bool valid = false;
    ConstraintDefinition definition;
    std::vector<ReportMessage> messages;
};

const std::vector<ConstraintDefinition>& builtinDefinitions();
const ConstraintDefinition* findDefinition(ConstraintKind kind);
int residualDimension(ConstraintKind kind);
int genericDofEffect(ConstraintKind kind);
ConstraintValidationResult validateConstraint(const ConstraintValidationInput& input);
StageReport validateModelConstraints(const ModelSnapshot& model);

}
