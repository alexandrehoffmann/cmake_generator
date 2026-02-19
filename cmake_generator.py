import os
import yaml
import re

glob_language_complier_options = []
glob_obj_library = []

def get_compiler_id(compiler):
	match compiler:
		case "gnu":
			return "GNU"
		case "clang":
			return "Clang"
		case "clang_gnu" | "gnu_clang":
			return "GNU,Clang"
		case "msvc":
			return "MSVC"

default_git_tag          = "main"
default_include_dir      = "include"
default_src_dir          = "src"
default_build_tests      = False
default_build_demos      = False
default_version          = "1.0.0"
default_languages        = {'languages': {'CXX': {'standard': 20}}}
default_language_options = []

def write_section(fout, secion_name):	
	fout.write(u'########################################################################\n')
	fout.write(u'####' + secion_name.center(64) + u'####\n') 
	fout.write(u'########################################################################\n') 

def to_camel(txt):
	return re.sub(r'(?<!^)(?=[A-Z])', '_', txt).upper()

def load_config(file_path="config.yaml"):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def create_folders(config):
	os.makedirs(config.get("include_dir", default_include_dir), exist_ok=True)
	os.makedirs(config.get("src_dir", default_src_dir), exist_ok=True)
	os.makedirs("cmake", exist_ok=True)
	
	if config.get("build_tests", default_build_tests):
		os.makedirs("tests", exist_ok=True)
	if config.get("demos", default_build_demos):
		os.makedirs("demos", exist_ok=True)

def write_header(fout, config):
	fout.write(u'cmake_minimum_required(VERSION 3.20)\n')
	fout.write(u'\n')
	
def write_project(fout, config):
	write_section(fout, "Project metadata") 
	fout.write(u'\n') 
	fout.write(u'project(' + config["project_name"] + u'\n')
	fout.write(u'	VERSION ' + config.get("version", default_version) + u'\n')
	fout.write(u'	LANGUAGES\n')
	for language in config.get("languages", default_languages):
		fout.write(u'		' + language + u'\n')
	fout.seek(fout.tell() - 1, os.SEEK_SET)
	fout.write(u')\n\n') 
	
def write_variables(fout, config):
	write_section(fout, "Variables")
	fout.write(u'\n')
	fout.write(u'if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)\n')
	fout.write(u'	set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Choose the type of build." FORCE)\n')
	fout.write(u'\n')
	fout.write(u'	set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "RelWithDebInfo" "MinSizeRel")\n')
	fout.write(u'endif()\n')
	fout.write(u'\n')
	fout.write(u'set(SAN_FLAGS -fsanitize=address -fsanitize=undefined -fno-omit-frame-pointer)\n')
	fout.write(u'\n')
	
	glob_language_complier_options.clear()
	
	for language, language_data in config.get("languages", default_languages).items():
		for compiler_opts, compiler_opts_data in config.get(language + "_options", default_language_options).items(): 
			if compiler_opts_data:
				glob_language_complier_options.append([compiler_opts, language.upper()])
				
			fout.write(u'set(' + to_camel(config["project_name"]) + u'_' + compiler_opts.upper() + u'_' + language + u'_COMPILE_OPTIONS \n')
			for option in compiler_opts_data:
				fout.write(u'	' + option + '\n')
			fout.seek(fout.tell() - 1, os.SEEK_SET)
			fout.write(u')\n\n') 
	
def write_options(fout, config):
	write_section(fout, "Options")
	fout.write(u'\n')
	#default options
	fout.write(u'option(' + to_camel(config["project_name"]) + '_ENABLE_SANITIZERS "Enable sanitizers in Debug builds" OFF)\n')
	fout.write(u'option(' + to_camel(config["project_name"]) + '_BUILD_DEMO        "Build demo executable" OFF)\n')
	fout.write(u'option(' + to_camel(config["project_name"]) + '_BUILD_DOC         "Build Doxygen documentation" OFF)\n')
	fout.write(u'option(' + to_camel(config["project_name"]) + '_BUILD_TESTS       "Build unit tests" OFF)\n')
	# user specified options
	for option, data in config["options"].items():
		default = "ON" if data["default"] else "OFF"
		fout.write(u'option(' + to_camel(config["project_name"]) + '_' + option.upper() + u' "' + data["description"] + u'" ' + default + u')\n')
	fout.write(u'\n')

def write_dependencies(fout, config):
	write_section(fout, "Dependencies")
	fout.write(u'\n')
	for dependency, data in config["dependencies"].items():
		if data is None:
			fout.write(u'find_package(' + dependency + u' REQUIRED)\n')
		elif "version" in data:
			if "git" in data:
				fout.write(u'find_package(' + dependency + u' ' + data["version"] + u' QUIET CONFIG)\n')
			else:
				fout.write(u'find_package(' + dependency + u' ' + data["version"] + 'u REQUIRED)\n')
		else:
			if "git" in data:
				fout.write(u'find_package(' + dependency + u' QUIET)\n')
			else:
				fout.write(u'find_package(' + dependency + u' REQUIRED)\n')
	fout.write(u'\n')
	fout.write(u'include(FetchContent)\n')
	fout.write(u'\n')
	for dependency, data in config["dependencies"].items():
		if data is not None and "git" in data:
			fout.write(u'if (NOT ' + dependency + '_FOUND)\n')
			fout.write(u'	message(STATUS "' + dependency + ' not found — falling back to FetchContent.")\n')
			fout.write(u'	\n')
			fout.write(u'	FetchContent_Declare(' + dependency + u' GIT_REPOSITORY ' + data["git"] + u' GIT_TAG ' + data.get("tag", default_git_tag) + u')\n')
			fout.write(u'	FetchContent_MakeAvailable(' + dependency + ')\n')
			fout.write(u'else()\n')
			fout.write(u'	message(STATUS "Found ' + dependency + ' using system installation.")\n')
			fout.write(u'endif()\n')
			fout.write(u'\n')
		
def write_targets(fout, config):
	write_section(fout, "Targets")
	fout.write(u'\n')
	fout.write(u'add_library(' + config["project_name"] + '_options  INTERFACE)\n')
	fout.write(u'add_library(' + config["project_name"] + '_includes INTERFACE)\n')
	
	glob_obj_library.clear()
	
	if "libraries" in config:
		for library, data in config["libraries"].items():
			if "sources" in data:
				glob_obj_library.append(library)
				fout.write(u'add_library(' + library + ' OBJECT)\n')
			else:
				fout.write(u'add_library(' + library + u' INTERFACE)\n')
	fout.write(u'\n')
	fout.write(u'add_library(' + config["project_name"] + '::options ALIAS ' + config["project_name"] + '_options)\n')
	fout.write(u'add_library(' + config["project_name"] + '::includes ALIAS ' + config["project_name"] + '_includes)\n')
	for library in config.get("libraries", []):
		fout.write(u'add_library(' + config["project_name"] + '::' + library + u' ALIAS ' + library + u')\n')
	fout.write(u'\n')
	if "executables" in config:
		for executable, data in config["executables"].items():
			fout.write(u'add_executable(' + executable + ')\n')
	fout.write(u'\n')
	
def write_sources(fout, config):
	write_section(fout, "Sources")
	fout.write(u'\n')
	for targetType in ["libraries", "executables"]:
		if targetType in config:
			for target, target_data in config[targetType].items():
				if "sources" in target_data:
					fout.write(u'target_sources(' + target + u' PRIVATE\n')
					for source in target_data["sources"]:
						if "folder" in target_data:
							fout.write(u'	' + config.get("src_dir", default_src_dir) + u'/' + target_data["folder"] + u'/' + source + '\n')
						else:
							fout.write(u'	' + config.get("src_dir", default_src_dir) + u'/' + source + '\n')
					fout.seek(fout.tell() - 1, os.SEEK_SET)
					fout.write(u')\n')
		fout.write(u'\n') 
	for executable in config.get("executables", []):
		if glob_obj_library:
			fout.write(u'target_sources(' + executable + ' PRIVATE\n')
			for obj_library in glob_obj_library:
				fout.write(u'	$<TARGET_OBJECTS:' + obj_library +'>\n')
	fout.seek(fout.tell() - 1, os.SEEK_SET)
	fout.write(u')\n')
	fout.write(u'\n')
	
def write_include_directories(fout, config):
	target = config["project_name"] + '::includes'
	
	write_section(fout, "Includes")
	fout.write(u'\n')
	if "install" in config:
		fout.write(u'target_include_directories(' + target + u' INTERFACE\n')
		fout.write(u'	$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/' + config.get('include_dir', default_include_dir) + '>\n')
		fout.write(u'	$<INSTALL_INTERFACE:' + config.get('include_dir', default_include_dir) + '>)\n')
	else:
		fout.write(u'target_include_directories(' + target + u' INTERFACE $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/' + config.get('include_dir', default_include_dir) + '>)\n')
	fout.write(u'\n')

def write_compile_options(fout, config):
	write_section(fout, "Compile options")
	fout.write(u'\n')
	for language, language_data in config.get("languages", default_languages).items():
		fout.write(u'target_compile_features(' + config["project_name"] +  u'::options INTERFACE ' + language.lower() + '_std_' + str(language_data["standard"]) + ')\n')
	fout.write(u'\n')
	if glob_language_complier_options:
		fout.write(u'target_compile_options(' + config["project_name"] + '::options INTERFACE\n')
		for compiler, language in glob_language_complier_options:
			fout.write(u'	$<$<' + language + '_COMPILER_ID:' + get_compiler_id(compiler) + '>:${' + to_camel(config["project_name"]) + '_' + compiler.upper() + '_' + language + u'_COMPILE_OPTIONS}>\n')
	fout.seek(fout.tell() - 1, os.SEEK_SET)
	fout.write(u')\n')
	fout.write(u'\n')
	fout.write(u'if(MY_PROJECT_ENABLE_SANITIZERS)\n')
	fout.write(u'	target_compile_options(' + config["project_name"] +  u'::options INTERFACE $<$<CONFIG:Debug>:${SAN_FLAGS})\n')
	fout.write(u'endif()\n')
	fout.write(u'\n')
	fout.write(u'if(MY_PROJECT_USE_NATIVE_OPT)\n')
	fout.write(u'	target_compile_options(' + config["project_name"] +  u'::options INTERFACE -march=native -mtune=native)\n')
	fout.write(u'endif()\n')
	fout.write(u'\n')
	for targetType in ["libraries", "executables"]:
		if targetType in config:
			for target, target_data in config[targetType].items():
				target_options = [] 
				for language in config.get("languages", default_languages):
					if language + "_options" in target_data:
						target_options = target_options +  target_data[language + "_options"]
				if target_options:
					fout.write(u'target_compile_options(' + target + ' PRIVATE\n')
					for option in target_options:
						fout.write(u'	' + option + '\n')
					fout.seek(fout.tell() - 1, os.SEEK_SET)
					fout.write(u')\n\n')

def write_link_libraries(fout, config):
	write_section(fout, "Link")
	fout.write(u'\n')
	if "libraries" in config:
		for target, data in config["libraries"].items():
			if target in glob_obj_library:
				fout.write(u'target_link_libraries(' + target + '\n')
				fout.write(u'	PRIVATE ' + config["project_name"] + '::options\n')
				fout.write(u'	PUBLIC  ' + config["project_name"] + '::includes\n')
				for dependency in data.get("public_dependencies", []):
					fout.write('	PUBLIC ' + dependency + '\n')
				for dependency in data.get("private_dependencies", []):
					fout.write('	PRIVATE ' + dependency + '\n')
				fout.seek(fout.tell() - 1, os.SEEK_SET)
				fout.write(u')\n\n')
	if "executables" in config:
		for target, data in config["executables"].items():
			fout.write(u'target_link_libraries(' + target + u' PRIVATE\n')
			fout.write(u'	' + config["project_name"] + u'::options\n')
			fout.write(u'	' + config["project_name"] + u'::includes\n')
			for dependency in data.get("dependencies", []):
				fout.write(u'	' + dependency + '\n')
			fout.seek(fout.tell() - 1, os.SEEK_SET)
			fout.write(u')\n\n')
	fout.write(u'if(MY_PROJECT_ENABLE_SANITIZERS)\n')
	fout.write(u'	target_link_options(' + config["project_name"] +  u'::options INTERFACE $<$<CONFIG:Debug>:${SAN_FLAGS})\n')
	fout.write(u'endif()\n\n')

def write_tests(fout, config):
	write_section(fout, "Tests")
	fout.write(u'\n')
	fout.write(u'if(' + to_camel(config["project_name"]) + u'_BUILD_TESTS)\n')
	fout.write(u'	enable_testing()\n')
	fout.write(u'	find_package(GTest REQUIRED)\n')
	fout.write(u'	add_subdirectory(tests)\n')
	fout.write(u'endif()\n\n')

if __name__ == "__main__":
	config = load_config()
	create_folders(config)
	
	with open("CMakeLists.txt", "w") as fout:
		write_header(fout, config)
		write_project(fout, config)
		write_options(fout, config)
		write_variables(fout, config)
		write_dependencies(fout, config)
		write_targets(fout, config)
		write_sources(fout, config)
		write_include_directories(fout, config)
		write_link_libraries(fout, config)
		write_compile_options(fout, config)
		write_tests(fout, config)
