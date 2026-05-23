module;

export module gcs.contract_tools;

export import gcs.kernel;

export namespace gcs::tools {

using gcs::kernel::ContextSnapshot;
using gcs::kernel::ModelSnapshot;

ModelSnapshot make_two_point_distance_model();
ContextSnapshot make_whole_context_for(const ModelSnapshot& model);

}
