module;

#include <optional>
#include <string>
#include <vector>

export module gcs.diagnostics;

export import gcs.kernel;
export import gcs.numeric_engine;

export namespace gcs::diagnostics {

struct DofReport {
    int parameterDof = 0;
    int equationDof = 0;
    int gaugeDof = 0;
    int freeDof = 0;
    SolveStatus status = SolveStatus::NotRun;
};

struct RankReport {
    int structuralRankEstimate = 0;
    int numericRankEstimate = 0;
    double conditionEstimate = 0.0;
};

struct ConstraintResidual {
    ConstraintId constraintId;
    double residual = 0.0;
    double tolerance = 0.0;
    bool satisfied = true;
};

struct ResidualReport {
    double totalResidual = 0.0;
    double maxResidual = 0.0;
    std::vector<ConstraintResidual> constraints;
};

struct ObstructionReport {
    bool present = false;
    std::string code;
    std::string message;
    std::vector<ContextId> contextIds;
    std::vector<EntityId> entityIds;
    std::vector<ConstraintId> constraintIds;
};

struct OverlapStatus {
    ProjectionId projectionId;
    bool compatible = true;
    double boundaryResidual = 0.0;
    std::vector<EntityId> entityIds;
};

struct GluingInput {
    ModelSnapshot model;
    CoverPlan coverPlan;
    std::vector<LocalSection> localSections;
    std::vector<BoundaryProjection> boundaryProjections;
    GaugePolicy gaugePolicy;
    TolerancePolicy tolerances;
};

struct GluingReport {
    bool accepted = false;
    ProposedState proposedGlobalState;
    std::vector<OverlapStatus> overlapStatuses;
    bool gaugeConsistent = true;
    ObstructionReport obstructionReport;
    StageReport stageReport;
};

struct DiagnosticInput {
    ModelSnapshot model;
    std::optional<ContextSnapshot> context;
    std::optional<numeric::NumericReport> numericReport;
    GaugePolicy gaugePolicy;
};

struct DiagnosticOutput {
    SolveStatus statusCode = SolveStatus::NotRun;
    DofReport dofReport;
    RankReport rankReport;
    ResidualReport residualReport;
    GluingReport gluingReport;
    ObstructionReport obstructionReport;
    std::vector<ReportMessage> warnings;
};

DofReport analyzeDof(const ModelSnapshot& model,
                     const ContextSnapshot& context,
                     const GaugePolicy& gaugePolicy);
DiagnosticOutput diagnose(const DiagnosticInput& input);
GluingReport glueLocalSections(const GluingInput& input);
ObstructionReport makeObstruction(std::string code, std::string message);

}
