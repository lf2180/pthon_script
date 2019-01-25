#!/usr/local/bin/python
#-*-coding:utf-8 -*-
import os
import ConfigParser
import argparse
import subprocess
import time
import shutil

import  logging
import requests
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fg = logging.FileHandler('/servers/scripts/python/deploy/log/dep.log')
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fg.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fg)
logger.addHandler(ch)

class register:
    def _argparse(self):
        parser = argparse.ArgumentParser(description='This is description')
        subparsers = parser.add_subparsers(dest='javacontainer',help='option project')

        cPortal_war = subparsers.add_parser('***')
        cPortal_war.add_argument('war_name', help='option', nargs='+', choices=['***', '***', '***', '***'])

        bPortal_war = subparsers.add_parser('***')
        bPortal_war.add_argument('war_name', help='option', nargs='+', choices=['***', '***', '***', '***'])

        backstage_war = subparsers.add_parser('***')
        backstage_war.add_argument('war_name', help='option', nargs='+', choices=['***', '***', '***', '***'])

        return parser.parse_args()
class readconfig:
    def __init__(self, config_name):
        self.config = ConfigParser.SafeConfigParser()
        self.config.read(config_name)
    def get(self, *args, **kwargs):
        return self.config.get(*args, **kwargs)
class war:
    def __init__(self, one, two):
        self.package_name = one
        self.package_two_name = two
    def down(self,war_config):
        war_dict={self.package_name:{}}
        for i in self.package_two_name:
            http_war = war_config.get(self.package_name, i)
            war_dict[self.package_name][i] = http_war
        return war_dict
    def download_war(self,war_dict,war_config):
        for project in war_dict:
            for war_name in war_dict[project]:
                logger.info(u'开始下载'+ war_dict[project][war_name])
                res = requests.get(war_dict[project][war_name])
                with open("%s%s.war"%(war_config.get('down_dir', 'down_dir'),war_name),"wb") as code:
                    code.write(res.content)
                logging.info("%s%s.war"%(war_config.get('down_dir', 'down_dir'), war_name))
class tomcat_manage:
    def __init__(self,war_config,war_dict):
        self.webapp = '/webapps/lvpai'
        self.start_bin = '/bin/startup.sh'
        self.stop_pid = '/TOMCAT_PID'
        self.war_config = war_config
        self.war_dict = war_dict
    def start(self):
        for config in sorted(self.war_dict):
            war_path = self.war_config.get('path',config)
            war_start = "sleep 5 &&sh %s%s"%(war_path,self.start_bin)
            logger.info(u'启动war包 %s %s'%(config,war_start))
            subprocess.check_output(war_start, shell=True, universal_newlines=True)
    def stop(self):
        for config in sorted(self.war_dict):
            logger.info(u"停止项目 %s"%(config))
            war_path = self.war_config.get('path',config)
            war_pid = "cat %s%s"%(war_path, self.stop_pid)
            pid = subprocess.check_output(war_pid, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
            pro_num = int(os.popen('ps -ef |grep %i|grep -v grep|wc -l' % (int(pid))).read())
            logger.info('进程号%i'%(pro_num))
            if pro_num >= 1:
                logger.info('kill ' + pid)
                subprocess.call("kill %i" %(int(pid)), shell=True)
            else:
                logger.info('pronum 小于1')
            count = 0
            while (count < 5):
                pro_num = int(os.popen('ps -ef |grep %i|grep -v grep|wc -l' % (int(pid))).read())
                if pro_num >= 1:
                    time.sleep(5)
                    count = count + 1
                    logger.info(pro_num)
                    logger.info(u'失败次数%i'%(count))
                else:
                    break
    def bak(self):
        bak_path = self.war_config.get('bak', 'back_path')
        for config in self.war_dict:
            for war_name in self.war_dict[config]:
                if war_name in ['cPortal','bPortal','backstage']:
                    war_path = "%s%s.war"%(self.war_config.get('special_path', war_name),
                                         war_name)
                    date = time.strftime("%Y-%m-%d-%H%M%S", time.localtime())
                    shutil.copy(war_path,'%s.%s'%(bak_path + '/' + war_name,date))
                    logger.info(u'开始备份，原始war包%s,备份war包%s'%(war_path,'%s.%s'%(bak_path + '/' + war_name,date)))
                else:
                    logger.info(config)
                    war_path = "%s/webapps/%s.war"%(self.war_config.get('path',config),war_name)
                    date = time.strftime("%Y-%m-%d-%H%M%S", time.localtime())
                    shutil.copy(war_path,'%s.%s'%(bak_path + '/' + war_name,date))
                    logger.info(u'开始备份，原始war包%s,备份war包%s'%(war_path,'%s.%s'%(bak_path + '/' + war_name,date)))
                    # print(war_path,'%s.%s'%(bak_path + '/' + war_name,date))

    def mvwar(self):
        for config in self.war_dict:
            for war_name in self.war_dict[config]:
                if war_name in ['cPortal','bPortal','backstage']:
                    del_path = "%s%s.war"%(self.war_config.get('special_path', war_name),
                                         war_name)
                    logger.info(u'开始删除，删除目录' + del_path)
                    os.remove(del_path)
                    down_dir="%s%s.war"%(self.war_config.get('down_dir', 'down_dir'), war_name)
                    shutil.move(down_dir, self.war_config.get('special_path', war_name))
                    logger.info(u'移动war包  原始包名：%s，移动目录%s'%(down_dir, self.war_config.get('special_path', war_name)))
                else:
                    del_path = "%s/webapps/%s.war"%(self.war_config.get('path', config), war_name)
                    down_dir = "%s%s.war" % (self.war_config.get('down_dir', 'down_dir'), war_name)
                    logger.info(u'开始删除，删除包名：' + del_path)
                    os.remove(del_path)
                    shutil.move(down_dir,del_path)
                    logger.info(u'移动war包  原始包名：%s，移动目录%s'%(down_dir,del_path))
class main:
    def __init__(self):
        a = register()
        parser = a._argparse()
        javacon = parser.javacontainer
        war_name = parser.war_name
        self.war_config = readconfig('/servers/scripts/python/deploy/config/deploy.conf')
        down = war(javacon, war_name)
        self.war_dict = down.down(self.war_config)
        down.download_war(self.war_dict, self.war_config)
    def rollback(self):
        pass
    def run(self):
        tomcat=tomcat_manage(self.war_config,self.war_dict)
        tomcat.bak()
        tomcat.stop()
        tomcat.mvwar()
        tomcat.start()
if __name__ == '__main__':
    a = main()
    a.run()

