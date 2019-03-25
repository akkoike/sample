import os
import io
from azure.mgmt.compute import ComputeManagementClient
import azure.mgmt.resource
import automationassets
import azure.mgmt.storage
from azure.storage.blob import BlockBlobService
import requests
from email import message
import smtplib
import base64
from email.Header import Header
from email.utils import formatdate
from email.MIMEText import MIMEText

def get_automation_runas_credential(runas_connection):
    from OpenSSL import crypto
    import binascii
    from msrestazure import azure_active_directory
    import adal

    # Get the Azure Automation RunAs service principal certificate
    cert = automationassets.get_automation_certificate("AzureRunAsCertificate")
    pks12_cert = crypto.load_pkcs12(cert)
    pem_pkey = crypto.dump_privatekey(crypto.FILETYPE_PEM,pks12_cert.get_privatekey())

    # Get run as connection information for the Azure Automation service principal
    application_id = runas_connection["ApplicationId"]
    thumbprint = runas_connection["CertificateThumbprint"]
    tenant_id = runas_connection["TenantId"]

    # Authenticate with service principal certificate
    resource ="https://management.core.windows.net/"
    authority_url = ("https://login.microsoftonline.com/"+tenant_id)
    context = adal.AuthenticationContext(authority_url)
    return azure_active_directory.AdalAuthentication(
    lambda: context.acquire_token_with_client_certificate(
            resource,
            application_id,
            pem_pkey,
            thumbprint)
    )

# Authenticate to Azure using the Azure Automation RunAs service principal
runas_connection = automationassets.get_automation_connection("AzureRunAsConnection")
azure_credential = get_automation_runas_credential(runas_connection)
subscription_id = str(runas_connection["SubscriptionId"])

# Get storage key
storage_resource_group = "{RESOURCE_GROUP_NAME}"
storage_account_name = "{STORAGE_ACCOUNT_NAME}"
storage_container_name = "{STORAGE_ACCOUNT_CONTAINER_NAME}"
storage_file_name = "{BLOB_OBJECT_NAME}"

storage_client = azure.mgmt.storage.StorageManagementClient(
    azure_credential,
    subscription_id)
storage_keys = storage_client.storage_accounts.list_keys(storage_resource_group, storage_account_name)
storage_account_key = storage_keys.keys[0].value

# instanced blob service
blobservice = BlockBlobService(account_name=storage_account_name, account_key=storage_account_key)

# get list under Storage Account Container
# bloblist = blobservice.list_blobs(storage_container_name)
# for blob in bloblist:
#    print("\t Blob name: " + blob.name)

# Create URL list and GET http method per urls, finaly create email body
urllist = blobservice.get_blob_to_text(storage_container_name,storage_file_name)
mailbody = ""
for url in urllist.content.splitlines():
    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as e:
  	    response = "Error please check"
    finally:
        mailbody = str(mailbody) + str(url) + "\t" + str(response) + "\n\n"

# smtp for SendGrid
smtp_host = 'smtp.sendgrid.net'
smtp_port = 587
from_email = '{ENVELOPE_FROM_ADDRESS}'
to_email = '{ENVELOPE_TO_ADDRESS}'
username = '{SENDGRID_ACCOUNT_NAME}'
password = '{SENDGRID_PASSWORD}'
Encoding = "utf-8"

message = MIMEText(mailbody.encode(Encoding),"plain",Encoding)
message["Subject"] = str(Header("Testmail from Automation Python Runbook",Encoding))
message["From"] = "%s <%s>" %(str(Header("From",Encoding)),from_email)
message["To"] = "%s <%s>" %(str(Header("To",Encoding)),to_email)
message["Date"] = formatdate()

s = smtplib.SMTP(smtp_host, 587)
s.ehlo()
s.starttls()
s.login(username,password)

s.sendmail(from_email,[to_email],message.as_string())
s.close()
