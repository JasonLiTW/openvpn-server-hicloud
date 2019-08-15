import os
import json
import boto3
import botocore.vendored.requests as requests


def handler(event, context):
    instance_id = os.environ['instanceId']
    lambda_client = boto3.client('lambda')

    status_signed_res = lambda_client.invoke(
        FunctionName="getCaasSignature",
        InvocationType='RequestResponse',
        Payload=("\"https://hws.hicloud.hinet.net/cloud_hws/api/hws/?"
                 "action=describeInstances&instanceId={0}"
                 "&version=2015-05-26\"").format(instance_id))

    status_signed_url = json.loads(status_signed_res['Payload'].read())
    session = requests.session()
    try:
        status_res = session.get(status_signed_url)
        status_res_json = status_res.json()
    except requests.exceptions.RequestException as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': "A network error occurred while getting the Server state."})}

    if "instanceList" in status_res_json and len(status_res_json["instanceList"]) == 1 and "operationStatus" in \
            status_res_json["instanceList"][0]:
        status = status_res_json["instanceList"][0]["operationStatus"]

        if status == "vm_stop":
            start_signed_res = lambda_client.invoke(
                FunctionName="getCaasSignature",
                InvocationType='RequestResponse',
                Payload=("\"https://hws.hicloud.hinet.net/cloud_hws/api/hws/?"
                         "action=startInstances&instanceId={0}"
                         "&version=2015-05-26\"").format(instance_id))
            start_signed_url = json.loads(start_signed_res['Payload'].read())

            try:
                start_res = session.get(start_signed_url)
                start_res_json = start_res.json()
            except requests.exceptions.RequestException as e:
                return {
                    'statusCode': 500,
                    'body': json.dumps({'message': "A network error occurred while starting the server."})}

            if "errors" in start_res_json:
                return {
                    'statusCode': 500,
                    'body': json.dumps({'message': ("An exception occurred while starting the server. "
                                                    "Please try again later.")})}
            else:
                status = "OK, Server is booting up."
        elif status == "vm_start":
            status = ("Server is powered on, you can try to connect directly. "
                      "If you are unable to connect, maybe our server is starting the VPN service, "
                      "or is preparing to shutdown. Please try again after about 1 minute.")
        elif status == "vm_stopping":
            status = "Server is shutting down, please try again later."
        elif status == "vm_starting":
            status = "Server is booting up, please try again later."
        else:
            status = "Unknown error."

        return {
            'statusCode': 200,
            'body': json.dumps({'message': status})}
