from setuptools import setup

setup(
    name='EC2master',
    vertsion='0.1',
    author="Igor Mishchuk",
    description="EC2master is a tool to manage AWS EC2 snapshots",
    license="GPLv3+",
    packages=['ec2master'],
    url="https://github.com/IgorMishchuk/ec2master",
    install_requires=[
        'click',
        'boto3'
    ],
    entry_points='''
        [console_scripts]
        ec2master=ec2master.ec2master:cli
        '''
)