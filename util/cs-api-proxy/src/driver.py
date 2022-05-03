import json

from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext
#from data_model import *  # run 'shellfoundry generate' to generate data model classes
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.helpers.sandbox_reporter.reporter import SandboxConsole
from cloudshell.api.cloudshell_api import SandboxDataKeyValue


class CsApiProxyDriver (ResourceDriverInterface):

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        pass

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        pass

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass

    def console_write(self, context, message):
        """
        :param ResourceCommandContext context:
        :param str message:
        :return:
        """
        api = CloudShellSessionContext(context).get_api()
        sb_id = context.reservation.reservation_id
        api.WriteMessageToReservationOutput(reservationId=sb_id, message=message)

    def console_warning(self, context, message):
        """
        :param ResourceCommandContext context:
        :param str message:
        :return:
        """
        api = CloudShellSessionContext(context).get_api()
        sb_id = context.reservation.reservation_id
        console = SandboxConsole(api, sb_id)
        console.warn_print(message)

    def console_success(self, context, message):
        """
        :param ResourceCommandContext context:
        :param str message:
        :return:
        """
        api = CloudShellSessionContext(context).get_api()
        sb_id = context.reservation.reservation_id
        console = SandboxConsole(api, sb_id)
        console.success_print(message)

    def get_sandbox_data(self, context):
        """
        :param ResourceCommandContext context:
        :return:
        """
        api = CloudShellSessionContext(context).get_api()
        sb_id = context.reservation.reservation_id
        data_keys = api.GetSandboxData(reservationId=sb_id).SandboxDataKeyValues
        dict_data = [{"key": x.Key, "value": x.Value} for x in data_keys]
        return json.dumps(dict_data, indent=4)

    def set_sandbox_data(self, context, key, value):
        """
        :param ResourceCommandContext context:
        :param str key:
        :param str value:
        :return:
        """
        api = CloudShellSessionContext(context).get_api()
        sb_id = context.reservation.reservation_id
        data = [SandboxDataKeyValue(key, value)]
        api.SetSandboxData(reservationId=sb_id, sandboxDataKeyValues=data)
        return f"'{key}' set to sandbox data store"
