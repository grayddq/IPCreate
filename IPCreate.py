# -*- coding: utf-8 -*-

import re,os,optparse

#脚本功能为：通过指定IP网段列表文件，生成所有可用的ip信息
#
#脚本使用如下：
#python IPCreate.py
#
#默认会识别当前ip.txt文件，也可通过-f ip.txt来指定，文件内容格式为一行一条，支持如下格式：
#支持127.0.0.1-127.0.1.1
#支持127.0.0.1/24
#支持127.0.0.1
#
#默认会输出out.txt文件，文件内容为所有的可用的ip信息，一行一条。
#


NAME, VERSION, AUTHOR, LICENSE = "IPCreate", "V0.1", "咚咚呛", "Public (FREE)"

class IPCreate():
    def __init__(self, file, writefile):
        self.file = file
        self.writefile = writefile
        self.ip_list = []
        self.result_info = []
        

    def isIP(self,str):
        p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
        if p.match(str):
            return True
        else:
            return False

    def ip2num(self,ip):
        ips = [int(x) for x in ip.split('.')]
        return ips[0]<< 24 | ips[1]<< 16 | ips[2] << 8 | ips[3]

    def num2ip(self,num):
        return '%s.%s.%s.%s' % ((num >> 24) & 0xff, (num >> 16) & 0xff, (num >> 8) & 0xff, (num & 0xff))

    def getIPs(self, ips):
        start ,end = [self.ip2num(x) for x in ips.split('-')]
        return [self.num2ip(num) for num in range(start,end+1) if num & 0xff]


    def dec255_to_bin8(self,dec_str):
        bin_str = bin(int(dec_str,10)).replace("0b",'')
        headers = ['', '0', '00', '000', '0000', '00000', '000000', '0000000']
        if len(bin_str)<8:
            bin_str = headers[8-len(bin_str)]+bin_str
        return bin_str


    def ipstr_to_binstr(self,ip):
        a,b,c,d = ip.split(".")
        ipbin = self.dec255_to_bin8(a)+self.dec255_to_bin8(b)+self.dec255_to_bin8(c)+self.dec255_to_bin8(d)
        return ipbin

    def binstr_to_ipstr(self,binstr):
        return str(int(binstr[0:8], base=2))+"."+str(int(binstr[8:16], base=2))+"."+str(int(binstr[16:24], base=2))+"."+str(int(binstr[24:32], base=2))

    #把带有子网掩码的网段转成-格式
    def FormtIP(self,ips):
        if ips.find('/')>0:
            ip, mask = ips.split("/")
            ipbin = self.ipstr_to_binstr(ip)
            ipnet_bin = ipbin[0:int(mask)]+ipbin[int(mask):32].replace("1", "0")
            ipstart_bin = bin(int(ipnet_bin, base=2)+1).replace("0b", '')
            ipend_bin = bin(int(ipnet_bin, base=2)+pow(2,32-int(mask))-2).replace("0b", '')

            ipstart = self.binstr_to_ipstr(ipstart_bin)
            ipend = self.binstr_to_ipstr(ipend_bin)
            return ipstart+"-"+ipend
        #把单独的IP转成-格式
        elif self.isIP(ips):
            return ips +'-' + ips
        return ips

    def run(self):
        #读IP列表文件
        if not self.get_ips_list(): return []
        #self.ip_list = ['127.0.0.1-127.0.0.5','128.0.0.1/24']
        
        for ips in self.ip_list:
            self.result_info += self.getIPs(self.FormtIP(ips))

        #写IP列表文件
        self.write_result()


    def write_result(self):
        fl = open(self.writefile, 'w')
        for i in self.result_info:
            fl.write(i)
            fl.write("\n")
        fl.close()

    #读取文件内容
    def get_ips_list(self):
        if os.path.exists(self.file):
            with open(self.file) as f:
                for line in f:
                    self.ip_list.append(line.strip())
            return True
        else: 
            print '%s file no exists' % self.file
            return False

if __name__ == '__main__':
    parser = optparse.OptionParser('Usage: %prog ip.txt')
    parser.add_option('-f', dest='IP_File', default='ip.txt', help='IP list file')
    parser.add_option('-o', dest='Out_File', default='out.txt', help='Result ip list out file')
    (opts, args)=parser.parse_args()

    IPCreate(opts.IP_File, opts.Out_File).run()