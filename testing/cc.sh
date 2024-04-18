#!/bin/bash

# Path Addition
export PATH=$PATH:/opt/intel/oneapi/compiler/latest/linux/bin-llvm/

# Vtune Repo
VTUNE_REPO="/home/sdp/workspace/anurag/fresh_attempt/applications.analyzers.vtune"

# Directory containing the .profraw files
PROFRAW_DIR="${VTUNE_REPO}/unit_tests/posix-x86_64"

# Output directory for the merged .profdata file
MERGED_PROFRAW="merged.profdata"

# Output directory for the lcov report
LCOV_REPORT_DIR="lcov_report_dir_cov"

# Create the output directory for the lcov report if it doesn't exist
mkdir -p $LCOV_REPORT_DIR

# Merge the .profraw files using llvm-profdata
llvm-profdata merge -sparse $PROFRAW_DIR/*/*.profraw -o $MERGED_PROFRAW

# Iterate over matching .so files and generate coverage report
for so_file in "$VTUNE_REPO"/install/lib64/*.so; do
    # Generate coverage report for each .so file
    llvm_cov_args+=("--object=$so_file")
done

# Generate coverage report using llvm-cov
llvm-cov show \
    --ignore-filename-regex="_sdks/*" \
    --output-dir="$LCOV_REPORT_DIR" \
    --format=html \
    --instr-profile="$MERGED_PROFRAW" \
    --project-title='VTune' \
    "${llvm_cov_args[@]}" \
    --show-directory-coverage
