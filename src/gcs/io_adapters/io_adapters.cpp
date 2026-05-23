module;

#include <cstdint>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

module gcs.io_adapters;

import gcs.kernel;

namespace gcs::io {

namespace kernel = gcs::kernel;

namespace {

bool has_json_extension(const std::string& path) {
    return path.size() >= 5 && path.substr(path.size() - 5) == ".json";
}

}  // namespace

SceneLoadResult load_scene(const SceneLoadRequest& request) {
    SceneLoadResult result;
    if (has_json_extension(request.path)) {
        result.errors.push_back(
            "JSON scene loading is intentionally not part of the first C++23 module skeleton.");
        return result;
    }

    std::ifstream input(request.path);
    if (!input) {
        result.errors.push_back("Failed to open scene file: " + request.path);
        return result;
    }

    int rigid_set_count = 0;
    if (!(input >> rigid_set_count)) {
        result.errors.push_back("Failed to read rigid set count.");
        return result;
    }

    for (int i = 0; i < rigid_set_count; ++i) {
        std::uint64_t id = 0;
        input >> id;
        result.snapshot.rigid_sets.push_back(
            kernel::RigidSetDraft{kernel::RigidSetId{id}, {}});
    }

    int entity_count = 0;
    if (!(input >> entity_count)) {
        result.errors.push_back("Failed to read entity count.");
        return result;
    }

    for (int i = 0; i < entity_count; ++i) {
        std::uint64_t id = 0;
        int kind = 0;
        std::uint64_t rigid_set_id = 0;
        input >> id >> kind >> rigid_set_id;

        kernel::EntityDraft entity;
        entity.id = kernel::EntityId{id};
        entity.kind = static_cast<kernel::GeometryKind>(kind);
        entity.rigid_set_id = kernel::RigidSetId{rigid_set_id};
        entity.parameters.dimension = kernel::geometry_dof(entity.kind);
        result.snapshot.entities.push_back(entity);

        for (auto& rigid_set : result.snapshot.rigid_sets) {
            if (rigid_set.id == entity.rigid_set_id) {
                rigid_set.entity_ids.push_back(entity.id);
                break;
            }
        }
    }

    int constraint_count = 0;
    if (!(input >> constraint_count)) {
        result.errors.push_back("Failed to read constraint count.");
        return result;
    }

    for (int i = 0; i < constraint_count; ++i) {
        std::uint64_t id = 0;
        int kind = 0;
        int arity = 0;
        input >> id >> kind >> arity;

        kernel::ConstraintDraft constraint;
        constraint.id = kernel::ConstraintId{id};
        constraint.kind = static_cast<kernel::ConstraintKind>(kind);
        for (int j = 0; j < arity; ++j) {
            std::uint64_t entity_id = 0;
            input >> entity_id;
            constraint.entity_ids.push_back(kernel::EntityId{entity_id});
        }
        result.snapshot.constraints.push_back(constraint);
    }

    for (int i = 0; i < entity_count; ++i) {
        std::uint64_t id = 0;
        if (!(input >> id)) {
            result.errors.push_back("Failed to read entity parameter block.");
            return result;
        }
        auto* entity = const_cast<kernel::EntityDraft*>(
            kernel::find_entity(result.snapshot, kernel::EntityId{id}));
        if (entity == nullptr) {
            result.errors.push_back("Entity parameter block references a missing entity.");
            return result;
        }
        for (double& value : entity->parameters.values) {
            input >> value;
        }
    }

    for (int i = 0; i < constraint_count; ++i) {
        std::uint64_t id = 0;
        double value = 0.0;
        if (!(input >> id >> value)) {
            result.errors.push_back("Failed to read constraint parameter block.");
            return result;
        }
        auto* constraint = const_cast<kernel::ConstraintDraft*>(
            kernel::find_constraint(result.snapshot, kernel::ConstraintId{id}));
        if (constraint == nullptr) {
            result.errors.push_back("Constraint parameter block references a missing constraint.");
            return result;
        }
        constraint->value = value;
    }

    auto validation = kernel::validate_model(result.snapshot);
    if (validation.report.status == kernel::StageStatus::error) {
        for (const auto& message : validation.report.messages) {
            result.errors.push_back(message.code.value + ": " + message.summary);
        }
        return result;
    }

    result.ok = true;
    return result;
}

SceneWriteResult write_scene_text(const SceneWriteRequest& request) {
    SceneWriteResult result;
    std::ofstream output(request.path);
    if (!output) {
        result.errors.push_back("Failed to open scene file for writing: " + request.path);
        return result;
    }

    output << request.snapshot.rigid_sets.size() << "\n";
    for (const auto& rigid_set : request.snapshot.rigid_sets) {
        output << rigid_set.id.value << " ";
    }
    output << "\n";

    output << request.snapshot.entities.size() << "\n";
    for (const auto& entity : request.snapshot.entities) {
        output << entity.id.value << " " << static_cast<int>(entity.kind) << " "
               << entity.rigid_set_id.value << "\n";
    }

    output << request.snapshot.constraints.size() << "\n";
    for (const auto& constraint : request.snapshot.constraints) {
        output << constraint.id.value << " " << static_cast<int>(constraint.kind) << " "
               << constraint.entity_ids.size();
        for (kernel::EntityId entity_id : constraint.entity_ids) {
            output << " " << entity_id.value;
        }
        output << "\n";
    }

    output << "\n";
    for (const auto& entity : request.snapshot.entities) {
        output << entity.id.value;
        for (double value : entity.parameters.values) {
            output << " " << value;
        }
        output << "\n";
    }

    output << "\n";
    for (const auto& constraint : request.snapshot.constraints) {
        output << constraint.id.value << " " << constraint.value << "\n";
    }

    result.ok = true;
    return result;
}

std::string summarize_scene(const ModelSnapshot& snapshot) {
    std::ostringstream output;
    output << "StateVersion=" << snapshot.state_version.value
           << " RigidSets=" << snapshot.rigid_sets.size()
           << " Entities=" << snapshot.entities.size()
           << " Constraints=" << snapshot.constraints.size();
    return output.str();
}

}
