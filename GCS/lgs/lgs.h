#pragma once

#include "core/core.h"
#include "dcm/dcm.h"
#include <vector>
#include <string>

namespace gcs {
namespace lgs {

enum class ConstraintStatus {
    WellConstrained,
    UnderConstrained,
    OverConstrained,
    OverConstrainedConsistent
};

std::string toString(ConstraintStatus status);

struct DOFAnalysis {
    int geometryDOF;
    int constraintRemovedDOF;
    int netDOF;
    ConstraintStatus status;
};

struct ConstraintViolation {
    int constraintId;
    double residual;
    double tolerance;
    bool satisfied;
};

struct StatusReport {
    ConstraintStatus overallStatus;
    DOFAnalysis dofAnalysis;
    std::vector<ConstraintViolation> violations;
    bool isConsistent;
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
    ConstraintStatus classifyStatusWithRigidSets(const Manager& m, const dcm::SubProblem& sp, int netDOF) const;
    double computeConstraintResidual(const Manager& m, const Constraint& c) const;
};

}
}
