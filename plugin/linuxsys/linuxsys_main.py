#!/usr/bin/python
#coding: utf-8
#-----------------------------
# 宝塔Linux面板内测插件
#-----------------------------
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
os.chdir('/www/server/panel');
sys.path.append("class/")
import public,db,time

class linuxsys_main:
    __setupPath = '/www/server/panel/plugin/linuxsys';
    #设置DNS
    def SetConfig(self,get):
        dnsStr = "nameserver " + get.dns1 + "\n" ;
        if get.dns2:
            dnsStr += "nameserver " + get.dns2 + '\n'
        public.writeFile('/etc/resolv.conf',dnsStr);
        return public.returnMsg(True,'设置成功!')
    
    #设置IP地址
    def SetAddress(self,get):
        if not self.CheckIp(get.address): return public.returnMsg(False,'IP地址不合法!');
        if not self.CheckIp(get.netmask): return public.returnMsg(False,'子网掩码不合法!');
        if not self.CheckIp(get.gateway): return public.returnMsg(False,'网关地址不合法!');
        cfile,devName = self.GetDevConf();
        if not os.path.exists(cfile): return public.returnMsg(False,'无法正确获取设备名称!');
        timeOut = public.do_one(get.address,0.5);
        if timeOut: return public.returnMsg(False,'IP地址已被其它计算机使用!');
        import re;
        for i in range(100):
            if i < 1: continue;
            pfile = cfile + ':' + str(i)
            newName = devName +':'+ str(i);
            if not os.path.exists(pfile): break;
            conf = public.readFile(pfile);
            rep = "IPADDR\d*\s*=\s*(.+)\n";
            tmp = re.search(rep,conf);
            if not tmp: continue;
            if tmp.groups()[0] == get.address: return public.returnMsg(False,'指定IP地址已添加过!');
    
        cconfig = public.readFile(cfile)
        rep = "DEVICE\s*=\s*\w+\n";
        cconfig = re.sub(rep,'DEVICE=' + newName + '\n',cconfig);
        rep = "NAME\s*=\s*\w+\n";
        cconfig = re.sub(rep,'NAME=' + newName + '\n',cconfig);
        rep = "IPADDR\d*\s*=\s*.+\n";
        cconfig = re.sub(rep,'IPADDR=' + get.address + '\n',cconfig);
        rep = "NETMASK\s*=\s*.+\n";
        cconfig = re.sub(rep,"NETMASK="+get.netmask+"\n",cconfig);
        rep = "GATEWAY\s*=\s*.+\n";
        cconfig = re.sub(rep,"GATEWAY="+get.gateway+"\n",cconfig);
        
        public.writeFile(pfile,cconfig);
        return public.returnMsg(True,'添加成功!');
    #验证IP合法性
    def CheckIp(self,address):
        try:
            if address.find('.') == -1: return False;
            iptmp = address.split('.');
            if len(iptmp) != 4: return False;
            for ip in iptmp:
                if int(ip) > 255: return False
            return True
        except:
            return False
    
    #删除IP
    def DelAddress(self,get):
        if not self.CheckIp(get.address): return public.returnMsg(False,'IP地址不合法!');
        cfile,devName = self.GetDevConf();
        if not os.path.exists(cfile): return public.returnMsg(False,'无法正确获取设备名称!');
        isDel = False;
        import re;
        for i in range(100):
            if i < 1: continue;
            pfile = cfile + ':' + str(i);
            if not os.path.exists(pfile): continue;
            conf = public.readFile(pfile);
            rep = "IPADDR\d*\s*=\s*(.+)\n";
            tmp = re.search(rep,conf);
            if not tmp: continue;
            if tmp.groups()[0] == get.address:
                os.system('rm -f ' + pfile);
                isDel = True;
                break;
        if isDel: return public.returnMsg(True,'删除成功!');
        return public.returnMsg(False,'此IP不能删除');
    
    #获取网卡配置文件地址
    def GetDevConf(self):
        devName = 'eth0';
        cfile = '/etc/sysconfig/network-scripts/ifcfg-' + devName;
        try:
            if not os.path.exists(cfile): devName = 'eno16777736';
            if not os.path.exists(cfile): devName = 'eno1';
            if not os.path.exists(cfile):
                devName = public.ExecShell("ip add |grep LOWER_UP|grep -v lo|sed 's/://g'|awk '{print $2}'")[0].split()[0].strip()
            cfile = '/etc/sysconfig/network-scripts/ifcfg-' + devName
            return cfile,devName
        except:
            return cfile,devName
        
    
    #网卡配置补全
    def CheckConfig(self,get):
        if not self.CheckIp(get.address): return public.returnMsg(False,'IP地址不合法!');
        if not self.CheckIp(get.netmask): return public.returnMsg(False,'子网掩码不合法!');
        if not self.CheckIp(get.gateway): return public.returnMsg(False,'网关地址不合法!');
        cfile,devName = self.GetDevConf();
        if not os.path.exists(cfile): return public.returnMsg(False,'无法正确获取设备名称!');
        import re
        conf = public.readFile(cfile);
        rep = "ONBOOT\s*=\s*.+\n";
        if not re.search(rep,conf): 
            conf += "\nONBOOT=yes";
        else:
            conf = re.sub(rep,"ONBOOT=yes\n",conf);
        
        rep = "BOOTPROTO\s*=\s*\w+\n";
        if not re.search(rep,conf):
            conf += "\nBOOTPROTO=static";
        else:
            conf = re.sub(rep,"BOOTPROTO=static\n",conf);
        
        rep = "IPADDR\s*=\s*.+\n";
        if not re.search(rep,conf):
            conf += "\nIPADDR="+get.address;
        else:
            conf = re.sub(rep,"IPADDR="+get.address+"\n",conf);
        rep = "NETMASK\s*=\s*.+\n";
        if not re.search(rep,conf):
            conf += "\nNETMASK="+get.netmask;
        else:
            conf = re.sub(rep,"NETMASK="+get.netmask+"\n",conf);
            
        rep = "GATEWAY\s*=\s*.+\n";
        if not re.search(rep,conf):
            conf += "\nGATEWAY="+get.gateway;
        else:
            conf = re.sub(rep,"GATEWAY="+get.gateway+"\n",conf);
        
        public.writeFile(cfile,conf)
        return public.returnMsg(True,'初始化网卡成功');
                
    
    #重载网络
    def ReloadNetwork(self,get):
        if os.path.exists('/usr/bin/systemctl'):
            os.system('systemctl restart network.service');
        else:
            os.system('service network reload');
        return public.returnMsg(True,'网络已重启!');
        
    
    #获取IP地址
    def GetAddress(self,get):
        if not os.path.exists('/etc/redhat-release'): return False;
        import re;
        cfile,devName = self.GetDevConf();
        if not os.path.exists(cfile): return public.returnMsg(False,'无法正确获取设备名称!');
        conf = public.readFile(cfile);
        rep = "BOOTPROTO\s*=\s*(.+)\n";
        try:
            if re.search(rep,conf).groups()[0].replace("'",'').lower() == 'dhcp': return public.returnMsg(False,'未初始化网卡!');
        except:
            return public.returnMsg(False,'未初始化网卡!');

        result = []
        for i in range(100):
            if i < 1:
                pfile = cfile;
            else:
                pfile = cfile + ':' + str(i);
            if not os.path.exists(pfile): continue;
            tmp = {}
            conf = public.readFile(pfile);
            rep = "IPADDR\d*\s*=\s*(.+)\n";
            tmp['address'] = re.search(rep,conf).groups()[0].replace("'",'');
            rep = "GATEWAY\d*\s*=\s*(.+)\n";
            tmp['gateway'] = re.search(rep,conf).groups()[0].replace("'",'');
            rep = "NETMASK\d*\s*=\s*(.+)\n";
            tmp['netmask'] = re.search(rep,conf).groups()[0].replace("'",'');
            result.append(tmp);
        return result;
    
    #取DNS信息
    def GetConfig(self,get):
        dnsStr = public.ExecShell('cat /etc/resolv.conf|grep nameserver')
        tmp = dnsStr[0].split()
        dnsInfo = {}
        dnsInfo['dns1'] = ''
        dnsInfo['dns2'] = ''
        if len(tmp) > 1:
            dnsInfo['dns1'] = tmp[1];
        if len(tmp) > 2:
            dnsInfo['dns2'] = tmp[3];
        return dnsInfo;
    
    #测试DNS
    def TestDns(self,get):
        resolv = '/etc/resolv.conf'
        dnsStr = "nameserver " + get.dns1 + "\n" + "nameserver " + get.dns2;
        backupDns = public.readFile(resolv)
        public.writeFile(resolv,dnsStr);
        tmp = public.ExecShell("ping -c 1 -w 1 www.qq.com")
        isPing = False
        try:
            if tmp[0].split('time=')[1].split()[0]: isPing = True
        except:
            pass
        public.writeFile(resolv,backupDns);
        if isPing:
            return public.returnMsg(True,'当前DNS可用!<br>'+tmp[0].replace('\n','<br>'))
        return public.returnMsg(False,'当前DNS不可用!<br>'+tmp[1])

    #获取SWAP信息
    def GetSwap(self,get):
        swapStr = public.ExecShell('free -m|grep Swap')
        tmp = swapStr[0].split();
        swapInfo = {}
        swapInfo['total'] = int(tmp[1])
        swapInfo['used'] = int(tmp[2])
        swapInfo['free'] = int(tmp[3])
        swapInfo['size'] = 0
        if os.path.exists('/www/swap'):
            swapInfo['size'] = os.path.getsize('/www/swap')
        return swapInfo;
        
    
    #设置SWAP
    def SetSwap(self,get):
        swapFile = '/www/swap'
        if os.path.exists(swapFile):
            os.system('swapoff ' + swapFile)
            os.system('rm -f ' + swapFile)
            os.system('sed -i "/'+swapFile.replace('/','\\/')+'/d" /etc/fstab')
        if float(get.size) > 1:
            import system
            disk = system.system().GetDiskInfo();
            dsize = 0
            isSize = True
            for d in disk:
                if d['path'] == '/www': dsize = d['size'][2]
                if d['path'] == '/':
                    if not dsize: dsize = d['size'][2]
            if dsize.find('T') != -1:
                fsize = dsize.replace('T','')
                if (float(fsize) * 1024 * 1024) < float(get.size): isSize = False
			
            if dsize.find('G') != -1:
                fsize = dsize.replace('G','')
                if (float(fsize) * 1024) < float(get.size): isSize = False
			
            if dsize.find('M') != -1:
                fsize = dsize.replace('M','')
                if float(fsize) < float(get.size): isSize = False
                
            if not isSize:
                data = self.GetSwap(get);
                data['status'] = False
                data['msg'] = '失败，磁盘空间不足，当前可用空间：' + dsize
                return data;
            
            os.system('dd if=/dev/zero of='+swapFile+' bs=1M count=' + get.size)
            os.system('mkswap -f ' + swapFile)
            os.system('swapon ' + swapFile)
            os.system('echo "'+ swapFile +'    swap    swap    defaults    0 0" >> /etc/fstab')
        data = self.GetSwap(get);
        data['status'] = True
        data['msg'] = '设置成功'
        return data;
    
    #获取时区
    def GetZoneinfo(self,get):
        zoneList = ['Asia','Africa','America','Antarctica','Arctic','Atlantic','Australia','Europe','Indian','Pacific']
        areaList = []
        for area in os.listdir('/usr/share/zoneinfo/'+get.zone):
            areaList.append(area)
        data = {}
        data['zoneList'] = zoneList
        data['areaList'] = sorted(areaList)
        data['zone'] = get.zone;
        data['date'] = public.ExecShell('date +"%Y-%m-%d %H:%M:%S %Z %z"')[0];
        return data;
    
    #设置时区
    def SetZone(self,get):
        os.system('rm -f /etc/localtime')
        os.system("\cp -a -r '/usr/share/zoneinfo/" + get.zone + "/" + get.area + "' '/etc/localtime'")
        data = self.GetZoneinfo(get)
        data['status'] = True
        data['msg'] = "设置成功!"
        return data
    
    #取当前用户名
    def GetRoot(self,get):
        try:
            return public.ExecShell("who|awk '{print $1}'")[0].split()[0]
        except:
            return 'root';
    
    #修改用户密码
    def SetRoot(self,get):
        if not get.user: return public.returnMsg(False,"用户名不能为空!");
        if get.passwd1 != get.passwd2: return public.returnMsg(False,"两次输入的密码不一致!");
        os.system('(echo "'+get.passwd1.strip()+'";sleep 1;echo "'+get.passwd2.strip()+'")|passwd ' + get.user);
        return public.returnMsg(True,'修改成功!');  
    
