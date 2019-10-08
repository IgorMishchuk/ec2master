# ec2master
Demo scripts

## About

This is a demo

## Configuring

ec2master uses the configuration file created by AWS cli e.g.

`aws configure --profile ec2master`

## Running

`pipenv run python .\ec2master\ec2master.py <command> <subcommand> <--project=PROJECT>`

*command* is instances, volumes or snapshots

*subcommand* - depends on command

*project* is optional