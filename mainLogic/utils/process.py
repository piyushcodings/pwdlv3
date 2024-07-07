import subprocess
import re
import sys
import os
def shell(command, filter=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, progress_callback=None, handleProgress=None, inline_progress=False, return_out=False,cwd=os.getcwd()):
    import os

    # Set PYTHONUNBUFFERED environment variable
    os.environ['PYTHONUNBUFFERED'] = '1'

    command = to_list(command)

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8', universal_newlines=True, cwd=cwd)

        output_lines = []
        while True:
            try:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break

                output = output.strip()
                if output:
                    output_lines.append(output)

                    if filter is not None and re.search(filter, output):
                        # Call the progress callback with the filtered output
                        if progress_callback:
                            if handleProgress:
                                progress_callback(handleProgress(output))
                            else:
                                progress_callback(output)

                    if inline_progress:
                        # Update progress in the same line
                        sys.stdout.write('\r' + output.strip())
                        sys.stdout.flush()
                    else:
                        # Print output normally
                        if stdout is not None and stdout != '':
                            print(output)

            except UnicodeEncodeError:
                sys.stdout.write("\rUnicodeEncodeError")
                sys.stdout.flush()
                pass

        # Wait for the process to complete and get the return code
        return_code_value = process.wait()

        # Return output only if return_code flag is False
        if not return_out:
            return return_code_value
        else:
            # Return both output and return code
            return return_code_value, output_lines

    except Exception as e:
        print(f"Error: {e}")
        if not return_out:
            return []
        else:
            return -1, []

def to_list(variable):
    if isinstance(variable, list):
        return variable
    elif variable is None:
        return []
    else:
        # Convert to string and then to list by splitting at whitespaces
        return variable.split()
