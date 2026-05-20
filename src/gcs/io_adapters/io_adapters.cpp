module;

#include <fstream>
#include <sstream>
#include <string>
#include <vector>

module gcs.io_adapters;

import gcs.kernel;

namespace gcs::io {

namespace {

bool hasJsonExtension(const std::string& path) {
    return path.size() >= 5 && path.substr(path.size() - 5) == ".json";
}

}

SceneLoadResult loadScene(const SceneLoadRequest& request) {
    SceneLoadResult result;
    if (hasJsonExtension(request.path)) {
        result.errors.push_back("JSON scene loading is intentionally not part of the first C++23 module skeleton.");
        return result;
    }

    std::ifstream input(request.path);
    if (!input) {
        result.errors.push_back("Failed to open scene file: " + request.path);
        return result;
    }

    int rigidSetCount = 0;
    if (!(input >> rigidSetCount)) {
        result.errors.push_back("Failed to read rigid set count.");
        return result;
    }

    for (int i = 0; i < rigidSetCount; ++i) {
        int id = 0;
        input >> id;
        result.snapshot.rigidSets.push_back(RigidSet{RigidSetId{id}, {}});
    }

    int entityCount = 0;
    if (!(input >> entityCount)) {
        result.errors.push_back("Failed to read entity count.");
        return result;
    }

    for (int i = 0; i < entityCount; ++i) {
        int id = 0;
        int kind = 0;
        int rigidSetId = 0;
        input >> id >> kind >> rigidSetId;

        GeometricEntity entity;
        entity.id = EntityId{id};
        entity.kind = static_cast<GeometryKind>(kind);
        entity.rigidSetId = RigidSetId{rigidSetId};
        entity.parameters.dimension = geometryDof(entity.kind);
        result.snapshot.entities.push_back(entity);

        for (auto& rigidSet : result.snapshot.rigidSets) {
            if (rigidSet.id == entity.rigidSetId) {
                rigidSet.entityIds.push_back(entity.id);
                break;
            }
        }
    }

    int constraintCount = 0;
    if (!(input >> constraintCount)) {
        result.errors.push_back("Failed to read constraint count.");
        return result;
    }

    for (int i = 0; i < constraintCount; ++i) {
        int id = 0;
        int kind = 0;
        int arity = 0;
        input >> id >> kind >> arity;

        ConstraintInstance constraint;
        constraint.id = ConstraintId{id};
        constraint.kind = static_cast<ConstraintKind>(kind);
        for (int j = 0; j < arity; ++j) {
            int entityId = 0;
            input >> entityId;
            constraint.entityIds.push_back(EntityId{entityId});
        }
        result.snapshot.constraints.push_back(constraint);
    }

    for (int i = 0; i < entityCount; ++i) {
        int id = 0;
        if (!(input >> id)) {
            result.errors.push_back("Failed to read entity parameter block.");
            return result;
        }
        auto* entity = const_cast<GeometricEntity*>(findEntity(result.snapshot, EntityId{id}));
        if (entity == nullptr) {
            result.errors.push_back("Entity parameter block references a missing entity.");
            return result;
        }
        for (double& value : entity->parameters.values) {
            input >> value;
        }
    }

    for (int i = 0; i < constraintCount; ++i) {
        int id = 0;
        double value = 0.0;
        if (!(input >> id >> value)) {
            result.errors.push_back("Failed to read constraint parameter block.");
            return result;
        }
        auto* constraint = const_cast<ConstraintInstance*>(findConstraint(result.snapshot, ConstraintId{id}));
        if (constraint == nullptr) {
            result.errors.push_back("Constraint parameter block references a missing constraint.");
            return result;
        }
        constraint->value = value;
    }

    result.ok = true;
    return result;
}

SceneWriteResult writeSceneText(const SceneWriteRequest& request) {
    SceneWriteResult result;
    std::ofstream output(request.path);
    if (!output) {
        result.errors.push_back("Failed to open scene file for writing: " + request.path);
        return result;
    }

    output << request.snapshot.rigidSets.size() << "\n";
    for (const auto& rigidSet : request.snapshot.rigidSets) {
        output << rigidSet.id.value << " ";
    }
    output << "\n";

    output << request.snapshot.entities.size() << "\n";
    for (const auto& entity : request.snapshot.entities) {
        output << entity.id.value << " " << static_cast<int>(entity.kind) << " "
               << entity.rigidSetId.value << "\n";
    }

    output << request.snapshot.constraints.size() << "\n";
    for (const auto& constraint : request.snapshot.constraints) {
        output << constraint.id.value << " " << static_cast<int>(constraint.kind) << " "
               << constraint.entityIds.size();
        for (EntityId entityId : constraint.entityIds) {
            output << " " << entityId.value;
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

std::string summarizeScene(const ModelSnapshot& snapshot) {
    std::ostringstream output;
    output << "StateVersion=" << snapshot.stateVersion.value
           << " RigidSets=" << snapshot.rigidSets.size()
           << " Entities=" << snapshot.entities.size()
           << " Constraints=" << snapshot.constraints.size();
    return output.str();
}

}
