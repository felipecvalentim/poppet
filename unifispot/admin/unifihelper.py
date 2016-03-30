'''A set of methods for Unifi related operations'''

import time
import math

def ap_status_generate(state):
    status_list = ['<span class="label label-danger">AP Disconnected</span>','<span class="label label-success">AP Active</span>',\
                    '<span class="label label-warning">Pending</span>','<span class="label label-warning">Firmware Mismatch</span>',\
                    '<span class="label label-primar">AP Upgrading</span>','<span class="label label-success">Provisioning</span>',\
                    '<span class="label label-danger">Heartbeat Missed</span>','<span class="label label-primary">Adopting</span>',\
                    '<span class="label label-primary">AP Deleting</span>','<span class="label label-warning">Managed By Others</span>',\
                    '<span class="label label-danger">Adopt Failed</span>','<span class="label label-warning">AP is isolated</span>',\
                    '<span class="label label-danger">AP Disconnected</span>','<span class="label label-success">AP Ready</span>',\
                    '<span class="label label-warning">Pending</span>','<span class="label label-warning">Firmware Mismatch</span>',\
                    '<span class="label label-primary">AP Upgrading</span>','<span class="label label-success">Initializing</span>',\
                    '<span class="label label-danger">Heartbeat Missed</span>','<span class="label label-primary">Initializing</span>',\
                    '<span class="label label-primary">D:AP Deleting</span>','<span class="label label-warning">Managed By Others</span>',\
                    '<span class="label label-danger">Adopt Failed</span>','<span class="label label-warning">AP is isolated</span>']
    try:
        status = status_list[state]

    except:
        status = '<span class="label label-danger">UNKNOWN</span>'

    return status


def guest_status_generate(client,site_name):
    ap_mac  = client.get('ap_mac','')
    rssi = client.get('rssi',0)
    user_mac = client.get('mac','')
    #Convert rssi number to signal quality %
    if rssi > 45:
        rssi =45
    if rssi <5:
        rssi = 5
    rssi_val = ( (rssi -5 ) / 40 * 99 )
    rssi_val = math.ceil(rssi_val)
    #Convert up time in seconds to more readable format
    uptime = time.strftime('%H:%M:%S', time.gmtime(client.get('uptime',0)))
    if client.get('authorized',False):
        status = '<span class="label label-success">Authorized</span>'
    else:
        status = '<span class="label label-warning">Pending</span>'
    return [site_name,ap_mac,user_mac,rssi_val,uptime,status]


