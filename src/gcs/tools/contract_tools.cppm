module;

export module gcs.contract_tools;

export import gcs.kernel;

export namespace gcs::tools {

ModelSnapshot makeTwoPointDistanceModel();
ContextSnapshot makeWholeContextFor(const ModelSnapshot& model);

}
