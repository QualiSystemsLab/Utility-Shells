from cloudshell.shell.core.driver_context import ResourceCommandContext, AutoLoadDetails, AutoLoadAttribute, \
    AutoLoadResource
from collections import defaultdict


class LegacyUtils(object):
    def __init__(self):
        self._datamodel_clss_dict = self.__generate_datamodel_classes_dict()

    def migrate_autoload_details(self, autoload_details, context):
        model_name = context.resource.model
        root_name = context.resource.name
        root = self.__create_resource_from_datamodel(model_name, root_name)
        attributes = self.__create_attributes_dict(autoload_details.attributes)
        self.__attach_attributes_to_resource(attributes, '', root)
        self.__build_sub_resoruces_hierarchy(root, autoload_details.resources, attributes)
        return root

    def __create_resource_from_datamodel(self, model_name, res_name):
        return self._datamodel_clss_dict[model_name](res_name)

    def __create_attributes_dict(self, attributes_lst):
        d = defaultdict(list)
        for attribute in attributes_lst:
            d[attribute.relative_address].append(attribute)
        return d

    def __build_sub_resoruces_hierarchy(self, root, sub_resources, attributes):
        d = defaultdict(list)
        for resource in sub_resources:
            splitted = resource.relative_address.split('/')
            parent = '' if len(splitted) == 1 else resource.relative_address.rsplit('/', 1)[0]
            rank = len(splitted)
            d[rank].append((parent, resource))

        self.__set_models_hierarchy_recursively(d, 1, root, '', attributes)

    def __set_models_hierarchy_recursively(self, dict, rank, manipulated_resource, resource_relative_addr, attributes):
        if rank not in dict: # validate if key exists
            pass

        for (parent, resource) in dict[rank]:
            if parent == resource_relative_addr:
                sub_resource = self.__create_resource_from_datamodel(
                    resource.model.replace(' ', ''),
                    resource.name)
                self.__attach_attributes_to_resource(attributes, resource.relative_address, sub_resource)
                manipulated_resource.add_sub_resource(
                    self.__slice_parent_from_relative_path(parent, resource.relative_address), sub_resource)
                self.__set_models_hierarchy_recursively(
                    dict,
                    rank + 1,
                    sub_resource,
                    resource.relative_address,
                    attributes)

    def __attach_attributes_to_resource(self, attributes, curr_relative_addr, resource):
        for attribute in attributes[curr_relative_addr]:
            setattr(resource, attribute.attribute_name.lower().replace(' ', '_'), attribute.attribute_value)
        del attributes[curr_relative_addr]

    def __slice_parent_from_relative_path(self, parent, relative_addr):
        if parent is '':
            return relative_addr
        return relative_addr[len(parent) + 1:] # + 1 because we want to remove the seperator also

    def __generate_datamodel_classes_dict(self):
        return dict(self.__collect_generated_classes())

    def __collect_generated_classes(self):
        import sys, inspect
        return inspect.getmembers(sys.modules[__name__], inspect.isclass)


class TrafficChassisMock(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'Traffic Chassis Mock'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype TrafficChassisMock
        """
        result = TrafficChassisMock(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'TrafficChassisMock'

    @property
    def user(self):
        """
        :rtype: str
        """
        return self.attributes['Traffic Chassis Mock.User'] if 'Traffic Chassis Mock.User' in self.attributes else None

    @user.setter
    def user(self, value):
        """
        User with administrative privileges
        :type value: str
        """
        self.attributes['Traffic Chassis Mock.User'] = value

    @property
    def password(self):
        """
        :rtype: string
        """
        return self.attributes['Traffic Chassis Mock.Password'] if 'Traffic Chassis Mock.Password' in self.attributes else None

    @password.setter
    def password(self, value):
        """
        Password
        :type value: string
        """
        self.attributes['Traffic Chassis Mock.Password'] = value

    @property
    def controller_tcp_port(self):
        """
        :rtype: str
        """
        return self.attributes['Traffic Chassis Mock.Controller TCP Port'] if 'Traffic Chassis Mock.Controller TCP Port' in self.attributes else None

    @controller_tcp_port.setter
    def controller_tcp_port(self, value):
        """
        The TCP port of the traffic server. Relevant only in case an external server is configured. Default TCP port should be used if kept empty.
        :type value: str
        """
        self.attributes['Traffic Chassis Mock.Controller TCP Port'] = value

    @property
    def controller_address(self):
        """
        :rtype: str
        """
        return self.attributes['Traffic Chassis Mock.Controller Address'] if 'Traffic Chassis Mock.Controller Address' in self.attributes else None

    @controller_address.setter
    def controller_address(self, value):
        """
        The IP address of the traffic server. Relevant only in case an external server is configured.
        :type value: str
        """
        self.attributes['Traffic Chassis Mock.Controller Address'] = value

    @property
    def client_install_path(self):
        """
        :rtype: str
        """
        return self.attributes['Traffic Chassis Mock.Client Install Path'] if 'Traffic Chassis Mock.Client Install Path' in self.attributes else None

    @client_install_path.setter
    def client_install_path(self, value):
        """
        The path in which the traffic client is installed on the Execution Server. For example "C:/Program Files (x86)/Ixia/IxLoad/5.10-GA".
        :type value: str
        """
        self.attributes['Traffic Chassis Mock.Client Install Path'] = value

    @property
    def power_management(self):
        """
        :rtype: bool
        """
        return self.attributes['Traffic Chassis Mock.Power Management'] if 'Traffic Chassis Mock.Power Management' in self.attributes else None

    @power_management.setter
    def power_management(self, value=True):
        """
        Used by the power management orchestration, if enabled, to determine whether to automatically manage the device power status. Enabled by default.
        :type value: bool
        """
        self.attributes['Traffic Chassis Mock.Power Management'] = value

    @property
    def serial_number(self):
        """
        :rtype: str
        """
        return self.attributes['Traffic Chassis Mock.Serial Number'] if 'Traffic Chassis Mock.Serial Number' in self.attributes else None

    @serial_number.setter
    def serial_number(self, value):
        """
        The serial number of the resource.
        :type value: str
        """
        self.attributes['Traffic Chassis Mock.Serial Number'] = value

    @property
    def server_description(self):
        """
        :rtype: str
        """
        return self.attributes['Traffic Chassis Mock.Server Description'] if 'Traffic Chassis Mock.Server Description' in self.attributes else None

    @server_description.setter
    def server_description(self, value):
        """
        The full description of the server. Usually includes the OS, exact firmware version and additional characteritics of the device.
        :type value: str
        """
        self.attributes['Traffic Chassis Mock.Server Description'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value

    @property
    def model_name(self):
        """
        :rtype: str
        """
        return self.attributes['CS_TrafficGeneratorChassis.Model Name'] if 'CS_TrafficGeneratorChassis.Model Name' in self.attributes else None

    @model_name.setter
    def model_name(self, value=''):
        """
        The catalog name of the device model. This attribute will be displayed in CloudShell instead of the CloudShell model.
        :type value: str
        """
        self.attributes['CS_TrafficGeneratorChassis.Model Name'] = value

    @property
    def vendor(self):
        """
        :rtype: str
        """
        return self.attributes['CS_TrafficGeneratorChassis.Vendor'] if 'CS_TrafficGeneratorChassis.Vendor' in self.attributes else None

    @vendor.setter
    def vendor(self, value):
        """
        The name of the device manufacture.
        :type value: str
        """
        self.attributes['CS_TrafficGeneratorChassis.Vendor'] = value

    @property
    def version(self):
        """
        :rtype: str
        """
        return self.attributes['CS_TrafficGeneratorChassis.Version'] if 'CS_TrafficGeneratorChassis.Version' in self.attributes else None

    @version.setter
    def version(self, value):
        """
        The firmware version of the resource.
        :type value: str
        """
        self.attributes['CS_TrafficGeneratorChassis.Version'] = value


class GenericTrafficGeneratorModule(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'Traffic Chassis Mock.GenericTrafficGeneratorModule'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype GenericTrafficGeneratorModule
        """
        result = GenericTrafficGeneratorModule(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'GenericTrafficGeneratorModule'

    @property
    def version(self):
        """
        :rtype: str
        """
        return self.attributes['Traffic Chassis Mock.GenericTrafficGeneratorModule.Version'] if 'Traffic Chassis Mock.GenericTrafficGeneratorModule.Version' in self.attributes else None

    @version.setter
    def version(self, value=''):
        """
        The firmware version of the resource.
        :type value: str
        """
        self.attributes['Traffic Chassis Mock.GenericTrafficGeneratorModule.Version'] = value

    @property
    def serial_number(self):
        """
        :rtype: str
        """
        return self.attributes['Traffic Chassis Mock.GenericTrafficGeneratorModule.Serial Number'] if 'Traffic Chassis Mock.GenericTrafficGeneratorModule.Serial Number' in self.attributes else None

    @serial_number.setter
    def serial_number(self, value=''):
        """
        
        :type value: str
        """
        self.attributes['Traffic Chassis Mock.GenericTrafficGeneratorModule.Serial Number'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value

    @property
    def model_name(self):
        """
        :rtype: str
        """
        return self.attributes['CS_TrafficGeneratorModule.Model Name'] if 'CS_TrafficGeneratorModule.Model Name' in self.attributes else None

    @model_name.setter
    def model_name(self, value=''):
        """
        The catalog name of the device model. This attribute will be displayed in CloudShell instead of the CloudShell model.
        :type value: str
        """
        self.attributes['CS_TrafficGeneratorModule.Model Name'] = value


class GenericTrafficGeneratorPortGroup(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'Traffic Chassis Mock.GenericTrafficGeneratorPortGroup'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype GenericTrafficGeneratorPortGroup
        """
        result = GenericTrafficGeneratorPortGroup(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'GenericTrafficGeneratorPortGroup'

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value


class GenericTrafficGeneratorPort(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'Traffic Chassis Mock.GenericTrafficGeneratorPort'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype GenericTrafficGeneratorPort
        """
        result = GenericTrafficGeneratorPort(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'GenericTrafficGeneratorPort'

    @property
    def media_type(self):
        """
        :rtype: str
        """
        return self.attributes['Traffic Chassis Mock.GenericTrafficGeneratorPort.Media Type'] if 'Traffic Chassis Mock.GenericTrafficGeneratorPort.Media Type' in self.attributes else None

    @media_type.setter
    def media_type(self, value):
        """
        Interface media type. Possible values are Fiber and/or Copper (comma-separated).
        :type value: str
        """
        self.attributes['Traffic Chassis Mock.GenericTrafficGeneratorPort.Media Type'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value

    @property
    def max_speed(self):
        """
        :rtype: str
        """
        return self.attributes['CS_TrafficGeneratorPort.Max Speed'] if 'CS_TrafficGeneratorPort.Max Speed' in self.attributes else None

    @max_speed.setter
    def max_speed(self, value):
        """
        Max speed supported by the interface (default units - MB)
        :type value: str
        """
        self.attributes['CS_TrafficGeneratorPort.Max Speed'] = value

    @property
    def logical_name(self):
        """
        :rtype: str
        """
        return self.attributes['CS_TrafficGeneratorPort.Logical Name'] if 'CS_TrafficGeneratorPort.Logical Name' in self.attributes else None

    @logical_name.setter
    def logical_name(self, value):
        """
        The port's logical name in the test configuration. If kept emtpy - allocation will applied in the blue print.
        :type value: str
        """
        self.attributes['CS_TrafficGeneratorPort.Logical Name'] = value

    @property
    def configured_controllers(self):
        """
        :rtype: str
        """
        return self.attributes['CS_TrafficGeneratorPort.Configured Controllers'] if 'CS_TrafficGeneratorPort.Configured Controllers' in self.attributes else None

    @configured_controllers.setter
    def configured_controllers(self, value):
        """
        specifies what controller can be used with the ports (IxLoad controller, BP controller etc...)
        :type value: str
        """
        self.attributes['CS_TrafficGeneratorPort.Configured Controllers'] = value


class GenericTrafficGeneratorEndPoint(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'Traffic Chassis Mock.GenericTrafficGeneratorEndPoint'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype GenericTrafficGeneratorEndPoint
        """
        result = GenericTrafficGeneratorEndPoint(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'GenericTrafficGeneratorEndPoint'

    @property
    def version(self):
        """
        :rtype: str
        """
        return self.attributes['Traffic Chassis Mock.GenericTrafficGeneratorEndPoint.Version'] if 'Traffic Chassis Mock.GenericTrafficGeneratorEndPoint.Version' in self.attributes else None

    @version.setter
    def version(self, value):
        """
        The OS and client version of the endpoint.
        :type value: str
        """
        self.attributes['Traffic Chassis Mock.GenericTrafficGeneratorEndPoint.Version'] = value

    @property
    def address(self):
        """
        :rtype: str
        """
        return self.attributes['Traffic Chassis Mock.GenericTrafficGeneratorEndPoint.Address'] if 'Traffic Chassis Mock.GenericTrafficGeneratorEndPoint.Address' in self.attributes else None

    @address.setter
    def address(self, value):
        """
        The IP address of the endpoint.
        :type value: str
        """
        self.attributes['Traffic Chassis Mock.GenericTrafficGeneratorEndPoint.Address'] = value

    @property
    def identifier(self):
        """
        :rtype: str
        """
        return self.attributes['Traffic Chassis Mock.GenericTrafficGeneratorEndPoint.Identifier'] if 'Traffic Chassis Mock.GenericTrafficGeneratorEndPoint.Identifier' in self.attributes else None

    @identifier.setter
    def identifier(self, value):
        """
        The unique ID of the endpoint.
        :type value: str
        """
        self.attributes['Traffic Chassis Mock.GenericTrafficGeneratorEndPoint.Identifier'] = value

    @property
    def ssid(self):
        """
        :rtype: str
        """
        return self.attributes['Traffic Chassis Mock.GenericTrafficGeneratorEndPoint.SSID'] if 'Traffic Chassis Mock.GenericTrafficGeneratorEndPoint.SSID' in self.attributes else None

    @ssid.setter
    def ssid(self, value):
        """
        The endpoints's SSID. If kept emtpy - allocation will applied in the blue print.
        :type value: str
        """
        self.attributes['Traffic Chassis Mock.GenericTrafficGeneratorEndPoint.SSID'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value

    @property
    def logical_name(self):
        """
        :rtype: str
        """
        return self.attributes['CS_TrafficGeneratorEndPoint.Logical Name'] if 'CS_TrafficGeneratorEndPoint.Logical Name' in self.attributes else None

    @logical_name.setter
    def logical_name(self, value):
        """
        The endpoints's logical name in the test configuration. If kept emtpy - allocation will applied in the blue print.
        :type value: str
        """
        self.attributes['CS_TrafficGeneratorEndPoint.Logical Name'] = value


class GenericPowerPort(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'Traffic Chassis Mock.GenericPowerPort'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype GenericPowerPort
        """
        result = GenericPowerPort(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'GenericPowerPort'

    @property
    def model(self):
        """
        :rtype: str
        """
        return self.attributes['Traffic Chassis Mock.GenericPowerPort.Model'] if 'Traffic Chassis Mock.GenericPowerPort.Model' in self.attributes else None

    @model.setter
    def model(self, value):
        """
        The device model. This information is typically used for abstract resource filtering.
        :type value: str
        """
        self.attributes['Traffic Chassis Mock.GenericPowerPort.Model'] = value

    @property
    def serial_number(self):
        """
        :rtype: str
        """
        return self.attributes['Traffic Chassis Mock.GenericPowerPort.Serial Number'] if 'Traffic Chassis Mock.GenericPowerPort.Serial Number' in self.attributes else None

    @serial_number.setter
    def serial_number(self, value):
        """
        
        :type value: str
        """
        self.attributes['Traffic Chassis Mock.GenericPowerPort.Serial Number'] = value

    @property
    def version(self):
        """
        :rtype: str
        """
        return self.attributes['Traffic Chassis Mock.GenericPowerPort.Version'] if 'Traffic Chassis Mock.GenericPowerPort.Version' in self.attributes else None

    @version.setter
    def version(self, value):
        """
        The firmware version of the resource.
        :type value: str
        """
        self.attributes['Traffic Chassis Mock.GenericPowerPort.Version'] = value

    @property
    def port_description(self):
        """
        :rtype: str
        """
        return self.attributes['Traffic Chassis Mock.GenericPowerPort.Port Description'] if 'Traffic Chassis Mock.GenericPowerPort.Port Description' in self.attributes else None

    @port_description.setter
    def port_description(self, value):
        """
        The description of the port as configured in the device.
        :type value: str
        """
        self.attributes['Traffic Chassis Mock.GenericPowerPort.Port Description'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value

    @property
    def model_name(self):
        """
        :rtype: str
        """
        return self.attributes['CS_PowerPort.Model Name'] if 'CS_PowerPort.Model Name' in self.attributes else None

    @model_name.setter
    def model_name(self, value=''):
        """
        The catalog name of the device model. This attribute will be displayed in CloudShell instead of the CloudShell model.
        :type value: str
        """
        self.attributes['CS_PowerPort.Model Name'] = value



