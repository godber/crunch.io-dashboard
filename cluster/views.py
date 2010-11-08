from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, mail_admins

from dash.cluster.models import ClusterTemplate, ClusterInstance, UserProfile
from dash.cluster.models import Ec2InstanceType, Disk, AwsCredential
from dash.cluster.forms import ClusterTemplateForm, DiskForm, AwsCredentialForm
from dash.cluster.forms import ClusterUserCreationForm
import dash.ec2utils as ec2utils

from djangotasks.models import Task

import datetime

def register(request):
    user = request.user
    return render_to_response('registration/register.html', {
        'user': user,
    } )


@login_required
def create(request):
    user = request.user
    user_profile = user.get_profile()
    if request.method == 'POST':
        cluster_form = ClusterTemplateForm(request.POST)
        disk_form = DiskForm(request.POST)
        if cluster_form.is_valid() and disk_form.is_valid():
            # Creating the Cluster Template and Related Activities
            if 'is_demo' in request.POST:
                is_demo = request.POST['is_demo']
            else:
                is_demo = False
            instance_type = Ec2InstanceType.objects.get(id = request.POST['type_of_nodes'])
            cluster_template = ClusterTemplate(
                user_profile    = user_profile,
                name            = request.POST['name'],
                number_of_nodes = request.POST['number_of_nodes'], 
                type_of_nodes   = instance_type,
                creation_time   = datetime.datetime.now(),
                is_demo         = is_demo,
                status          = 'disk-creating',
                )
            cluster_template.save()
            disk = Disk( 
                    size             = request.POST['size'],
                    cluster_template = cluster_template,
                    )
            disk.save()
            task = Task.objects.task_for_object(
                    Disk,
                    disk.id,
                    'make_initial_snapshot'
                    )
            Task.objects.run_task(task.id)
            mail_admins(
                    "User %s created a cluster" % user.username,
                    "User %s created a cluster: %s (DEMO: %s)" % (
                        user.username,
                        cluster_template.name,
                        cluster_template.is_demo,
                        )
                    )

            return HttpResponseRedirect('/')
    else:
        cluster_form = ClusterTemplateForm( initial = {'is_demo': True} )
        disk_form = DiskForm()


    return render_to_response(
            'create.html',
            {
            'cluster_form': cluster_form,
            'disk_form': disk_form,
            'user': user,
            },
            context_instance=RequestContext(request)
    )

@login_required
def launch(request, cluster_template_id):
    user = request.user
    if request.method == 'GET':
        # FIXME: Switch to POST
        # Clusters should only launch if its a POST request
        cluster_template = get_object_or_404(
            ClusterTemplate,
            id=cluster_template_id
            )
        if cluster_template.status in ('starting', 'stopping', 'running'):
            error_message = 'This cluster is already running.  Only one cluster may run at a time.  Create a new cluster and launch it if necessary.'
            return render_to_response('launch_error.html', {
                'user': user,
                'cluster_template': cluster_template,
                'error_message': error_message,
                } )
        else:
            cluster_template.status = 'starting'
            cluster_template.save()
            cluster_instance = ClusterInstance(
                cluster_template = cluster_template,
                launch_time      = datetime.datetime.now()
                )
            cluster_instance.save()
            task = Task.objects.task_for_object( ClusterInstance, cluster_instance.id, 'launch' )
            Task.objects.run_task(task.id)
            mail_admins(
                    "User %s launched a cluster" % user.username,
                    "User %s launched a cluster: %s (DEMO: %s)" % (
                        user.username,
                        cluster_template.name,
                        cluster_template.is_demo,
                        )
                    )
    return render_to_response(
            'launch.html',
            {
            'user': user,
            'cluster_template': cluster_template,
            'cluster_instance': cluster_instance,
            },
            context_instance=RequestContext(request)
        )

@login_required
def terminate(request,cluster_instance_id):
    user = request.user
    cluster_instance = get_object_or_404(ClusterInstance,id=cluster_instance_id)
    cluster_instance.termination_time = datetime.datetime.now()
    cluster_instance.save()

    cluster_instance.cluster_template.status = 'stopping'
    cluster_instance.cluster_template.save()
    task = Task.objects.task_for_object(
            ClusterInstance,
            cluster_instance.id,
            'terminate'
            )
    Task.objects.run_task(task.id)
    mail_admins(
            "User %s terminated a cluster" % user.username,
            "User %s terminated a cluster" % user.username
            )
    return render_to_response(
            'terminate.html',
            {
            'user': user,
            'cluster_instance': cluster_instance
            },
            context_instance=RequestContext(request)
        )

@login_required
def account(request, user_id):
    user = request.user
    return render_to_response(
            'account.html',
            {
                'user': user,
            })

@login_required
def ssh_key(request):
    user = request.user
    ssh_key = user.userprofile_set.all()[0].awscredential.ssh_key
    response = HttpResponse(ssh_key, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=crunch_io_master.rsa'
    return response

@login_required
def history(request, cluster_template_id):
    user = request.user
    cluster_template = get_object_or_404(ClusterTemplate,id=cluster_template_id)
    return render_to_response('history.html', {
        'user': user,
        'cluster_template': cluster_template,
        } )

@login_required
def dash(request):
    user = request.user
    user_profile = user.get_profile()
    cluster_templates = list(ClusterTemplate.objects.filter(user_profile = user_profile))
    cluster_instances = list(ClusterInstance.objects.all())
    return render_to_response('dash.html', {
        'user': user,
        'cluster_templates': cluster_templates,
        'cluster_instances': cluster_instances,
        'running_states': ['starting', 'stopping', 'running'],
        } )

def account_create(request):
    if request.method == 'POST':
        user_form = ClusterUserCreationForm(request.POST)
        aws_credential_form = AwsCredentialForm(request.POST)
        if user_form.is_valid() and aws_credential_form.is_valid():
            user_data = user_form.cleaned_data
            aws_data = aws_credential_form.cleaned_data

            ssh_key_needed = False
            ssh_key = ec2utils.create_ssh_key(
                    aws_data['aws_key_id'],
                    aws_data['aws_secret_key'],
                    'crunch-master'
                    )
            if ssh_key == None:
                ssh_key = 'Please paste your SSH key here'
                ssh_key_needed = True

            user = User(
                    username = user_data['username'],
                    email = user_data['email_address'],
                    )
            user.set_password(user_data['password1'])
            user.is_active = False
            user.save()
            user_profile = UserProfile(
                    user = user,
                    credit = '0.00',
                    )
            user_profile.save()
            aws_credentials = AwsCredential(
                    user_profile   = user_profile,
                    aws_user_id    = aws_data['aws_user_id'],
                    ssh_key        = ssh_key,
                    aws_key_id     = aws_data['aws_key_id'],
                    aws_secret_key = aws_data['aws_secret_key'],
                    )
            aws_credentials.save()
            mail_admins(
                    "User Account %s Created for %s" % (
                        user_data['username'],
                        user_data['email_address']
                        ),
                    """The following user account has been created:
    username: %s
    email:    %s
    ssh_key_needed: %s
                    """ % (
                        user_data['username'],
                        user_data['email_address'],
                        ssh_key_needed,
                        )
                    )
            return render_to_response(
                    'account_created.html',
                    {
                    'ssh_key_needed': ssh_key_needed,
                    'email': user_data['email_address'],
                    },
                    context_instance=RequestContext(request)
                    )
    else:
        user_form = ClusterUserCreationForm()
        aws_credential_form = AwsCredentialForm()

    return render_to_response(
            'account_create.html',
            {
            'user_form': user_form,
            'aws_credential_form': aws_credential_form,
            },
            context_instance=RequestContext(request)
        )

