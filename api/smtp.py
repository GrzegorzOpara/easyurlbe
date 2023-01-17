from __future__ import print_function
import time
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings

def sendEmail(email, temp_id, link):
    # Configure API key authorization: api-key
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.SMTP_API_KEY

     # Uncomment below lines to configure API key authorization using: partner-key
    # configuration = sib_api_v3_sdk.Configuration()
    # configuration.api_key['partner-key'] = 'YOUR_API_KEY'

    # create an instance of the API class
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=[{"email":email}], template_id=temp_id, params={"PASSWORDRESETLINK": link}, headers={"charset": "iso-8859-1"})

    try:
        # Send a transactional email
        api_response = api_instance.send_transac_email(send_smtp_email)
        return(api_response)
    except ApiException as e:
        return("Exception when calling SMTPApi->send_transac_email: %s\n" % e)