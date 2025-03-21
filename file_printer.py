import sys
import os
import os.path as osp
import subprocess


ARGS = {
    # 'docs' : {
    #     'value_arg' : ['', ' --dpi 50'],
    #     'added' : [' --dpi 50'],
    #     'added_default' : ['', ' --dpi 25'],
    #     'overwrite_all' : ['', ' --dpi 10'],
    #     'overwrite_default' : ['', ' --dpi 10'],
    #     'args_default' : [' --help'],
    #     'args_all' : [' --help'],
    #     'args_none' : ['', ' --help', ' --dpi 50'],
    # },
    'examples' : {
        'canvas' : [
            ' --cscale_colour royalblue --dpi 50',
            ' --cscale_colour gold --figsize 10 10',
            ' --cscale_colour crimson --ymax 1',
        ],
    },
}

def run_and_print(folder, file):
    os.system(f'cp {osp.join(folder, file)} __{file}')
    no_ext_file = osp.splitext(file)[0]
    output_string = '\n'
    for args in ARGS.get(folder, {}).get(no_ext_file, ['']):
        output_string += f'$ python {osp.join(folder, file)}{args}\n'
        try:
            command_output = subprocess.check_output(
                f'python3 __{file}{args}',
                shell=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            print('#'*10)
            print(f'Problem with file {folder}, {file}')
            print('#'*10)
            command_output = '\n'
        assert command_output.endswith('\n')
        command_output = command_output[:-1]
        for line in command_output.split('\n'):
            output_string += f'(_>_) {line}\n'
        output_string += '\n'
    assert output_string.endswith('\n')
    output_string = output_string[:-1]
    with open(osp.join(folder, no_ext_file + '.txt'), 'w') as output:
        output.write(output_string)
    os.system(f'rm __{file}')

if __name__ == '__main__':
    for folder in ARGS:
        for file in os.listdir(folder):
            if file.endswith('.py'):
                run_and_print(folder, file)