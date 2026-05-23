import gcs.contract_tools;

#include <gtest/gtest.h>

namespace {

namespace tools = gcs::tools;

}  // namespace

TEST(ModuleDependencyContract, RejectsForbiddenBoundaryImport) {
    auto audit = tools::audit_module_dependencies(
        tools::DependencyAuditRequest{
            {tools::ModuleImport{"gcs.kernel", "gcs.viewer_bridge"}}});

    EXPECT_FALSE(audit.payload.valid);
    ASSERT_EQ(audit.payload.violations.size(), 1U);
    EXPECT_EQ(audit.payload.violations.front().code,
              "tools.dependency.forbidden_boundary_import");
}

TEST(ModuleDependencyContract, AllowsBoundaryToConsumeRuntimeContracts) {
    auto audit = tools::audit_module_dependencies(
        tools::DependencyAuditRequest{
            {tools::ModuleImport{"gcs.viewer_bridge", "gcs.session_runtime"}}});

    EXPECT_TRUE(audit.payload.valid);
    EXPECT_TRUE(audit.payload.violations.empty());
}
