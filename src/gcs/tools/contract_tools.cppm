module;

export module gcs.contract_tools;

export import gcs.kernel;

export namespace gcs::tools {

using gcs::kernel::ContextSnapshot;
using gcs::kernel::ModelSnapshot;

ModelSnapshot make_two_point_distance_model();
ModelSnapshot make_unsatisfied_two_point_distance_model();
ModelSnapshot make_two_component_distance_model();
ModelSnapshot make_missing_entity_reference_model();
ContextSnapshot make_whole_context_for(const ModelSnapshot& model);

}
