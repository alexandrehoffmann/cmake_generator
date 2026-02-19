"""
Tests for CMake generator
"""

import unittest
import tempfile
import os
from pathlib import Path
from cmake_generator.generator import CMakeGenerator


class TestCMakeGenerator(unittest.TestCase):
    """Test cases for CMakeGenerator"""

    def test_basic_project(self):
        """Test basic project generation"""
        config = {
            'project': {
                'name': 'TestProject',
                'version': '1.0.0',
                'languages': ['CXX'],
                'cmake_minimum': '3.15'
            }
        }
        
        generator = CMakeGenerator(config)
        output = generator.generate()
        
        self.assertIn('cmake_minimum_required(VERSION 3.15)', output)
        self.assertIn('project(TestProject', output)
        self.assertIn('VERSION 1.0.0', output)
        self.assertIn('LANGUAGES CXX', output)

    def test_cpp_standard(self):
        """Test C++ standard setting"""
        config = {
            'compiler': {
                'cpp_standard': 17
            }
        }
        
        generator = CMakeGenerator(config)
        output = generator.generate()
        
        self.assertIn('set(CMAKE_CXX_STANDARD 17)', output)
        self.assertIn('set(CMAKE_CXX_STANDARD_REQUIRED ON)', output)

    def test_executable_target(self):
        """Test executable target generation"""
        config = {
            'targets': [
                {
                    'name': 'myapp',
                    'type': 'executable',
                    'sources': ['main.cpp', 'app.cpp']
                }
            ]
        }
        
        generator = CMakeGenerator(config)
        output = generator.generate()
        
        self.assertIn('add_executable(myapp main.cpp app.cpp)', output)

    def test_library_target(self):
        """Test library target generation"""
        config = {
            'targets': [
                {
                    'name': 'mylib',
                    'type': 'library',
                    'library_type': 'static',
                    'sources': ['lib.cpp']
                }
            ]
        }
        
        generator = CMakeGenerator(config)
        output = generator.generate()
        
        self.assertIn('add_library(mylib STATIC lib.cpp)', output)

    def test_dependencies(self):
        """Test dependency generation"""
        config = {
            'dependencies': [
                {
                    'name': 'Boost',
                    'version': '1.70',
                    'components': ['system', 'filesystem']
                }
            ]
        }
        
        generator = CMakeGenerator(config)
        output = generator.generate()
        
        self.assertIn('find_package(Boost 1.70 COMPONENTS system filesystem)', output)

    def test_target_with_dependencies(self):
        """Test target with linked dependencies"""
        config = {
            'targets': [
                {
                    'name': 'myapp',
                    'type': 'executable',
                    'sources': ['main.cpp'],
                    'dependencies': ['Boost::system', 'fmt::fmt']
                }
            ]
        }
        
        generator = CMakeGenerator(config)
        output = generator.generate()
        
        self.assertIn('target_link_libraries(myapp PRIVATE Boost::system fmt::fmt)', output)

    def test_install_rules(self):
        """Test installation rules generation"""
        config = {
            'install': {
                'targets': ['myapp', 'mylib'],
                'headers_dir': 'include',
                'destination': 'bin'
            }
        }
        
        generator = CMakeGenerator(config)
        output = generator.generate()
        
        self.assertIn('install(TARGETS myapp mylib DESTINATION bin)', output)
        self.assertIn('install(DIRECTORY include/ DESTINATION include)', output)

    def test_from_yaml(self):
        """Test loading from YAML file"""
        yaml_content = """
project:
  name: YAMLTest
  version: 2.0.0
  
compiler:
  cpp_standard: 20
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            yaml_path = f.name
        
        try:
            generator = CMakeGenerator.from_yaml(yaml_path)
            output = generator.generate()
            
            self.assertIn('YAMLTest', output)
            self.assertIn('VERSION 2.0.0', output)
            self.assertIn('set(CMAKE_CXX_STANDARD 20)', output)
        finally:
            os.unlink(yaml_path)

    def test_write_to_file(self):
        """Test writing to file"""
        config = {
            'project': {
                'name': 'FileTest',
                'version': '1.0.0'
            }
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'CMakeLists.txt')
            generator = CMakeGenerator(config)
            generator.write_to_file(output_path)
            
            self.assertTrue(os.path.exists(output_path))
            
            with open(output_path, 'r') as f:
                content = f.read()
                self.assertIn('FileTest', content)

    def test_warnings_extra(self):
        """Test compiler warnings setting"""
        config = {
            'compiler': {
                'warnings': 'extra'
            }
        }
        
        generator = CMakeGenerator(config)
        output = generator.generate()
        
        self.assertIn('if(MSVC)', output)
        self.assertIn('add_compile_options(/W4)', output)
        self.assertIn('add_compile_options(-Wall -Wextra -Wpedantic)', output)


if __name__ == '__main__':
    unittest.main()
