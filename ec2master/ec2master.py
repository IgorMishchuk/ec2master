import boto3
import botocore
import click

def filter_instances(project):
    instances=[]
    if project:
        filters =[{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances

def has_pending_snapshot(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots and snapshots[0].state == 'pending'

@click.group()
@click.option('--profile', default='testuser', help="Specify profile to use")
def cli(profile):
    """EC2Master manages snapshots"""
    session = boto3.Session(profile_name=profile)
    global ec2
    ec2 = session.resource('ec2')

@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list')
@click.option('--project', default=None, help="Only snapshots for project (tag Project:<nam>)")
@click.option('--all', 'list_all', default=False, is_flag=True, help="List all snapshots")
def list_snapshots(project, list_all):
    "List EC2 snapshots"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ".join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c")
                )))

                if s.state == 'completed' and not list_all: break

    return

@cli.group('volumes')
def volumes():
    """Commands for volumes"""

@volumes.command('list')
@click.option('--project', default=None, help="Only volumes for project (tag Project:<nam>)")
def list_volumes(project):
    "List EC2 volumes"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(", ".join((
                v.id,
                i.id,
                v.state,
                str(v.size) + " GiB",
                v.encrypted and "Encrypyed" or "Not encrypted"
            )))

    return

@cli.group('instances')
def instances():
    """Commands for instances"""

@instances.command('snapshot', help="Create snapshots of all volumes")
@click.option('--project', default=None, help="Only instances for project (tag Project:<nam>)")
@click.option('--force', 'force', default=False, is_flag=True, help="Force command run for all instances")
def create_snapshots(project, force):
    "Create snapshots for EC2 instances"
    if not force and not project:
        raise Exception('You need to pass --force if you want to run command against all instances')
    instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}...".format(i.id))
        i.stop()
        i.wait_until_stopped()
        for v in i.volumes.all():
            if has_pending_snapshot(v):
                print(" Skipping {0}, snapshot already in progress".format(v.id))
                continue
            print(" Creating snashot of {0}".format(v.id))
            v.create_snapshot(Description="Created by EC2Master")
        print("Starting {0}...".format(i.id))
        i.start()
        i.wait_until_running()
    
    print("Job's done.")
    return

@instances.command('list')
@click.option('--project', default=None, help="Only instances for project (tag Project:<nam>)")
def list_instacnes(project):
    "List EC2 instances"

    instances = filter_instances(project)
    
    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags or []}
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Project', '<no project>')
        )))

    return

@instances.command('stop')
@click.option('--project', default=None, help='Only instacnes for project')
@click.option('--force', 'force', default=False, is_flag=True, help="Force command run for all instances")
def stop_instances(project, force):
    "Stop EC2 instances"
    if not force and not project:
        raise Exception('You need to pass --force if you want to run command against all instances')
    instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}...".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print(" Could not stop {0}. ".format(i.id) + str(e))
            continue

    return

@instances.command('start')
@click.option('--project', default=None, help='Only instacnes for project')
@click.option('--force', 'force', default=False, is_flag=True, help="Force command run for all instances")
def start_instances(project, force):
    "Start EC2 instances"
    if not force and not project:
        raise Exception('You need to pass --force if you want to run command against all instances')
    instances = filter_instances(project)

    for i in instances:
        print("Starting {0}...".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print(" Could not start {0}. ".format(i.id) + str(e))
            continue

    return

@instances.command('reboot')
@click.option('--project', default=None, help='Only instacnes for project')
@click.option('--force', 'force', default=False, is_flag=True, help="Force command run for all instances")
def reboot_instances(project, force):
    "Reboot EC2 instances"
    if not force and not project:
        raise Exception('You need to pass --force if you want to run command against all instances')
    instances = filter_instances(project)

    for i in instances:
        print("Rebooting {0}...".format(i.id))
        try:
            i.reboot()
        except botocore.exceptions.ClientError as e:
            print(" Could not reboot {0}. ".format(i.id) + str(e))
            continue

    return

if __name__ == '__main__':
    cli()