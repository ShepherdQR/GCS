module;

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <string>
#include <utility>
#include <vector>

module gcs.numeric_engine;

import gcs.kernel;
import gcs.constraint_catalog;

namespace gcs::numeric {

namespace kernel = gcs::kernel;

namespace {

struct VariableColumn {
    EntityId entity_id;
    int offset = 0;
    int dimension = 0;
};

struct RankComputation {
    int rank = 0;
    double max_pivot = 0.0;
    double min_pivot = 0.0;
};

kernel::ReportMessage make_message(kernel::ReportSeverity severity,
                                   const char* code,
                                   const std::string& summary,
                                   std::vector<kernel::StableId> subjects = {}) {
    return kernel::make_report_message(
        severity,
        kernel::ReportCode{code},
        summary,
        std::move(subjects));
}

void append_message(StageReport& report,
                    std::vector<ReportMessage>& payload_messages,
                    kernel::ReportMessage message) {
    payload_messages.push_back(message);
    kernel::append_report_message(report, std::move(message));
}

bool positive_tolerances(const TolerancePolicy& tolerances) {
    return tolerances.residual > 0.0 &&
           tolerances.rank > 0.0 &&
           tolerances.boundary > 0.0;
}

bool valid_solve_limits(const SolveLimits& limits) {
    return limits.max_iterations >= 0 &&
           limits.trust_region_radius > 0.0 &&
           limits.damping > 0.0;
}

double residual_norm(const std::vector<double>& residuals) {
    double sum = 0.0;
    for (double residual : residuals) {
        sum += residual * residual;
    }
    return std::sqrt(sum);
}

double max_abs_value(const std::vector<double>& values) {
    double maximum = 0.0;
    for (double value : values) {
        maximum = std::max(maximum, std::abs(value));
    }
    return maximum;
}

double vector_norm(const std::vector<double>& values) {
    double sum = 0.0;
    for (double value : values) {
        sum += value * value;
    }
    return std::sqrt(sum);
}

bool residual_within_tolerance(const EquationAssembly& assembly, double tolerance) {
    return max_abs_value(assembly.residual_vector) <= tolerance;
}

std::vector<VariableColumn> build_variable_columns(const NumericTask& task,
                                                   int& variable_dimension) {
    std::vector<VariableColumn> columns;
    variable_dimension = 0;
    for (EntityId entity_id : task.active_variables) {
        const auto* entity = kernel::find_entity(task.problem_snapshot, entity_id);
        if (entity == nullptr) continue;
        const int dimension = kernel::geometry_dof(entity->kind);
        columns.push_back(VariableColumn{entity_id, variable_dimension, dimension});
        variable_dimension += dimension;
    }
    return columns;
}

const VariableColumn* find_variable_column(const std::vector<VariableColumn>& columns,
                                           EntityId entity_id) {
    for (const auto& column : columns) {
        if (column.entity_id == entity_id) return &column;
    }
    return nullptr;
}

const kernel::EntityState* find_state(const std::vector<kernel::EntityState>& states,
                                      EntityId entity_id) {
    for (const auto& state : states) {
        if (state.entity_id == entity_id) return &state;
    }
    return nullptr;
}

kernel::EntityDraft* find_mutable_entity(ModelSnapshot& snapshot, EntityId id) {
    for (auto& entity : snapshot.entities) {
        if (entity.id == id) return &entity;
    }
    return nullptr;
}

bool same_parameters(const kernel::ParameterVector& lhs,
                     const kernel::ParameterVector& rhs,
                     double tolerance) {
    if (lhs.dimension != rhs.dimension) return false;
    for (int index = 0; index < lhs.dimension; ++index) {
        if (std::abs(lhs.values[static_cast<std::size_t>(index)] -
                     rhs.values[static_cast<std::size_t>(index)]) > tolerance) {
            return false;
        }
    }
    return true;
}

RankComputation estimate_rank(std::vector<double> matrix,
                              int row_count,
                              int column_count,
                              double tolerance) {
    RankComputation result;
    int pivot_row = 0;

    for (int column = 0; column < column_count && pivot_row < row_count; ++column) {
        int best_row = pivot_row;
        double best_abs = 0.0;
        for (int row = pivot_row; row < row_count; ++row) {
            const double value = std::abs(
                matrix[static_cast<std::size_t>(row * column_count + column)]);
            if (value > best_abs) {
                best_abs = value;
                best_row = row;
            }
        }

        if (best_abs <= tolerance) continue;

        if (best_row != pivot_row) {
            for (int swap_column = column; swap_column < column_count; ++swap_column) {
                std::swap(
                    matrix[static_cast<std::size_t>(pivot_row * column_count + swap_column)],
                    matrix[static_cast<std::size_t>(best_row * column_count + swap_column)]);
            }
        }

        const double pivot = matrix[static_cast<std::size_t>(
            pivot_row * column_count + column)];
        const double pivot_abs = std::abs(pivot);
        result.max_pivot = std::max(result.max_pivot, pivot_abs);
        result.min_pivot =
            result.rank == 0 ? pivot_abs : std::min(result.min_pivot, pivot_abs);

        for (int row = pivot_row + 1; row < row_count; ++row) {
            const double factor =
                matrix[static_cast<std::size_t>(row * column_count + column)] / pivot;
            if (std::abs(factor) <= tolerance) continue;
            for (int reduce_column = column; reduce_column < column_count; ++reduce_column) {
                matrix[static_cast<std::size_t>(row * column_count + reduce_column)] -=
                    factor * matrix[static_cast<std::size_t>(
                                 pivot_row * column_count + reduce_column)];
            }
        }

        ++result.rank;
        ++pivot_row;
    }

    return result;
}

std::vector<int> build_free_columns(const NumericTask& task,
                                    const EquationAssembly& assembly) {
    std::vector<int> columns;
    int offset = 0;
    for (EntityId entity_id : assembly.variable_order) {
        const auto* entity = kernel::find_entity(task.problem_snapshot, entity_id);
        if (entity == nullptr) continue;
        const int dimension = kernel::geometry_dof(entity->kind);
        const bool boundary = kernel::contains_entity(task.boundary_variables, entity_id);
        if (!boundary) {
            for (int index = 0; index < dimension; ++index) {
                columns.push_back(offset + index);
            }
        }
        offset += dimension;
    }
    return columns;
}

std::vector<double> select_columns(const std::vector<double>& matrix,
                                   int row_count,
                                   int column_count,
                                   const std::vector<int>& selected_columns) {
    std::vector<double> selected;
    selected.reserve(static_cast<std::size_t>(row_count) * selected_columns.size());
    for (int row = 0; row < row_count; ++row) {
        for (int column : selected_columns) {
            if (column >= 0 && column < column_count) {
                selected.push_back(
                    matrix[static_cast<std::size_t>(row * column_count + column)]);
            }
        }
    }
    return selected;
}

bool solve_dense_linear_system(std::vector<double> matrix,
                               std::vector<double> rhs,
                               int dimension,
                               double tolerance,
                               std::vector<double>& solution) {
    if (dimension <= 0) return false;

    for (int column = 0; column < dimension; ++column) {
        int pivot_row = column;
        double pivot_abs = 0.0;
        for (int row = column; row < dimension; ++row) {
            const double value = std::abs(
                matrix[static_cast<std::size_t>(row * dimension + column)]);
            if (value > pivot_abs) {
                pivot_abs = value;
                pivot_row = row;
            }
        }
        if (pivot_abs <= tolerance) return false;

        if (pivot_row != column) {
            for (int swap_column = column; swap_column < dimension; ++swap_column) {
                std::swap(
                    matrix[static_cast<std::size_t>(column * dimension + swap_column)],
                    matrix[static_cast<std::size_t>(pivot_row * dimension + swap_column)]);
            }
            std::swap(rhs[static_cast<std::size_t>(column)],
                      rhs[static_cast<std::size_t>(pivot_row)]);
        }

        const double pivot =
            matrix[static_cast<std::size_t>(column * dimension + column)];
        for (int row = column + 1; row < dimension; ++row) {
            const double factor =
                matrix[static_cast<std::size_t>(row * dimension + column)] / pivot;
            if (std::abs(factor) <= tolerance) continue;
            for (int reduce_column = column; reduce_column < dimension; ++reduce_column) {
                matrix[static_cast<std::size_t>(row * dimension + reduce_column)] -=
                    factor * matrix[static_cast<std::size_t>(
                                 column * dimension + reduce_column)];
            }
            rhs[static_cast<std::size_t>(row)] -=
                factor * rhs[static_cast<std::size_t>(column)];
        }
    }

    solution.assign(static_cast<std::size_t>(dimension), 0.0);
    for (int row = dimension - 1; row >= 0; --row) {
        double value = rhs[static_cast<std::size_t>(row)];
        for (int column = row + 1; column < dimension; ++column) {
            value -= matrix[static_cast<std::size_t>(row * dimension + column)] *
                     solution[static_cast<std::size_t>(column)];
        }
        const double diagonal =
            matrix[static_cast<std::size_t>(row * dimension + row)];
        if (std::abs(diagonal) <= tolerance) return false;
        solution[static_cast<std::size_t>(row)] = value / diagonal;
    }
    return true;
}

bool compute_damped_gauss_newton_step(const EquationAssembly& assembly,
                                      const std::vector<int>& free_columns,
                                      double damping,
                                      double tolerance,
                                      std::vector<double>& full_step) {
    const int free_dimension = static_cast<int>(free_columns.size());
    const int row_count = assembly.jacobian_report.row_count;
    const int column_count = assembly.jacobian_report.column_count;
    if (free_dimension <= 0 || row_count <= 0 || column_count <= 0) return false;

    std::vector<double> normal_matrix(
        static_cast<std::size_t>(free_dimension * free_dimension),
        0.0);
    std::vector<double> rhs(static_cast<std::size_t>(free_dimension), 0.0);

    for (int lhs = 0; lhs < free_dimension; ++lhs) {
        const int lhs_column = free_columns[static_cast<std::size_t>(lhs)];
        for (int row = 0; row < row_count; ++row) {
            const double lhs_value = assembly.jacobian_report.values[
                static_cast<std::size_t>(row * column_count + lhs_column)];
            rhs[static_cast<std::size_t>(lhs)] -=
                lhs_value * assembly.residual_vector[static_cast<std::size_t>(row)];
            for (int rhs_index = 0; rhs_index < free_dimension; ++rhs_index) {
                const int rhs_column = free_columns[static_cast<std::size_t>(rhs_index)];
                const double rhs_value = assembly.jacobian_report.values[
                    static_cast<std::size_t>(row * column_count + rhs_column)];
                normal_matrix[static_cast<std::size_t>(
                    lhs * free_dimension + rhs_index)] += lhs_value * rhs_value;
            }
        }
        normal_matrix[static_cast<std::size_t>(lhs * free_dimension + lhs)] += damping;
    }

    std::vector<double> reduced_step;
    if (!solve_dense_linear_system(
            std::move(normal_matrix),
            std::move(rhs),
            free_dimension,
            tolerance,
            reduced_step)) {
        return false;
    }

    full_step.assign(static_cast<std::size_t>(column_count), 0.0);
    for (int index = 0; index < free_dimension; ++index) {
        full_step[static_cast<std::size_t>(free_columns[static_cast<std::size_t>(index)])] =
            reduced_step[static_cast<std::size_t>(index)];
    }
    return true;
}

void apply_step(ModelSnapshot& snapshot,
                const NumericTask& task,
                const std::vector<double>& step,
                double scale) {
    int offset = 0;
    for (EntityId entity_id : task.active_variables) {
        const auto* original = kernel::find_entity(task.problem_snapshot, entity_id);
        if (original == nullptr) continue;
        const int dimension = kernel::geometry_dof(original->kind);
        const bool boundary = kernel::contains_entity(task.boundary_variables, entity_id);
        auto* entity = find_mutable_entity(snapshot, entity_id);
        if (entity != nullptr && !boundary) {
            for (int index = 0; index < dimension; ++index) {
                entity->parameters.values[static_cast<std::size_t>(index)] +=
                    scale * step[static_cast<std::size_t>(offset + index)];
            }
        }
        offset += dimension;
    }
}

NumericTask task_with_snapshot(const NumericTask& task, ModelSnapshot snapshot) {
    NumericTask next = task;
    next.problem_snapshot = std::move(snapshot);
    return next;
}

double scaled_step_norm(const std::vector<double>& step, double scale) {
    double sum = 0.0;
    for (double value : step) {
        const double scaled = scale * value;
        sum += scaled * scaled;
    }
    return std::sqrt(sum);
}

ResidualReport make_residual_report(const EquationAssembly& assembly) {
    ResidualReport report;
    report.dimension = assembly.residual_dimension;
    report.norm = residual_norm(assembly.residual_vector);
    report.max_abs_value = max_abs_value(assembly.residual_vector);
    report.blocks = assembly.residual_blocks;
    return report;
}

RankConditionReport make_rank_condition_report(const NumericTask& task,
                                               const EquationAssembly& assembly,
                                               double rank_tolerance) {
    RankConditionReport report;
    report.variable_dimension = assembly.variable_dimension;
    report.residual_dimension = assembly.residual_dimension;

    const auto free_columns = build_free_columns(task, assembly);
    report.free_variable_dimension = static_cast<int>(free_columns.size());
    report.frozen_variable_dimension =
        std::max(0, report.variable_dimension - report.free_variable_dimension);

    const auto free_jacobian = select_columns(
        assembly.jacobian_report.values,
        assembly.jacobian_report.row_count,
        assembly.jacobian_report.column_count,
        free_columns);
    const auto rank = estimate_rank(
        free_jacobian,
        assembly.jacobian_report.row_count,
        report.free_variable_dimension,
        rank_tolerance);
    report.rank_estimate = rank.rank;

    const int effective_variables = std::max(
        0,
        report.free_variable_dimension - task.gauge_policy.removed_dof);
    report.nullity_estimate = std::max(0, effective_variables - report.rank_estimate);
    report.under_constrained = report.nullity_estimate > 0;
    report.over_constrained = assembly.residual_dimension > effective_variables;
    report.numerically_singular =
        report.rank_estimate < std::min(assembly.residual_dimension, effective_variables);
    if (!report.numerically_singular && rank.rank > 0 && rank.min_pivot > 0.0) {
        report.condition_estimate_available = true;
        report.condition_estimate = rank.max_pivot / rank.min_pivot;
    }
    return report;
}

std::vector<BoundaryVariableReport> make_boundary_report(
    const NumericTask& task,
    const LocalSection& local_section) {
    std::vector<BoundaryVariableReport> reports;
    for (EntityId entity_id : task.boundary_variables) {
        BoundaryVariableReport report;
        report.entity_id = entity_id;
        report.active = kernel::contains_entity(task.active_variables, entity_id);
        if (const auto* before = kernel::find_entity(task.problem_snapshot, entity_id)) {
            report.before = before->parameters;
        }
        if (const auto* after = find_state(local_section.entity_states, entity_id)) {
            report.after = after->parameters;
        }
        report.unchanged = same_parameters(report.before, report.after, task.tolerances.boundary);
        reports.push_back(report);
    }
    return reports;
}

IterationTrace make_initial_trace(kernel::StateVersionId base_version,
                                  double initial_residual) {
    IterationTrace trace;
    trace.base_version = base_version;
    trace.entries.push_back(
        IterationTraceEntry{0, "initial", initial_residual, 0.0, false});
    return trace;
}

}  // namespace

NumericTask make_numeric_task(const ModelSnapshot& model,
                              const ContextSnapshot& context,
                              const std::vector<EntityId>& active_variables,
                              const std::vector<ConstraintId>& active_equations,
                              const GaugePolicy& gauge_policy) {
    NumericTask task;
    task.problem_snapshot = model;
    task.context_snapshot = context;
    task.active_variables = active_variables;
    task.active_equations = active_equations;
    task.tolerances = model.tolerances;
    task.gauge_policy = gauge_policy;
    return task;
}

gcs::kernel::ContractResult<NumericTaskValidationReport> validate_task(
    const NumericTask& task) {
    kernel::ContractResult<NumericTaskValidationReport> result;
    result.report = kernel::make_stage_report("numeric_engine.validate_task");

    if (!(task.context_snapshot.state_version == task.problem_snapshot.state_version)) {
        result.payload.valid = false;
        result.payload.context_version_matches = false;
        append_message(
            result.report,
            result.payload.messages,
            make_message(
                kernel::ReportSeverity::error,
                "numeric.context_version_mismatch",
                "Numeric task context state version must match the problem snapshot.",
                {kernel::StableId{"context", task.context_snapshot.id.value}}));
    }

    if (!positive_tolerances(task.tolerances)) {
        result.payload.valid = false;
        result.payload.tolerances_valid = false;
        append_message(
            result.report,
            result.payload.messages,
            make_message(
                kernel::ReportSeverity::error,
                "numeric.invalid_tolerance",
                "Numeric task tolerances must be positive."));
    }

    if (!valid_solve_limits(task.solve_limits)) {
        result.payload.valid = false;
        result.payload.solve_limits_valid = false;
        append_message(
            result.report,
            result.payload.messages,
            make_message(
                kernel::ReportSeverity::error,
                "numeric.invalid_solve_limits",
                "Numeric task solve limits are invalid."));
    }

    for (EntityId entity_id : task.active_variables) {
        if (kernel::find_entity(task.problem_snapshot, entity_id) == nullptr) {
            result.payload.valid = false;
            result.payload.active_variables_exist = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "numeric.missing_entity",
                    "Numeric task references a missing active entity.",
                    {kernel::StableId{"entity", entity_id.value}}));
        }
        if (!kernel::contains_entity(task.context_snapshot.entity_ids, entity_id)) {
            result.payload.valid = false;
            result.payload.active_variables_within_context = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "numeric.entity_not_in_context",
                    "Numeric task active entity is not part of the task context.",
                    {kernel::StableId{"context", task.context_snapshot.id.value},
                     kernel::StableId{"entity", entity_id.value}}));
        }
    }

    for (ConstraintId constraint_id : task.active_equations) {
        const auto* constraint = kernel::find_constraint(task.problem_snapshot, constraint_id);
        if (constraint == nullptr) {
            result.payload.valid = false;
            result.payload.active_equations_exist = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "numeric.missing_constraint",
                    "Numeric task references a missing active constraint.",
                    {kernel::StableId{"constraint", constraint_id.value}}));
        }
        if (!kernel::contains_constraint(task.context_snapshot.constraint_ids, constraint_id)) {
            result.payload.valid = false;
            result.payload.active_equations_within_context = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "numeric.constraint_not_in_context",
                    "Numeric task active constraint is not part of the task context.",
                    {kernel::StableId{"context", task.context_snapshot.id.value},
                     kernel::StableId{"constraint", constraint_id.value}}));
        }
        if (constraint != nullptr) {
            for (EntityId entity_id : constraint->entity_ids) {
                if (!kernel::contains_entity(task.active_variables, entity_id)) {
                    result.payload.valid = false;
                    result.payload.active_equation_entities_are_active = false;
                    append_message(
                        result.report,
                        result.payload.messages,
                        make_message(
                            kernel::ReportSeverity::error,
                            "numeric.constraint_entity_not_active",
                            "Numeric task equation references an entity outside the active variable set.",
                            {kernel::StableId{"constraint", constraint_id.value},
                             kernel::StableId{"entity", entity_id.value}}));
                }
            }
        }
    }

    for (EntityId entity_id : task.boundary_variables) {
        if (!kernel::contains_entity(task.active_variables, entity_id)) {
            result.payload.valid = false;
            result.payload.boundary_variables_are_active = false;
            append_message(
                result.report,
                result.payload.messages,
                make_message(
                    kernel::ReportSeverity::error,
                    "numeric.boundary_not_active",
                    "Numeric task boundary variable must also be an active variable.",
                    {kernel::StableId{"entity", entity_id.value}}));
        }
    }

    return result;
}

gcs::kernel::ContractResult<EquationAssembly> assemble_equations(
    const NumericTask& task,
    const constraints::ConstraintCatalog& catalog) {
    kernel::ContractResult<EquationAssembly> result;
    result.report = kernel::make_stage_report("numeric_engine.assemble_equations");

    auto validation = validate_task(task);
    for (auto message : validation.report.messages) {
        kernel::append_report_message(result.report, std::move(message));
    }
    if (!validation.payload.valid) return result;

    result.payload.variable_order = task.active_variables;
    result.payload.equation_order = task.active_equations;
    int variable_dimension = 0;
    const auto variable_columns = build_variable_columns(task, variable_dimension);
    result.payload.variable_dimension = variable_dimension;

    int residual_offset = 0;
    for (ConstraintId constraint_id : task.active_equations) {
        auto residual = constraints::evaluate_residual(
            catalog,
            constraints::ResidualEvaluationRequest{task.problem_snapshot, constraint_id});
        for (auto message : residual.report.messages) {
            kernel::append_report_message(result.report, std::move(message));
        }
        if (!residual.payload.valid) {
            kernel::append_report_message(
                result.report,
                make_message(
                    kernel::ReportSeverity::error,
                    "numeric.residual_assembly_failed",
                    "Constraint residual evaluation failed during numeric assembly.",
                    {kernel::StableId{"constraint", constraint_id.value}}));
            return result;
        }

        ResidualBlock block;
        block.constraint_id = constraint_id;
        block.offset = residual_offset;
        block.dimension = static_cast<int>(residual.payload.residuals.size());
        block.residuals = residual.payload.residuals;
        block.norm = residual_norm(block.residuals);
        block.max_abs_value = max_abs_value(block.residuals);

        auto jacobian = constraints::evaluate_jacobian(
            catalog,
            constraints::JacobianEvaluationRequest{task.problem_snapshot, constraint_id});
        for (auto message : jacobian.report.messages) {
            kernel::append_report_message(result.report, std::move(message));
        }
        if (!jacobian.payload.valid) {
            kernel::append_report_message(
                result.report,
                make_message(
                    kernel::ReportSeverity::error,
                    "numeric.jacobian_assembly_failed",
                    "Constraint Jacobian evaluation failed during numeric assembly.",
                    {kernel::StableId{"constraint", constraint_id.value}}));
            return result;
        }

        JacobianBlock jacobian_block;
        jacobian_block.constraint_id = constraint_id;
        jacobian_block.row_offset = residual_offset;
        jacobian_block.row_count = jacobian.payload.row_count;
        jacobian_block.column_count = jacobian.payload.column_count;
        jacobian_block.entity_ids = jacobian.payload.entity_ids;
        jacobian_block.entity_parameter_dimensions =
            jacobian.payload.entity_parameter_dimensions;
        jacobian_block.values = jacobian.payload.values;

        int minimum_column_offset = result.payload.variable_dimension;
        for (EntityId entity_id : jacobian_block.entity_ids) {
            const auto* column = find_variable_column(variable_columns, entity_id);
            if (column == nullptr) {
                kernel::append_report_message(
                    result.report,
                    make_message(
                        kernel::ReportSeverity::error,
                        "numeric.jacobian_variable_not_active",
                        "Jacobian references an entity outside the active variable order.",
                        {kernel::StableId{"constraint", constraint_id.value},
                         kernel::StableId{"entity", entity_id.value}}));
                return result;
            }
            jacobian_block.entity_column_offsets.push_back(column->offset);
            minimum_column_offset = std::min(minimum_column_offset, column->offset);
        }
        jacobian_block.column_offset =
            jacobian_block.entity_column_offsets.empty() ? 0 : minimum_column_offset;

        residual_offset += block.dimension;
        result.payload.residual_dimension += block.dimension;
        for (double value : block.residuals) {
            result.payload.residual_vector.push_back(value);
        }
        result.payload.residual_blocks.push_back(std::move(block));
        result.payload.jacobian_report.blocks.push_back(std::move(jacobian_block));
    }

    result.payload.jacobian_report.valid = true;
    result.payload.jacobian_report.row_count = result.payload.residual_dimension;
    result.payload.jacobian_report.column_count = result.payload.variable_dimension;
    result.payload.jacobian_report.values.assign(
        static_cast<std::size_t>(result.payload.residual_dimension *
                                 result.payload.variable_dimension),
        0.0);

    for (const auto& block : result.payload.jacobian_report.blocks) {
        int local_column_offset = 0;
        for (std::size_t entity_index = 0;
             entity_index < block.entity_ids.size() &&
             entity_index < block.entity_parameter_dimensions.size() &&
             entity_index < block.entity_column_offsets.size();
             ++entity_index) {
            const int entity_dimension =
                block.entity_parameter_dimensions[entity_index];
            const int target_column_offset =
                block.entity_column_offsets[entity_index];
            for (int row = 0; row < block.row_count; ++row) {
                for (int column = 0; column < entity_dimension; ++column) {
                    const auto source_index = static_cast<std::size_t>(
                        row * block.column_count + local_column_offset + column);
                    const auto target_index = static_cast<std::size_t>(
                        (block.row_offset + row) *
                            result.payload.jacobian_report.column_count +
                        target_column_offset + column);
                    result.payload.jacobian_report.values[target_index] =
                        block.values[source_index];
                }
            }
            local_column_offset += entity_dimension;
        }
    }

    result.payload.valid = true;
    return result;
}

gcs::kernel::ContractResult<EquationAssembly> assemble_equations(const NumericTask& task) {
    return assemble_equations(task, constraints::builtin_catalog());
}

NumericReport solve_local(const NumericTask& task) {
    NumericReport report;
    report.stage_report = kernel::make_stage_report("numeric_engine.solve_local");
    report.local_section.context_id = task.context_snapshot.id;
    report.proposed_state.base_version = task.problem_snapshot.state_version;

    auto assembly = assemble_equations(task);
    for (auto message : assembly.report.messages) {
        kernel::append_report_message(report.stage_report, std::move(message));
    }
    if (!assembly.payload.valid) {
        report.result_code = SolveStatus::invalid_model;
        report.local_section.valid = false;
        report.failure_cause = "Numeric task validation or equation assembly failed.";
        return report;
    }

    ModelSnapshot working_snapshot = task.problem_snapshot;
    NumericTask working_task = task_with_snapshot(task, working_snapshot);
    EquationAssembly current_assembly = std::move(assembly.payload);
    double current_residual = residual_norm(current_assembly.residual_vector);

    report.initial_residual = current_residual;
    report.final_residual = current_residual;
    report.iteration_trace = make_initial_trace(
        task.problem_snapshot.state_version,
        report.initial_residual);

    bool converged = residual_within_tolerance(
        current_assembly,
        task.tolerances.residual);
    bool failed = false;
    double last_step_norm = 0.0;

    if (converged) {
        report.iteration_trace.entries.push_back(
            IterationTraceEntry{0, "converged", current_residual, 0.0, true});
    }

    for (int iteration = 1;
         !converged && !failed && iteration <= task.solve_limits.max_iterations;
         ++iteration) {
        const auto free_columns = build_free_columns(working_task, current_assembly);
        std::vector<double> step;
        if (!compute_damped_gauss_newton_step(
                current_assembly,
                free_columns,
                task.solve_limits.damping,
                task.tolerances.rank,
                step)) {
            failed = true;
            report.failure_cause =
                "Damped Gauss-Newton step could not be computed for the active task.";
            break;
        }

        double base_scale = 1.0;
        const double raw_step_norm = vector_norm(step);
        if (raw_step_norm > task.solve_limits.trust_region_radius) {
            base_scale = task.solve_limits.trust_region_radius / raw_step_norm;
        }

        bool accepted = false;
        EquationAssembly accepted_assembly;
        ModelSnapshot accepted_snapshot;
        double accepted_residual = current_residual;
        double accepted_step_norm = 0.0;

        for (int attempt = 0; attempt < 8 && !accepted; ++attempt) {
            const double scale = base_scale / static_cast<double>(1 << attempt);
            ModelSnapshot trial_snapshot = working_snapshot;
            apply_step(trial_snapshot, working_task, step, scale);
            NumericTask trial_task = task_with_snapshot(task, trial_snapshot);
            auto trial_assembly = assemble_equations(trial_task);
            for (auto message : trial_assembly.report.messages) {
                kernel::append_report_message(report.stage_report, std::move(message));
            }
            if (!trial_assembly.payload.valid) {
                failed = true;
                report.failure_cause = "Trial equation assembly failed during numeric solve.";
                break;
            }

            const double trial_residual =
                residual_norm(trial_assembly.payload.residual_vector);
            if (trial_residual < current_residual ||
                residual_within_tolerance(
                    trial_assembly.payload,
                    task.tolerances.residual)) {
                accepted = true;
                accepted_snapshot = std::move(trial_snapshot);
                accepted_assembly = std::move(trial_assembly.payload);
                accepted_residual = trial_residual;
                accepted_step_norm = scaled_step_norm(step, scale);
            }
        }

        if (failed) break;
        if (!accepted) {
            failed = true;
            report.failure_cause =
                "Damped Gauss-Newton step failed to reduce the residual.";
            report.iteration_trace.entries.push_back(
                IterationTraceEntry{
                    iteration,
                    "damped_gauss_newton_rejected",
                    current_residual,
                    0.0,
                    false});
            break;
        }

        working_snapshot = std::move(accepted_snapshot);
        working_task = task_with_snapshot(task, working_snapshot);
        current_assembly = std::move(accepted_assembly);
        current_residual = accepted_residual;
        last_step_norm = accepted_step_norm;
        report.iteration_count = iteration;
        report.iteration_trace.entries.push_back(
            IterationTraceEntry{
                iteration,
                "damped_gauss_newton",
                current_residual,
                accepted_step_norm,
                true});
        converged = residual_within_tolerance(
            current_assembly,
            task.tolerances.residual);
    }

    if (!converged && !failed) {
        failed = true;
        report.failure_cause = "Numeric solve reached the iteration limit before convergence.";
    }

    if (converged &&
        (report.iteration_trace.entries.empty() ||
         report.iteration_trace.entries.back().phase != "converged")) {
        report.iteration_trace.entries.push_back(
            IterationTraceEntry{
                report.iteration_count,
                "converged",
                current_residual,
                0.0,
                true});
    }

    report.equation_assembly = std::move(current_assembly);

    report.local_section.entity_states = kernel::capture_entity_states(
        working_snapshot,
        task.active_variables);
    report.local_section.valid = true;
    report.proposed_state.entity_states = report.local_section.entity_states;

    report.residual_report = make_residual_report(report.equation_assembly);
    report.rank_condition_report = make_rank_condition_report(
        task,
        report.equation_assembly,
        task.tolerances.rank);
    report.rank_estimate = report.rank_condition_report.rank_estimate;
    report.condition_estimate = report.rank_condition_report.condition_estimate;
    report.final_residual = report.residual_report.norm;
    report.step_norm = last_step_norm;
    report.boundary_variables = make_boundary_report(task, report.local_section);
    report.result_code = failed ? SolveStatus::failed : SolveStatus::solved;

    if (failed) {
        report.local_section.valid = false;
        report.stage_report.status = kernel::StageStatus::error;
        kernel::append_report_message(
            report.stage_report,
            kernel::make_report_message(
                kernel::ReportSeverity::error,
                kernel::ReportCode{"numeric.local_section.failed"},
                report.failure_cause,
                {kernel::StableId{"context", task.context_snapshot.id.value}}));
    } else {
        kernel::append_report_message(
            report.stage_report,
            kernel::make_report_message(
                kernel::ReportSeverity::info,
                kernel::ReportCode{"numeric.local_section.converged"},
                "Damped Gauss-Newton numeric engine produced a converged local section.",
                {kernel::StableId{"context", task.context_snapshot.id.value}}));
    }

    return report;
}

}
