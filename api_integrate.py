import os

scripts = ["api_integrate_abs_desc.py","api_integrate_dept.py","api_integrate_desc.py","api_integrate_mod_dept.py","api_integrate_mod_subdept.py","api_integrate_subdept.py",]

# Command to run the code
command_template = "python {}"

for script in scripts:
    command = command_template.format(script)
    os.system(command)