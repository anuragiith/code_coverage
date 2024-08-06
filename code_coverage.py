import os
import subprocess
import logging
import json
import shutil
import pathlib as Path

PROFRAW_RELATIVE_PATH = "unit_tests/posix-x86_64"
SO_RELATIVE_PATH = "install/lib64"

class CodeCoverageReportGenerator:
    def __init__(self, root, components_file, exclude):
        self.root = root
        self.logger = self.setup_logger()
        self.component_version = self.get_component_version()
        self.component_map = self.read_components(components_file)
        # import sys; sys.exit()
        self.exclude = exclude
        self.failed_components = {}
        self.setup_code_coverage()
        self.profraw_files = self.collect_profraw_files()
        self.merged_profdata_file = self.generate_profdata_file()
        self.so_files = self.collect_so_files()

    def get_component_version(self):
        from sconstruct_reader import get_component_versions
        sconstruct_path = os.path.join(self.root, "SConstruct")
        print(sconstruct_path)
        try:
            component_versions = get_component_versions(sconstruct_path)
            if component_versions is not None:
                return component_versions
        except Exception as e:
            print(e)
            # TODO : Fallback mechanism
            print("Need fallback mechanism")

    def read_components(self, components_file):
        try:
            # Open the JSON file
            with open(components_file, 'r') as file:
                # Load JSON data from the file
                data = json.load(file)

                profraw_base_path = f"{self.root}/{PROFRAW_RELATIVE_PATH}"
                so_base_path = f"{self.root}/{SO_RELATIVE_PATH}"

                # Replace the placeholders in the JSON data
                for component, details in data.items():
                    if details['profraw_path']:
                        details['profraw_path'] = details['profraw_path'].format(base_path=profraw_base_path, version=self.component_version[component]['version'])
                    if details['so_file_path']:
                        details['so_file_path'] = details['so_file_path'].format(base_path=so_base_path)

                # Now you can use the updated data dictionary with the placeholders replaced
                self.logger.info(data)
            return data
        except FileNotFoundError as e:
            self.logger.error(f"Error: File '{components_file}' not found.")
            raise FileNotFoundError(f"Error: File '{components_file}' not found.") from e
        except json.JSONDecodeError:
            self.logger.error(f"Error: Unable to decode JSON data from file '{components_file}'.")
            raise json.JSONDecodeError(f"Error: Unable to decode JSON data from file '{components_file}'.") from e

    def setup_logger(self):
        """Configure logger to write messages to a log file."""
        logger = logging.getLogger('CodeCoverageReportGenerator')
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler('coverage_report_generator.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        return logger
    
    def setup_code_coverage(self):
        try:
            # Define code coverage directory paths
            self.code_coverage_dir = os.path.join(self.root, 'code_coverage')
            self.results_dir = os.path.join(self.code_coverage_dir, 'results')

            # Remove existing code coverage directory if it exists
            if os.path.exists(self.code_coverage_dir):
                shutil.rmtree(self.code_coverage_dir)

            # Create code coverage directory
            os.makedirs(self.code_coverage_dir)

            # Create results directory
            os.makedirs(self.results_dir)

            print("Code coverage directories initialized successfully.")
        except Exception as e:
            raise RuntimeError("Failed to initialize code coverage directories.") from e

    def collect_profraw_files(self):
        """Collect profraw files from default.profraw files."""
        all_profraw_files = []
        for component, paths in self.component_map.items():
            if "profraw_path" in paths and component not in self.exclude:
                profraw_path = os.path.join(self.root, paths["profraw_path"])
                if os.path.exists(profraw_path):
                    all_profraw_files.append(profraw_path)
                else:
                    self.failed_components[component] = profraw_path
                    self.logger.warning(f"No profraw file found for component '{component}' at: {profraw_path}")
        return all_profraw_files

    def collect_so_files(self):
        """Collect .so files from the specified directory."""
        all_so_files = []
        for component, paths in self.component_map.items():
            if "so_file_path" in paths and component not in self.exclude:
                so_file_path =  os.path.join(self.root, paths["so_file_path"])
                if os.path.exists(so_file_path):
                    all_so_files.append(so_file_path)
                else:
                    self.failed_components[component] = so_file_path
                    self.logger.warning(f"No .so file found for component '{component}' at: {so_file_path}")
        return all_so_files

    def generate_profdata_file(self):
        """Generate single profraw file from all profraw files."""
        merged_profdata_file = os.path.join(self.code_coverage_dir, "merged.profdata")
        command = ['llvm-profdata', 'merge', '-sparse', *self.profraw_files, '-o', merged_profdata_file]
        try:
            subprocess.run(command, check=True)
            # self.logger.info(f"Profdata command: {command}")
            self.logger.info(f"Merge file generated: {merged_profdata_file}")
            return merged_profdata_file
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error generating merge file: {e}")
            raise e
    
    def generate_coverage_report(self, llvm_cov_path):
        """Generate coverage report using llvm-cov."""
        command = [f'{llvm_cov_path}', 'show',
                   '--ignore-filename-regex="_sdks/*"',
                   '--output-dir', os.path.join(self.code_coverage_dir, "results"),
                   '--format=html',
                   '--instr-profile', self.merged_profdata_file,
                   '--project-title=VTune',
                   '--show-directory-coverage']
        
        for so_file in self.so_files:
            command.append(f'--object={so_file}')

        self.logger.info(f"Report Generation command: {command}")

        try:
            subprocess.run(command, check=True)
            self.logger.info(f"Coverage report generated.")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error generating coverage report: {e}")

# Example usage
if __name__ == "__main__":
    root = os.environ.get("REPO_PATH", "/home/sdp/workspace/anurag/fresh_attempt/applications.analyzers.vtune")
    llvm_cov = os.environ.get("LLVM-COV", "/home/sdp/intel/oneapi/compiler/2024.1/bin/compiler/llvm-cov")
    components_file = os.path.join(root, "component_info.json")
    exclude = ['clpt']

    generator = CodeCoverageReportGenerator(root, components_file, exclude)
    generator.generate_coverage_report(llvm_cov)
