#!/usr/bin/env python
from boto.ec2.connection import EC2Connection
from boto.exception import EC2ResponseError
import sys
import os
import time


def wait_for_volume_state(aws_key_id, aws_secret_key, volume_id, state):
    """
    state = { available, in-use }
    """
    print 'Waiting for %s to be in state: %s' % (volume_id, state)
    conn = EC2Connection(aws_key_id, aws_secret_key)
    v = conn.get_all_volumes(str(volume_id))[0]
    if v.status != state:
        while v.status != state:
            time.sleep(0.5)
            sys.stdout.flush()
            v = conn.get_all_volumes(str(volume_id))[0]


def valid_aws_credentials(aws_key_id, aws_secret_key):
    """
    Returns True if the credentials are good, False if they are bad
    """
    try:
        conn = EC2Connection(str(aws_key_id), str(aws_secret_key))
        conn.get_all_regions()
        return True
    except EC2ResponseError as e:
        # TODO: This exception is really broad and isn't just for
        # authentication errors, there is an XML response that should
        # actually be inpected to verify that its actually bad credentials.
        return False


def create_ssh_key(aws_key_id, aws_secret_key, ssh_key_name):
    """
    If ssh_key_name already exists, None is returned, if it does not exist, it
    is created and the key material is returned.
    """
    conn = EC2Connection(str(aws_key_id), str(aws_secret_key))
    r = None
    try:
        # Key exists, so we return None
        conn.get_key_pair(ssh_key_name)
    except EC2ResponseError as e:
        #Key does not exist
        if e.error_code == 'InvalidKeyPair.NotFound':
            # The key was not found, so we create it.
            key = conn.create_key_pair(ssh_key_name)
            r = key.material
        else:
            # The error was something else
            raise
    return r


def usage():
    print "You must specify one of the following commands:"
    print "        %s volumewait (available|in-use)" % sys.argv[0]
    print "        %s validcredentials" % sys.argv[0]
    print "        %s getsshkey <keyname>" % sys.argv[0]
    sys.exit(1)


def main():
    try:
        aws_key_id = os.environ['AMAZON_ACCESS_KEY_ID']
        aws_secret_key = os.environ['AMAZON_SECRET_ACCESS_KEY']
    except KeyError:
        print "You must set the following two environment variables:"
        print '    AMAZON_ACCESS_KEY_ID'
        print '    AMAZON_SECRET_ACCESS_KEY'
        sys.exit(1)

    if len(sys.argv) < 2:
        usage()

    command = sys.argv[1]
    if command == 'volumewait':
        volume_id = 'vol-82e98aeb'
        wait_for_volume_state(
                aws_key_id,
                aws_secret_key,
                volume_id,
                sys.argv[1]
                )
    elif command == 'validcredentials':
        print valid_aws_credentials(aws_key_id, aws_secret_key)
    elif command == 'getsshkey':
        if len(sys.argv) != 3:
            print "ERROR: You must supply the SSH keyname as an argument"
            print
            usage()
        key_name = sys.argv[2]
        print create_ssh_key(
                aws_key_id,
                aws_secret_key,
                key_name
                )
    else:
        print "ERROR: %s is not a valid command" % command
        print
        usage()


if __name__ == "__main__":
    main()
