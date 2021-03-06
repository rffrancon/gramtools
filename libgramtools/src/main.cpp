#include <iostream>

#include <boost/program_options/variables_map.hpp>
#include <boost/program_options/parsers.hpp>
#include <boost/variant/variant.hpp>
#include <boost/variant/get.hpp>
#include <boost/filesystem.hpp>

#include <sdsl/bit_vectors.hpp>
#include <omp.h>

#include "prg/prg.hpp"
#include "common/timer_report.hpp"

#include "build/build.hpp"
#include "build/parameters.hpp"

#include "quasimap/quasimap.hpp"
#include "quasimap/parameters.hpp"

#include "main.hpp"


namespace po = boost::program_options;
namespace fs = boost::filesystem;
using namespace gram;


int main(int argc, const char *const *argv) {
    Parameters parameters = {};
    Commands command;
    std::tie(parameters, command) = parse_command_line_parameters(argc, argv);
    
    std::cout << "maximum thread count: " << parameters.maximum_threads << std::endl;
    omp_set_num_threads(parameters.maximum_threads);

    switch (command) {
        case Commands::build:
            commands::build::run(parameters);
            break;
        case Commands::quasimap:
            commands::quasimap::run(parameters);
            break;
    }
    return 0;
}


std::pair<Parameters, Commands> gram::parse_command_line_parameters(int argc, const char *const *argv) {
    po::options_description global("Global options");
    global.add_options()
                  ("debug", "Turn on debug output")
                  ("command", po::value<std::string>(), "command to execute")
                  ("subargs", po::value<std::vector<std::string> >(), "Arguments for command");

    po::positional_options_description pos;
    pos.add("command", 1)
       .add("subargs", -1);

    po::variables_map vm;

    po::parsed_options parsed =
            po::command_line_parser(argc, argv)
                    .options(global)
                    .positional(pos)
                    .allow_unregistered()
                    .run();

    po::store(parsed, vm);
    std::string cmd = vm["command"].as<std::string>();

    if (cmd == "build") {
        auto parameters = commands::build::parse_parameters(vm, parsed);
        return std::make_pair(parameters, Commands::build);
    } else if (cmd == "quasimap") {
        auto parameters = commands::quasimap::parse_parameters(vm, parsed);
        return std::make_pair(parameters, Commands::quasimap);
    }

    // unrecognised command
    throw po::invalid_option_value(cmd);
}
