from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext

from data_model import *  # run 'shellfoundry generate' to generate data model classes


RESERVED_STATUS = "Reserved"


class InvalidResourceName(Exception):
    pass


class UnavailableResource(Exception):
    pass


class ResourceFinderDriver(ResourceDriverInterface):

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

    def swap_resource(self, context, resource_name):
        """
        Looks for EXCLUSIVE access to entire resource
        :param ResourceCommandContext context:
        :return:
        """
        api = CloudShellSessionContext(context).get_api()
        sb_id = context.reservation.reservation_id

        # validate resource name
        try:
            api.GetResourceDetails(resource_name)
        except Exception as e:
            raise InvalidResourceName(str(e))

        # validate availability
        resource_availability = api.GetResourceAvailability(resourcesNames=[resource_name]).Resources
        reserved = [x for x in resource_availability if x.ReservedStatus == RESERVED_STATUS]
        if reserved:
            raise UnavailableResource(f"Unavailable target resources: {reserved}")

        # find current position of service
        positions = api.GetReservationServicesPositions(sb_id).ResourceDiagramLayouts
        service_position = [x for x in positions if x.ResourceName == context.resource.name][0]

        # add new resource
        api.AddResourcesToReservation(reservationId=sb_id, resourcesFullPath=[resource_name])

        # put at current service position
        api.SetReservationResourcePosition(reservationId=sb_id,
                                           resourceFullName=resource_name,
                                           x=service_position.X,
                                           y=service_position.Y)

        # remove self
        api.WriteMessageToReservationOutput(reservationId=sb_id, message=f"Resource added, removing service {context.resource.name}")
        api.RemoveServicesFromReservation(reservationId=sb_id, services=[context.resource.name])
