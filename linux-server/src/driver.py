from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext

from data_model import *  # run 'shellfoundry generate' to generate data model classes
from cli_handler import LinuxSSH
from timeit import default_timer
from retrying import retry



class LinuxServerDriver (ResourceDriverInterface):

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
        resource = LinuxServer.create_from_context(context)
        resource.vendor = 'specify the shell vendor'
        resource.model = 'specify the shell model'
        port1 = ResourcePort('Port 1')
        port1.ipv4_address = '192.168.10.7'
        resource.add_sub_resource('1', port1)

        return resource.create_autoload_details()
        '''
        self.health_check(context)
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
    def _get_ssh_session_from_context(context, api):
        """
        destructure context and return ssh session
        :param ResourceCommandContext context:
        :param CloudShellAPISession api:
        :return:
        """
        resource = LinuxServer.create_from_context(context)
        resource_name = context.resource.name
        private_ip = context.resource.address
        user = resource.user
        encrypted_password = resource.password
        decrypted_password = api.DecryptPassword(encrypted_password).Value
        port_attr = int(resource.cli_tcp_port)
        ssh_port = port_attr if port_attr else 22

        if not decrypted_password:
            exc_msg = f"No password populated for '{resource_name}'. Can't get WinRM session"
            raise ValueError(exc_msg)

        ssh = LinuxSSH(address=private_ip, username=user, password=decrypted_password, port=ssh_port)
        return ssh

    def send_custom_command(self, context, command):
        """
        SSH session test
        :param ResourceCommandContext context:
        :param str command:
        :return:
        """
        resource_name = context.resource.name
        api = CloudShellSessionContext(context).get_api()

        with LoggingSessionContext(context) as logger:
            ssh = self._get_ssh_session_from_context(context, api)
            logger.info("'{}' Sending SSH command: '{}'".format(resource_name, command))
            try:
                response = ssh.send_command(command)
            except Exception as e:
                exc_msg = f"SSH Command failed for '{resource_name}'. {type(e).__name__}: {str(e)}"
                logger.error(exc_msg)
                raise Exception(exc_msg)
        return response

    def health_check(self, context):
        """
        SSH session test
        :param ResourceCommandContext context:
        :return:
        """
        resource_name = context.resource.name
        api = CloudShellSessionContext(context).get_api()

        with LoggingSessionContext(context) as logger:
            ssh = self._get_ssh_session_from_context(context, api)
            logger.info("'{}' Sending SSH Health Check".format(resource_name,))
            try:
                cli_user_outp = ssh.send_command("whoami")
            except Exception as e:
                err_msg = f"Issue running health check to {resource_name}. {type(e).__name__}: {str(e)}"
                logger.error(err_msg)
                api.SetResourceLiveStatus(resource_name, "Error", err_msg)
                raise Exception(err_msg)
        current_user = cli_user_outp.split("\n")[0].strip()
        success_msg = f"SSH Health check passed. Current running user: {current_user}"
        api.SetResourceLiveStatus(resource_name, "Online", success_msg)
        return success_msg

    def poll_health_check(self, context, max_polling_minutes):
        """
        :param ResourceCommandContext context:
        :param str max_polling_minutes: to be converted to integer
        :return:
        """
        resource_name = context.resource.name
        polling_ms = int(max_polling_minutes) * 60 * 1000
        api = CloudShellSessionContext(context).get_api()
        ssh = self._get_ssh_session_from_context(context, api)

        @retry(wait_fixed=10000, stop_max_delay=polling_ms)
        def _poll_for_user():
            return ssh.send_command("whoami")

        with LoggingSessionContext(context) as logger:
            start = default_timer()
            try:
                whoami_output = _poll_for_user()
            except Exception as e:
                exc_msg = f"SSH polling FAILED for '{resource_name}' after {max_polling_minutes} minutes. {type(e).__name__}: {str(e)}"
                logger.error(exc_msg)
                api.SetResourceLiveStatus(resource_name, "Error", exc_msg)
                raise Exception(exc_msg)
            elapsed = default_timer() - start
        current_user = whoami_output.split("\n")[0].strip()
        success_msg = f"SSH polling PASSED after '{elapsed:.2f}' seconds. Current CLI User: '{current_user}'"
        api.SetResourceLiveStatus(resource_name, "Online", success_msg)
        return success_msg


    # </editor-fold>
