CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -Wpedantic -Iinclude
BUILD_DIR ?= build

LIB_SRCS := \
	src/Hypergraph.cpp \
	src/ImmersionFunction.cpp \
	src/Matching.cpp \
	src/Parser.cpp \
	src/QuickImmersion.cpp

TEST_SRCS := \
	tests/test_hypergraph.cpp \
	tests/test_immersion_function.cpp \
	tests/test_matching.cpp \
	tests/test_quick_immersion.cpp

.PHONY: all test clean

all: $(BUILD_DIR)/fhi_cli $(BUILD_DIR)/fhi_tests

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(BUILD_DIR)/fhi_cli: $(LIB_SRCS) src/main.cpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(LIB_SRCS) src/main.cpp -o $@

$(BUILD_DIR)/fhi_tests: $(LIB_SRCS) $(TEST_SRCS) | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(LIB_SRCS) $(TEST_SRCS) -o $@

test: $(BUILD_DIR)/fhi_tests
	$(BUILD_DIR)/fhi_tests

clean:
	rm -rf $(BUILD_DIR)
