from unifispot.const import API_END_POINT_NONE,API_END_POINT_MAIL_CHIMP,API_END_POINT_GRIND,API_END_POINT_COUNTER

from .mailchimp import export_to_mailchimp

def get_api_endpoint(endpoint=None):
    if endpoint == API_END_POINT_MAIL_CHIMP:
        return export_to_mailchimp
    else:
        return None