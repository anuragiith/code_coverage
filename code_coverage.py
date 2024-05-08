import os
import subprocess
import logging
from component_info import component_info

class CodeCoverageReportGenerator:
    def __init__(self, component_so_map):
        self.component_so_map = component_so_map
        self.logger = self.setup_logger()
    
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
    
    def generate_merge_files(self, exclude_list, output_dir):
        """Generate merge files from default.profraw files."""
        merged_profdata_files = []
        
        for component_name, paths in self.component_info.items():
            if component_name not in exclude_list:
                try:
                    profraw_path = paths['profraw_path']
                    so_file_path = paths['so_file_path']
                except KeyError as e:
                    self.logger.warning(f"KeyError while accessing component information: {e}")
                    continue
                
                if not os.path.exists(profraw_path):
                    self.logger.warning(f"Profraw file not found for component '{component_name}' at path: {profraw_path}")
                    continue
                if not os.path.exists(so_file_path):
                    self.logger.warning(f"So file not found for component '{component_name}' at path: {so_file_path}")
                    continue
                    
                self.logger.info(f"Generating merge file for component '{component_name}'")
                merged_profdata_file = os.path.join(output_dir, f"{component_name}.profdata")
                try:
                    self.generate_merge_file(profraw_path, merged_profdata_file)
                    merged_profdata_files.append(merged_profdata_file)
                except Exception as e:
                    self.logger.error(f"Error generating merge file for component '{component_name}': {e}")
        return merged_profdata_files

    def generate_merge_file(self, so_file, merged_profdata_file):
        """Generate merge file for a single .so file."""
        command = ['llvm-profdata', 'merge', '-sparse', so_file, '-o', merged_profdata_file]
        try:
            subprocess.run(command, check=True)
            self.logger.info(f"Merge file generated: {merged_profdata_file}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error generating merge file: {e}")
    
    def generate_coverage_report(self, merged_profdata_file, output_dir):
        """Generate coverage report using llvm-cov."""
        output_file = os.path.join(output_dir, f"{os.path.basename(merged_profdata_file)}.html")
        command = ['llvm-cov', 'show',
                   '--ignore-filename-regex="_sdks/*"',
                   '--output-dir', output_dir,
                   '--format=html',
                   '--instr-profile', merged_profdata_file,
                   '--project-title=VTune',
                   '--show-directory-coverage']
        command.extend(['--object', self.component_so_map[os.path.splitext(os.path.basename(merged_profdata_file))[0]]])
        try:
            subprocess.run(command, check=True)
            self.logger.info(f"Coverage report generated: {output_file}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error generating coverage report: {e}")

# Example usage
if __name__ == "__main__":
    generator = CodeCoverageReportGenerator(component_info)
    directory_layout = '/path/to/some_path'
    exclude_list = ['component_to_exclude1', 'component_to_exclude2']
    output_dir = '/path/to/output_directory'
    merged_profdata_files = generator.generate_merge_files(directory_layout, exclude_list, output_dir)
    for merged_profdata_file in merged_profdata_files:
        generator.generate_coverage_report(merged_profdata_file, output_dir)
