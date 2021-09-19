from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext, AutoLoadCommandContext
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext
from cloudshell.api.cloudshell_api import CloudShellAPISession
import winrm
from retrying import retry

from data_model import *  # run 'shellfoundry generate' to generate data model classes


class WindowsServerDriver(ResourceDriverInterface):

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

    # <editor-fold desc="Discovery">

    def get_inventory(self, context):
        """
        Discovers the resource structure and attributes.
        :param AutoLoadCommandContext context: the context the command runs on
        :return Attribute and sub-resource information for the Shell resource you can return an AutoLoadDetails object
        :rtype: AutoLoadDetails
        """
        # See below some example code demonstrating how to return the resource structure and attributes
        # In real life, this code will be preceded by SNMP/other calls to the resource details and will not be static
        # run 'shellfoundry generate' in order to create classes that represent your data model

        '''
        resource = WindowsServer.create_from_context(context)
        resource.vendor = 'specify the shell vendor'
        resource.model = 'specify the shell model'
        port1 = ResourcePort('Port 1')
        port1.ipv4_address = '192.168.10.7'
        resource.add_sub_resource('1', port1)

        return resource.create_autoload_details()
        '''
        self.health_check_winrm(context)
        return AutoLoadDetails([], [])

    # </editor-fold>

    # <editor-fold desc="Orchestration Save and Restore Standard">
    def orchestration_save(self, context, cancellation_context, mode, custom_params):
        """
        Saves the Shell state and returns a description of the saved artifacts and information
        This command is intended for API use only by sandbox orchestration scripts to implement
        a save and restore workflow
        :param ResourceCommandContext context: the context object containing resource and reservation info
        :param CancellationContext cancellation_context: Object to signal a request for cancellation. Must be enabled in drivermetadata.xml as well
        :param str mode: Snapshot save mode, can be one of two values 'shallow' (default) or 'deep'
        :param str custom_params: Set of custom parameters for the save operation
        :return: SavedResults serialized as JSON
        :rtype: OrchestrationSaveResult
        """

        # See below an example implementation, here we use jsonpickle for serialization,
        # to use this sample, you'll need to add jsonpickle to your requirements.txt file
        # The JSON schema is defined at:
        # https://github.com/QualiSystems/sandbox_orchestration_standard/blob/master/save%20%26%20restore/saved_artifact_info.schema.json
        # You can find more information and examples examples in the spec document at
        # https://github.com/QualiSystems/sandbox_orchestration_standard/blob/master/save%20%26%20restore/save%20%26%20restore%20standard.md
        '''
        # By convention, all dates should be UTC
        created_date = datetime.datetime.utcnow()

        # This can be any unique identifier which can later be used to retrieve the artifact
        # such as filepath etc.

        # By convention, all dates should be UTC
        created_date = datetime.datetime.utcnow()

        # This can be any unique identifier which can later be used to retrieve the artifact
        # such as filepath etc.
        identifier = created_date.strftime('%y_%m_%d %H_%M_%S_%f')

        orchestration_saved_artifact = OrchestrationSavedArtifact('REPLACE_WITH_ARTIFACT_TYPE', identifier)

        saved_artifacts_info = OrchestrationSavedArtifactInfo(
            resource_name="some_resource",
            created_date=created_date,
            restore_rules=OrchestrationRestoreRules(requires_same_resource=True),
            saved_artifact=orchestration_saved_artifact)

        return OrchestrationSaveResult(saved_artifacts_info)
        '''
        pass

    def orchestration_restore(self, context, cancellation_context, saved_artifact_info, custom_params):
        """
        Restores a saved artifact previously saved by this Shell driver using the orchestration_save function
        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param CancellationContext cancellation_context: Object to signal a request for cancellation. Must be enabled in drivermetadata.xml as well
        :param str saved_artifact_info: A JSON string representing the state to restore including saved artifacts and info
        :param str custom_params: Set of custom parameters for the restore operation
        :return: None
        """
        '''
        # The saved_details JSON will be defined according to the JSON Schema and is the same object returned via the
        # orchestration save function.
        # Example input:
        # {
        #     "saved_artifact": {
        #      "artifact_type": "REPLACE_WITH_ARTIFACT_TYPE",
        #      "identifier": "16_08_09 11_21_35_657000"
        #     },
        #     "resource_name": "some_resource",
        #     "restore_rules": {
        #      "requires_same_resource": true
        #     },
        #     "created_date": "2016-08-09T11:21:35.657000"
        #    }

        # The example code below just parses and prints the saved artifact identifier
        saved_details_object = json.loads(saved_details)
        return saved_details_object[u'saved_artifact'][u'identifier']
        '''
        pass

    @staticmethod
    def _send_winrm_command(winrm_session, command):
        """
        :param winrm.Session winrm_session:
        :param str command:
        :return:
        :rtype str:
        """
        response = winrm_session.run_ps(command)

        # validate response
        if response.status_code != 0:
            exc_msg = "pywinrm response error. status code: {}".format(response.status_code)
            if response.std_out:
                exc_msg += ", std-out: {}".format(response.std_out)
            if response.std_err:
                exc_msg += ", std-err: {}".format(response.std_err)
            raise Exception(exc_msg)

        return response.std_out.decode("utf-8")

    def _get_winrm_session_from_context(self, context, api):
        """
        :param ResourceCommandContext context:
        :param CloudShellAPISession api:
        :return:
        """
        resource = WindowsServer.create_from_context(context)
        resource_name = context.resource.name
        private_ip = context.resource.address
        user = resource.user
        encrypted_password = resource.password
        decrypted_password = api.DecryptPassword(encrypted_password).Value

        if not decrypted_password:
            exc_msg = f"No password populated for '{resource_name}'. Can't get WinRM session"
            raise ValueError(exc_msg)

        s = winrm.Session(private_ip, auth=(user, decrypted_password))
        return s

    def _get_hostname_winrm(self, winrm_session):
        """
        :param winrm.Session winrm_session:
        :param ResourceCommandContext context:
        :return:
        """
        hostname = self._send_winrm_command(winrm_session, "hostname")
        return hostname.strip()

    def health_check_winrm(self, context):
        """
        :param ResourceCommandContext context:
        :return:
        """
        resource_name = context.resource.name
        api = CloudShellSessionContext(context).get_api()

        with LoggingSessionContext(context) as logger:
            try:
                s = self._get_winrm_session_from_context(context, api)
                hostname = self._get_hostname_winrm(s)
            except Exception as e:
                err_msg = f"Issue running health check to {resource_name}. {type(e).__name__}: {str(e)}"
                logger.error(err_msg)
                api.SetResourceLiveStatus(resource_name, "Error", err_msg)
                raise Exception(err_msg)

        api.SetResourceLiveStatus(resource_name, "Online", "WinRM Health Check Passed")
        return f"Health Check PASSED. Target hostname: '{hostname}'"

    def poll_health_check(self, context, max_polling_minutes):
        """
        :param ResourceCommandContext context:
        :param str max_polling_minutes: to be converted to integer
        :return:
        """
        from timeit import default_timer
        resource_name = context.resource.name
        polling_ms = int(max_polling_minutes) * 60 * 1000
        api = CloudShellSessionContext(context).get_api()
        s = self._get_winrm_session_from_context(context, api)

        @retry(wait_fixed=10000, stop_max_delay=polling_ms)
        def _poll_for_hostname():
            return self._get_hostname_winrm(s)

        with LoggingSessionContext(context) as logger:
            start = default_timer()
            try:
                hostname = _poll_for_hostname()
            except Exception as e:
                exc_msg = f"WinRM polling FAILED for '{resource_name}' after {max_polling_minutes} minutes. {type(e).__name__}: {str(e)}"
                logger.error(exc_msg)
                api.SetResourceLiveStatus(resource_name, "Error", exc_msg)
                raise Exception(exc_msg)
            elapsed = default_timer() - start
        success_msg = f"WinRM polling PASSED after '{elapsed:.2f}' seconds. Target Hostname '{hostname}'"
        api.SetResourceLiveStatus(resource_name, "Online", success_msg)
        return success_msg

    def send_winrm_command(self, context, command):
        """
        :param ResourceCommandContext context:
        :param str command:
        :return:
        """
        resource_name = context.resource.name
        api = CloudShellSessionContext(context).get_api()
        with LoggingSessionContext(context) as logger:
            s = self._get_winrm_session_from_context(context, api)
            logger.info("'{}' Sending WinRM command: '{}'".format(resource_name, command))
            try:
                response = self._send_winrm_command(s, command)
            except Exception as e:
                exc_msg = f"WinRM Command failed for '{resource_name}'. {type(e).__name__}: {str(e)}"
                logger.error(exc_msg)
                raise Exception(exc_msg)
        return response

    # </editor-fold>
