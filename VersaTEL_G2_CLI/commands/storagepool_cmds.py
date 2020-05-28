import argparse
import pickle

import sundry as sd
import execute as ex
import linstordb


class usage():
    storagepool = '''
    storagepool(sp) {create(c)/modify(m)/delete(d)/show(s)}'''

    storagepool_create = '''
    storagepool(sp) create(c) STORAGEPOOL -n NODE -lvm LVM/-tlv THINLV'''

    storagepool_delete = '''
    storagepool(sp) delete(d) STORAGEPOOL -n NODE'''

    # 待完善
    storagepool_modify = '''
    storagepool(sp) modify(m) STORAGEPOOL ...'''

    storagepool_show = '''
    storagepool(sp) show(s) [STORAGEPOOL]'''


class StoragePoolCommands():
    def __init__(self):
        pass

    def setup_commands(self, parser):
        """
        sp(storage pool)
        Add commands for the storage pool management:create,modify,delete,show
        :param:parser:sub-parser of the previous command
        """
        sp_parser = parser.add_parser(
            'storagepool',
            aliases=['sp'],
            help='Management operations for storagepool',
            usage=usage.storagepool)

        sp_subp = sp_parser.add_subparsers(
            dest='subargs_sp')

        """
        Create LINSTOR Storage Pool
        """
        p_create_sp = sp_subp.add_parser(
            'create',
            aliases='c',
            help='Create the storagpool',
            usage=usage.storagepool_create)

        p_create_sp.add_argument(
            'storagepool',
            metavar='STORAGEPOOL',
            action='store',
            help='Name of the new storage pool')
        p_create_sp.add_argument(
            '-n',
            dest='node',
            action='store',
            help='Name of the node for the new storage pool',
            required=True)
        p_create_sp.add_argument(
            '-gui',
            dest='gui',
            action='store_true',
            help=argparse.SUPPRESS,
            default=False)
        group_type = p_create_sp.add_mutually_exclusive_group()
        group_type.add_argument(
            '-lvm',
            dest='lvm',
            action='store',
            help='The Lvm volume group to use.')
        group_type.add_argument(
            '-tlv',
            dest='tlv',
            action='store',
            help='The LvmThin volume group to use. The full name of the thin pool, namely VG/LV')

        self.p_create_sp = p_create_sp
        p_create_sp.set_defaults(func=self.create)

        """
        Modify LISNTOR Storage Pool
        """
        pass

        """
        Delete LISNTOR Storage Pool
        """
        p_delete_sp = sp_subp.add_parser(
            'delete',
            aliases='d',
            help='Delete the storagpool',
            usage=usage.storagepool_delete)

        p_delete_sp.add_argument(
            'storagepool',
            metavar='STORAGEPOOL',
            help='Name of the storage pool to delete',
            action='store')
        p_delete_sp.add_argument(
            '-n',
            dest='node',
            action='store',
            help='Name of the Node where the storage pool exists',
            required=True)
        p_delete_sp.add_argument(
            '-y',
            dest='yes',
            action='store_true',
            help='Skip to confirm selection',
            default=False)
        p_delete_sp.add_argument(
            '-gui',
            dest='gui',
            action='store_true',
            help=argparse.SUPPRESS,
            default=False)

        p_delete_sp.set_defaults(func=self.delete)

        """
        Show LISNTOR Storage Pool
        """
        p_show_sp = sp_subp.add_parser(
            'show',
            aliases='s',
            help='Displays the storagpool view',
            usage=usage.storagepool_show)

        p_show_sp.add_argument(
            'storagepool',
            metavar='STORAGEPOOL',
            help='Print information about the storage pool in LINSTOR cluster',
            action='store',
            nargs='?')
        p_show_sp.add_argument(
            '--no-color',
            dest='nocolor',
            help='Do not use colors in output.',
            action='store_true',
            default=False)

        p_show_sp.set_defaults(func=self.show)

    def create(self, args):
        if args.storagepool and args.node:
            # The judgment of the lvm module to create a storage pool
            if args.lvm:
                if args.gui:
                    result = ex.Stor.create_storagepool_lvm(
                        args.node, args.storagepool, args.lvm)
                    result_pickled = pickle.dumps(result)
                    sd.send_via_socket(result_pickled)
                else:
                    ex.Stor.create_storagepool_lvm(
                        args.node, args.storagepool, args.lvm)
            # The judgment of the thin-lv module to create a storage pool
            elif args.tlv:
                if args.gui:
                    result = ex.Stor.create_storagepool_thinlv(
                        args.node, args.storagepool, args.tlv)
                    result_pickled = pickle.dumps(result)
                    sd.send_via_socket(result_pickled)
                else:
                    ex.Stor.create_storagepool_thinlv(
                        args.node, args.storagepool, args.tlv)
            else:
                self.p_create_sp.print_help()
        else:
            self.p_create_sp.print_help()

    def modify(self):
        pass

    @sd.comfirm_del('storage pool')
    def delete(self, args):
        ex.Stor.delete_storagepool(args.node, args.storagepool)

    def show(self, args):
        tb = linstordb.OutputData()
        if args.nocolor:
            tb.show_sp_one(
                args.storagepool) if args.storagepool else tb.sp_all()
        else:
            tb.show_sp_one_color(
                args.storagepool) if args.storagepool else tb.sp_all_color()