from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext
from data_model import *  # run 'shellfoundry generate' to generate data model classes


class TrafficChassisMockDriver(ResourceDriverInterface):

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

    def get_inventory(self, context):
        """ Return device structure with all standard attributes
        :type context: cloudshell.shell.core.driver_context.AutoLoadCommandContext
        :rtype: cloudshell.shell.core.driver_context.AutoLoadDetails
        """
        resource = TrafficChassisMock.create_from_context(context)
        resource.vendor = "Major Vendor"
        resource.model_name = "Model X"

        module1 = GenericTrafficGeneratorModule("Module1")
        resource.add_sub_resource(relative_path="1", sub_resource=module1)

        for i in range(1, 17):
            port = GenericTrafficGeneratorPort(f"Port {i}")

            if i < 9:
                port.max_speed = 10
            else:
                port.max_speed = 100

            module1.add_sub_resource(relative_path=str(i), sub_resource=port)

        return resource.create_autoload_details()