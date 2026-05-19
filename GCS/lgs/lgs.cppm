module;

#include <string>
#include <vector>

export module gcs.lgs;

export import gcs.core;
export import gcs.dcm;

export namespace gcs::lgs {

enum class ConstraintStatus {
    WellConstrained,
    UnderConstrained,
    OverConstrained,
    OverConstrainedConsistent
};

std::string toString(ConstraintStatus status);

struct DOFAnalysis {
    int geometryDOF = 0;
    int constraintRemovedDOF = 0;
    int netDOF = 0;
    ConstraintStatus status = ConstraintStatus::WellConstrained;
};

struct ConstraintViolation {
    int constraintId = 0;
    double residual = 0.0;
    double tolerance = 0.0;
    bool satisfied = true;
};

struct StatusReport {
    ConstraintStatus overallStatus = ConstraintStatus::WellConstrained;
    DOFAnalysis dofAnalysis;
    std::vector<ConstraintViolation> violations;
    bool isConsistent = true;
    std::string summaryText;
};

class LocalGeometricSolver {
public:
    LocalGeometricSolver() = default;

    DOFAnalysis analyzeDOF(const Manager& m) const;
    DOFAnalysis analyzeDOF(const Manager& m, const dcm::SubProblem& sp) const;

    StatusReport analyzeStatus(const Manager& m) const;
    StatusReport analyzeStatus(const Manager& m, const dcm::SubProblem& sp) const;

    std::vector<ConstraintViolation> checkSatisfaction(
        const Manager& m,
        double tolerance = 1e-6) const;

    bool isWellConstrained(const Manager& m) const;

private:
    int computeGeometryDOF(const Manager& m, const dcm::SubProblem& sp) const;
    int computeConstraintRemovedDOF(const Manager& m, const dcm::SubProblem& sp) const;
    ConstraintStatus classifyStatus(int netDOF) const;
    ConstraintStatus classifyStatusForSubProblem(const Manager& m, const dcm::SubProblem& sp, int netDOF) const;
    double computeConstraintResidual(const Manager& m, const Constraint& c) const;
};

}
