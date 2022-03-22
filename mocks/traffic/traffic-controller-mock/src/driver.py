import json

from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import ResourceCommandContext
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext
from time import sleep, time
from datetime import datetime
from random import randint
from quali_api_helper import QualiAPISession
from helpers.dict_to_csv_str import dict_to_csv_str

TRAFFIC_GENERATOR_CHASSIS_FAMILY = "CS_TrafficGeneratorChassis"
TRAFFIC_GENERATOR_PORT_FAMILY = "CS_TrafficGeneratorPort"


class TrafficControllerMockDriver(ResourceDriverInterface):

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        pass

    def load_config(self, context, config_file_location):
        """Reserve ports and load configuration

        :param ResourceCommandContext context:
        :param str config_file_location: configuration file location
        :return:
        """
        api = CloudShellSessionContext(context).get_api()
        sb_id = context.reservation.reservation_id

        with LoggingSessionContext(context) as logger:
            res_details = api.GetReservationDetails(reservationId=sb_id).ReservationDescription
            chassis = [x for x in res_details.Resources if x.ResourceFamilyName == TRAFFIC_GENERATOR_CHASSIS_FAMILY]
            if not chassis:
                raise ValueError("No Traffic Generator Chassis Found in sandbox")
            if len(chassis) > 1:
                raise ValueError("Multiple traffic Generator Chassis found in sandbox")

            traffic_ports = [x for x in res_details.Resources if x.ResourceFamilyName == TRAFFIC_GENERATOR_PORT_FAMILY]
            if not traffic_ports:
                raise ValueError("No traffic generator ports found in sandbox")
            loading_msg = f"Loading traffic config '{config_file_location}'"
            logger.info(loading_msg)
            api.WriteMessageToReservationOutput(reservationId=sb_id, message=loading_msg)
            sleep(2)
            reserving_msg = f"Reserving ports: {[x.Name for x in traffic_ports]}"
            api.WriteMessageToReservationOutput(reservationId=sb_id, message=reserving_msg)
            logger.info(reserving_msg)
            sleep(3)

        return "Load Config completed"

    def start_traffic(self, context, blocking):
        """Start traffic on all ports

        :param context: the context the command runs on
        :param str blocking: True - return after traffic finish to run, False - return immediately
        """
        api = CloudShellSessionContext(context).get_api()
        sb_id = context.reservation.reservation_id
        is_blocking = True if blocking.lower() == "true" else False

        with LoggingSessionContext(context) as logger:

            if is_blocking:
                start_msg = "Starting traffic in blocking mode"
                api.WriteMessageToReservationOutput(reservationId=sb_id, message=start_msg)
                logger.info(start_msg)
                sleep(10)
            else:
                start_msg = "Traffic started non-blocking"
                api.WriteMessageToReservationOutput(reservationId=sb_id, message=start_msg)
                logger.info(start_msg)

        return "start traffic completed"

    def stop_traffic(self, context):
        """Stop traffic on all ports

        :param context: the context the command runs on
        """
        return "stop traffic completed"

    def get_statistics(self, context, view_name, output_type):
        """Get real time statistics as sandbox attachment

        :param ResourceCommandContext context:
        :param str view_name: requested view name
        :param str output_type: CSV or JSON
        :return:
        """
        api = CloudShellSessionContext(context).get_api()
        sb_id = context.reservation.reservation_id
        is_json = True if output_type.lower() == "json" else False

        with LoggingSessionContext(context) as logger:
            res_details = api.GetReservationDetails(reservationId=sb_id).ReservationDescription
            chassis = [x for x in res_details.Resources if x.ResourceFamilyName == TRAFFIC_GENERATOR_CHASSIS_FAMILY]
            if not chassis:
                raise ValueError("No Traffic Generator Chassis Found in sandbox")
            if len(chassis) > 1:
                raise ValueError("Multiple traffic Generator Chassis found in sandbox")

            traffic_ports = [x for x in res_details.Resources if x.ResourceFamilyName == TRAFFIC_GENERATOR_PORT_FAMILY]
            if not traffic_ports:
                raise ValueError("No traffic generator ports found in sandbox")
            stats_payload = []
            for _ in traffic_ports:
                port_data = {
                    "L1Bytes": self._get_rand_int(),
                    "TrafficStream": self._get_rand_int(),
                }
                stats_payload.append(port_data)
            if is_json:
                json_res = json.dumps(stats_payload, indent=4)
                logger.debug(f"get statistics json response\n{json_res}")
                return json_res
            else:
                file_name = f"traffic_data_{str(datetime.now())}.txt"
                api = self._get_quali_api_from_context(context)
                csv_data = dict_to_csv_str(stats_payload)
                api.attach_file_to_reservation(sandbox_id=sb_id,
                                               data_str=csv_data,
                                               target_filename=file_name)
                msg = f"added {file_name} csv report to sandbox"
                logger.info(msg)
                return msg

    @staticmethod
    def _get_quali_api_from_context(context):
        """

        :param ResourceCommandContext context:
        :return:
        """
        try:
            api = QualiAPISession(host=context.connectivity.server_address,
                                  token=context.connectivity.admin_auth_token,
                                  domain=context.reservation.domain,
                                  port=context.connectivity.quali_api_port)
        except Exception as e:
            raise Exception(f"Failed to instantiate quali api. {type(e).__name__}: {str(e)}")

        return api

    @staticmethod
    def _get_rand_int():
        return randint(int(1e4), int(2e4))

    def send_arp(self, context):
        """Send ARP/ND for all protocols

        :param context:
        :return:
        """
        pass

    def start_protocols(self, context):
        """Start all protocols

        :param context:
        :return:
        """
        pass

    def stop_protocols(self, context):
        """Stop all protocols

        :param context:
        :return:
        """
        pass

    def run_quick_test(self, context):
        """Run quick test

        :param context:
        :return:
        """
        pass

    def get_session_id(self, context):
        """API only command to get REST session ID

        :param context:
        :return:
        """
        pass

    def get_children(self, context, obj_ref, child_type):
        """API only command to get list of children

        :param context:
        :param str obj_ref: valid object reference
        :param str child_type: requested children type. If None returns all children
        :return:
        """
        pass

    def get_attributes(self, context, obj_ref):
        """API only command to get object attributes

        :param context:
        :param str obj_ref: valid object reference
        :return:
        """
        pass

    def set_attribute(self, context, obj_ref, attr_name, attr_value):
        """API only command to set traffic generator object attribute

        :param context:
        :param str obj_ref: valid object reference
        :param str attr_name: attribute name
        :param str attr_value: attribute value
        :return:
        """
        pass

    def cleanup_reservation(self, context):
        """Clear reservation when it ends

        :param context:
        :return:
        """
        pass

    def cleanup(self, context):
        """

        :param context:
        :return:
        """
        pass

    def keep_alive(self, context, cancellation_context):
        """

        :param context:
        :param cancellation_context:
        :return:
        """
        pass
