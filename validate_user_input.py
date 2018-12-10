import glob
import ipaddress
import sys
import yaml


SITE_CODES = ['sea']
DEV_TYPES = ['nxos', 'eos']


def load_yaml_vars(infile):
    """Load YAML Variable file into dict

    Args:
        infile: (str) name of input file

    Kwargs:
        N/A

    Returns:
        var_dict: (dict) dict representation of Variable file
    """
    with open(infile, 'r') as f:
        var_dict = yaml.safe_load(f)

    return(var_dict)


def validate_ip(ip):
    """Prove input string is valid IP Address

    Args:
        ip: (str) string representation of suspected IP Address

    Kwargs:
        N/A

    Returns:
        bool True if valid IP; otherwise False
    """
    try:
        ipaddress.IPv4Interface(ip)
    except Exception as e:
        print(e)
        return(False)
    return(True)


def validate_vlan(vlan):
    """Prove input string is valid VLAN ID

    Args:
        vlan: (str) string representation of suspected VLAN ID

    Kwargs:
        N/A

    Returns:
        bool True if valid vlan; otherwise False
    """
    vlan = int(vlan)
    if vlan < 0 or vlan > 4094:
        return(False)
    else:
        return(True)


def validate_descr(descr):
    """Prove input string is valid (per some reqs) description

    Description should follow the below format:
    [site code]-[device type][id as an integer] [free form text]

    Args:
        descr: (str) description

    Kwargs:
        N/A

    Returns:
        bool True if valid descr; otherwise False
    """
    split_descr = descr.split('-')

    if '-' not in descr:
        print(f'Description {descr} is not formatted with hyphens properly.')
        return(False)
    elif not split_descr[0].startswith(tuple([f'{site_code}' for site_code in SITE_CODES])):
        print(f'Description {descr} does not start with valid site code.')
        return(False)
    elif not split_descr[1].startswith(tuple([f'{dev_type}' for dev_type in DEV_TYPES])):
        print(f'Description {descr} does not identify valid device type.')
        return(False)
    try:
        int(split_descr[2].split()[0])
    except ValueError:
        print(f'Description {descr} does not properly indicate device id.')
        return(False)

    return(True)


def get_recursively(in_dict, search_pattern):
    """
    Takes a dict with nested lists and dicts,
    and searches all dicts for a key of the field
    provided.
    """
    fields_found = []

    for key, value in in_dict.items():
        if key == search_pattern:
            fields_found.append(value)
        elif isinstance(value, dict):
            results = get_recursively(value, search_pattern)
            for result in results:
                fields_found.append(result)
    return(fields_found)


if __name__ == '__main__':
    # Empty list to contain all policy exceptions
    policy_exceptions = []

    # Capture all host/group variables using glob -- will grab any ".yaml" file
    # in any directory ending in _var
    var_files = glob.glob('*_vars/*.yaml')

    # Iterate through all variabble files
    for var_file in var_files:
        with open(var_file, 'r') as f:
            # Load YAML to Python Dict for parsing
            in_vars = yaml.safe_load(f)

        # Capture all values of keys "ip", "vlan", and "description"
        ips = get_recursively(in_vars, 'ip')
        vlans = get_recursively(in_vars, 'vlan')
        descrs = get_recursively(in_vars, 'description')

        # Validate IP addresses
        ip_violations = [ip for ip in ips if validate_ip(ip) is False]

        # Validate VLAN IDs
        vlan_violations = [vlan for vlan in vlans if validate_vlan(vlan) is False]

        # Validate Descriptions
        descr_violations = [descr for descr in descrs if validate_descr(descr) is False]

        if any((ip_violations, vlan_violations, descr_violations)):
            policy_exceptions.append((f.name, ip_violations,
                                      vlan_violations, descr_violations))

    if len(policy_exceptions) > 0:
        sys.exit(1)
    else:
        sys.exit(0)
