#pragma once

#include <cstdlib>
#include <iostream>

#define FHI_REQUIRE(condition) \
    do { \
        if (!(condition)) { \
            std::cerr << "FAILED: " << __FILE__ << ":" << __LINE__ << ": " #condition "\n"; \
            std::exit(1); \
        } \
    } while (false)
