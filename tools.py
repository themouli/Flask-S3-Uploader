from uuid import uuid4
import boto
import os
import os.path
from flask import current_app as app
from werkzeug.utils import secure_filename
from boto.s3.key import Key

def s3_upload(source_file, acl='public-read'):
    """ Uploads WTForm File Object to Amazon S3

        Expects following app.config attributes to be set:
            S3_KEY              :   S3 API Key
            S3_SECRET           :   S3 Secret Key
            S3_BUCKET           :   What bucket to upload to
            S3_UPLOAD_DIRECTORY :   Which S3 Directory.

        The default sets the access rights on the uploaded file to
        public-read.  It also generates a unique filename via
        the uuid4 function combined with the file extension from
        the source file.
    """

    destination_filename = get_destination_filename(source_file)
    # Connect to S3 and upload file.
    conn = boto.connect_s3(app.config["S3_KEY"], app.config["S3_SECRET"])
    b = conn.get_bucket(app.config["S3_BUCKET"])

    k = Key(b)
    k.key = destination_filename
    file_contents = source_file.data.read()
    k.set_contents_from_string(file_contents)
    public_url = k.generate_url(0, query_auth=False)
#   k.set_acl(acl)

    return destination_filename + " " + public_url


def store_locally(source_file):
    """
        Stores the uploaded file locally
    """
    destination_filename = get_destination_filename(source_file)

    file_contents = source_file.data.read()
    print "file contents from store_locally" + file_contents
    with open(app.config["LOCAL_OUTPUT_DIR"]+destination_filename, 'w') as output_file:
        output_file.write(file_contents)
    output_file.close()
    url = app.config["HOST"] + app.config["LOCAL_OUTPUT_DIR"] + destination_filename
    return url

def get_destination_filename(source_file):
    source_filename = secure_filename(source_file.data.filename)
    return  uuid4().hex + source_filename
