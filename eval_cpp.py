from pathlib import Path
from safe_run import run
import os

def compare_outputs(output1: str, output2: str) -> bool:
    # Normalize both outputs by stripping whitespace at line ends and removing trailing line breaks
    normalized_output1 = '\n'.join(line.rstrip() for line in output1.rstrip().splitlines())
    normalized_output2 = '\n'.join(line.rstrip() for line in output2.rstrip().splitlines())
    
    return normalized_output1 == normalized_output2

def eval_stdin_stdout(code: str, inputs: list[str], outputs: list[str], filename: str, base_dir="./tmp"):
    assert len(inputs) == len(outputs), "Inputs and Outputs must have the same number of cases"
    
    os.makedirs(base_dir, exist_ok=True)
    full_fn = f"{base_dir}/{filename}.cpp"
    exec_fn = f"{base_dir}/{filename}.o"
    
    with open(full_fn, "w") as f:
        f.write(code)
    
    build_result = run(["g++", full_fn, "-o", exec_fn, "-std=c++17"])
    
    if build_result.exit_code != 0:
        return False, [{
            "status": "Compilation Error",
            "exit_code": build_result.exit_code,
            "stdout": build_result.stdout,
            "stderr": build_result.stderr,
        }]
    
    test_results = []
    
    for input_, output_ in zip(inputs, outputs):
        run_result = run([exec_fn], input_str=input_)
        if run_result.exit_code:
            test_results.append({
                "status": "Runtime Error",
                "exit_code": run_result.exit_code,
                "stdin": input_,
                "stdout": run_result.stdout,
                "stderr": run_result.stderr,
            })
            return False, test_results

        if compare_outputs(run_result.stdout, output_):
            test_results.append({
                "status": "Passed",
                "exit_code": run_result.exit_code,
                "stdin": input_,
                "stdout": run_result.stdout,
                "stderr": run_result.stderr,
            })
        else:
            test_results.append({
                "status": "Wrong Answer",
                "exit_code": run_result.exit_code,
                "stdout": run_result.stdout,
                "stderr": run_result.stderr,
                "answer": output_,
            })
            return False, test_results
    
    return True, test_results
        
        

def eval_script(path: Path):
    basename = ".".join(str(path).split(".")[:-1])
    build_result = run(["g++", path, "-o", basename, "-std=c++17"])
    if build_result.exit_code != 0:
        return {
            "status": "SyntaxError",
            "exit_code": build_result.exit_code,
            "stdout": build_result.stdout,
            "stderr": build_result.stderr,
        }

    run_result = run([basename])
    if "In file included from /shared/centos7/gcc/9.2.0-skylake/" in run_result.stderr:
        raise Exception("Skylake bug encountered")
    if "/4.8.2" in run_result.stderr:
        raise Exception("Ancient compiler encountered")
    if run_result.timeout:
        status = "Timeout"
    elif run_result.exit_code != 0:
        status = "Exception"
    else:
        status = "OK"
    return {
        "status": status,
        "exit_code": run_result.exit_code,
        "stdout": run_result.stdout,
        "stderr": run_result.stderr,
    }