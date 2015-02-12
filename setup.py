from distutils.core import setup

setup(
    name = "brocade_nova_listener",
    version = "1.0",
    author = "Pattabi Ayyasami",
    author_email = "pattabi@brocade.com",
    description = "Brocade Nova Listener",
    url = "http://www.brocade.com",
    long_description = "Brocade Nova Listener for Load Balancer VM Instances",
    packages = ["brocade_nova_listener"],
    scripts = ["scripts/brocade_nova_listener"],
    data_files = [("/etc/neutron/services/loadbalancer/brocade", ["conf/brocade_nova_listener.ini"])],
    license = "Apache Software License",
    platforms = ["Linux"],
    classifiers = [
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Environment :: OpenStack",
        "License :: OSI Approved :: Apache Software License"
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7" ])
    
