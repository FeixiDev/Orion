import utils

class ServiceOperation(object):
    def __init__(self):
        pass


    def eviction_stop(self):
        """关闭auto-eviction服务"""
        cmd = "linstor controller sp DrbdOptions/AutoEvictAllowEviction false"
        result = utils.exec_cmd(cmd, )
        if result:
            if result["st"]:
                print("auto-eviction stops successfully")
            else:
                print("auto-eviction stops failing")

    def controller_start(self):
        """开启linstor controller服务"""
        cmd = "systemctl start linstor-controller"
        result = utils.exec_cmd(cmd, )
        if result:
            if result["st"]:
                print("linstor controller stops successfully")
            else:
                print("linstor controller stops failing")

    def controller_stop(self):
        """关闭linstor controller服务"""
        cmd = "systemctl stop linstor-controller"
        result = utils.exec_cmd(cmd, )
        if result:
            if result["st"]:
                print("linstor controller stops successfully")
            else:
                print("linstor controller stops failing")