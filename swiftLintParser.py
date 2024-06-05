from optparse import OptionParser
import re

input_files_regex = r"[\+\w./]+\.swift"
warning_files_regex = r"[\w./\+\-]+\.swift"
warning_violation_regex = r"warning:\s*(.*?)\s*Violation"

def parse_file(swiftlint_file: str):
    input_files_array = []
    violation_files_dict = {}
    warnings_count = 0
    with open(swiftlint_file) as swiftlint_file:
        for line in swiftlint_file:
            if 'Linting' in line:
                match = re.search(input_files_regex, line)
                if match:
                    input_files_array.append(match.group())
            elif 'warning:' in line:
                warning_file_match = re.search(warning_files_regex, line)
                warning_violation_match = re.search(warning_violation_regex, line)
                if warning_file_match and warning_violation_match:
                    warnings_count += 1
                    warning_file_match_value = warning_file_match.group()
                    warning_violation_match_value = warning_violation_match.group(1)
                    if warning_file_match_value in violation_files_dict:
                        current_violations = violation_files_dict[warning_file_match_value]
                        current_violations.append(warning_violation_match_value)
                        violation_files_dict[warning_file_match_value] = current_violations
                    else:
                        violation_files_dict[warning_file_match_value] = [warning_violation_match_value]
                else:
                    raise Exception(f"Failed to extract warning details from: {line}")
    
    print(f"Found {warnings_count} warnings!")

    file_index = 1
    file_count = len(input_files_array)
    processed_violation_files = []
    for input_file in input_files_array:
        input_file_is_violation = False
        for violation_file in violation_files_dict.keys():
            if input_file in violation_file and violation_file not in processed_violation_files:
                processed_violation_files.append(violation_file)
                violations = violation_files_dict[violation_file]
                violation_count = len(violations)
                unique_violations = '\n'.join(list(set(violations)))
                print(f"'{input_file}' ({file_index}/{file_count}),{violation_count},\"{unique_violations}\"")
                input_file_is_violation = True
                break
        if input_file_is_violation == False:
            print(f"'{input_file}' ({file_index}/{file_count}),0")
        
        file_index += 1


def main():
    parser = OptionParser(usage="usage: %prog")
    parser.add_option("--swiftlint-file", dest="swiftlint_file")
    (opts, args) = parser.parse_args()

    parse_file(opts.swiftlint_file)

if __name__ == '__main__':
    main()