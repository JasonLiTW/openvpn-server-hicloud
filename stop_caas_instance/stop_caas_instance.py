import os
import json
import boto3
import botocore.vendored.requests as requests


def handler(event, context):
    instance_id = os.environ["instanceId"]
    lambda_client = boto3.client('lambda')
    signed_res = lambda_client.invoke(
        FunctionName="getCaasSignature",
        InvocationType='RequestResponse',
        Payload=("\"https://hws.hicloud.hinet.net/cloud_hws/api/hws/?action=stopInstances"
                 "&instanceId={0}&version=2015-05-26\"").format(instance_id))
    signed_url = json.loads(signed_res['Payload'].read())
    session = requests.session()

    try:
        res = session.get(signed_url)
        res_json = res.json()
    except requests.exceptions.RequestException as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': "A network error occurred while stopping the server."})}

    if "errors" in res_json:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': "An exception occurred while stopping the server."})}

    if "statusMap" in res_json and instance_id in res_json["statusMap"]:
        if res_json["statusMap"][instance_id] == "vm_stopping":
            return {
                'statusCode': 200,
                'body': json.dumps({'message': "OK, Server is shutting down."})}
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({'message': res_json["statusMap"][instance_id] + "error."})}
