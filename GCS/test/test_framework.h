#pragma once

#include <iostream>
#include <string>
#include <cmath>

static int g_tests_run = 0;
static int g_tests_passed = 0;

#define GCS_ASSERT(cond, msg) do { \
    g_tests_run++; \
    if (cond) { \
        g_tests_passed++; \
        std::cout << "[PASS] " << msg << "\n"; \
    } else { \
        std::cerr << "[FAIL] " << msg << " at " << __FILE__ << ":" << __LINE__ << "\n"; \
    } \
} while(0)

#define GCS_ASSERT_EQ(a, b, msg) GCS_ASSERT((a) == (b), msg)
#define GCS_ASSERT_NE(a, b, msg) GCS_ASSERT((a) != (b), msg)
#define GCS_ASSERT_GT(a, b, msg) GCS_ASSERT((a) > (b), msg)
#define GCS_ASSERT_LT(a, b, msg) GCS_ASSERT((a) < (b), msg)
#define GCS_ASSERT_GE(a, b, msg) GCS_ASSERT((a) >= (b), msg)
#define GCS_ASSERT_LE(a, b, msg) GCS_ASSERT((a) <= (b), msg)

#define GCS_ASSERT_NEAR(a, b, eps, msg) GCS_ASSERT(std::abs((a) - (b)) < (eps), msg)

#define GCS_TEST_SUMMARY() do { \
    std::cout << "\n=== " << g_tests_passed << "/" << g_tests_run << " tests passed ===\n"; \
    return (g_tests_passed == g_tests_run) ? 0 : 1; \
} while(0)
