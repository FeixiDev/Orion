import execute as ex
import sundry as sd
import execute.service as se


class Usage():
    # host部分使用手册
    eviction = '''
    eviction(e) {stop}'''

    eviction_stop = '''
    eviction(e) stop'''

    controller = ''''
    controller(c) {start/stop}'''

    controller_start = '''
    controller(c) start'''

    controller_stop = '''
    controller(c) stop'''

class ServiceCommands():
    def __init__(self):
        pass

    def setup_commands(self, parser):
        """
        eviction
        """
        eviction_parser = parser.add_parser(
            'eviction',
            aliases='e',
            help='eviction service operation',
            usage=Usage.eviction)
        self.eviction_parser = eviction_parser
        eviction_subp = eviction_parser.add_subparsers(dest='subargs_eviction')

        """
        eviction stop
        """

        p_eviction_stop = eviction_subp.add_parser(
            'stop',
            help='Stop the eviction service',
            usage=Usage.eviction_stop)
        self.p_eviction_stop = p_eviction_stop

        p_eviction_stop.set_defaults(func=self.eviction_stop)

        """
        controller
        """
        controller_parser = parser.add_parser(
            'controller',
            aliases='c',
            help='controller service operation',
            usage=Usage.controller)
        self.controller_parser = controller_parser
        controller_subp = controller_parser.add_subparsers(dest='subargs_controller')

        """
        controller start
        """

        p_controller_start = controller_subp.add_parser(
            'start',
            help='Start the controller service',
            usage=Usage.controller_start)
        self.p_controller_start = p_controller_start

        p_controller_start.set_defaults(func=self.controller_start)

        """
        controller stop
        """

        p_controller_stop = controller_subp.add_parser(
            'stop',
            help='Stop the controller service',
            usage=Usage.controller_stop)
        self.p_controller_stop = p_controller_stop
        p_controller_stop.set_defaults(func=self.controller_stop)

        eviction_parser.set_defaults(func=self.print_eviction_help)
        controller_parser.set_defaults(func=self.print_controller_help)



    @sd.deco_record_exception
    def eviction_stop(self, args):
        print("this is eviction_stop")
        service_operation = se.ServiceOperation()
        service_operation.eviction_stop()


    @sd.deco_record_exception
    def controller_start(self, args):
        print("this is controller_start")
        service_operation = se.ServiceOperation()
        service_operation.controller_start()

    @sd.deco_record_exception
    def controller_stop(self, args):
        print("this is controller_stop")
        service_operation = se.ServiceOperation()
        service_operation.controller_stop()


    def print_eviction_help(self, *args):
        self.eviction_parser.print_help()

    def print_controller_help(self, *args):
        self.controller_parser.print_help()
