#encoding=utf-8

import re
import sys
import json
import requests

# 关闭错误提示
requests.urllib3.disable_warnings()

class Awvs(object):
    def __init__(self):
        self.url='https://172.20.10.5:3443'   #AWVS12扫描器IP和端口
        self.username='test@qq.com' #登录邮箱
        self.password='Test123456'   #登录密码
        self.api_key='2986ad8c0a5b3df4d7028d5f3c06e936c5ca8fd59abfd61ea2b4846779de9b6afd51d5bf81422422c9b8769d1bac27f38ff3e9a25922a1a1f977bf581b774f42e'    #添加KEY
        self.header={'X-Auth':self.api_key,'cookie':'ui_session='+self.api_key,'Content-type': 'application/json; charset=utf8'}
        self.path='tasks.txt'
        self.s = requests.Session()

    #登录请求
    def login(self):
        

        data={
        "email":"a123@qq.com",
        "password":"a123",
        "remember_me":False,
        "logout_previous":False
        }
        data["email"]=self.username
        data["password"]=self.password
        try:
            resp = self.s.post(self.url + '/api/v1/me/login', json=data, headers=self.header, verify=False, timeout=2).json()
            return len(resp)
        except:
            return 1
            
        

    def upload(self):

        #扫描任务文件预处理
        with open('urls.txt') as f1:
            rf=f1.readlines()
            for p in rf:
                rp=p.strip(' ').strip('http://').strip('https://')
                with open(self.path,'a+') as f2:
                    f2.write('http://'+rp)


        #开始上传任务列表

        print('\r\n'+'-'*20 + 'Upload Tasks'+ '-'*20)
        with open(self.path) as fp:
            description = re.findall('(\w+).txt',self.path)[0]
            targets = fp.readlines()
            a=0
            b=0
            for target in targets:
                target=target.strip('\n').strip('\r')
                data = {
                    "address": target,
                    "description": description,
                    "criticality": '10'
                }
                resp = self.s.post(self.url + '/api/v1/targets', json=data, headers=self.header, verify=False).json()
                #print resp
                try:
                    print('{}      Successed'.format(resp['address']))
                    a+=1
                except:
                    print('{}      Failed'.format(target))
                    b+=1

        print('Successed: %s Failed: %s'%(str(a),str(b)))
        print('-'*52)

        with open(self.path,'w') as f:
            f.truncate(0)

    #获取扫描列表
    def tasks(self):

        cursor=0
        tasks=[]

        while 1:
            vjson=self.s.get(self.url + '/api/v1/targets?c='+str(cursor), headers=self.header, verify=False).json()
            cursor=vjson['pagination']['next_cursor']
            tasks += vjson['targets']
            if cursor==None:
                break
        return tasks

    #删除任务列表
    def deleteAllTargets(self):

        print('\r\n'+'-'*20 + 'Delete Tasks'+ '-'*20)
 
        targets=self.tasks()
        for target in targets:
            self.s.delete(self.url + '/api/v1/targets/{}'.format(target['target_id']), headers=self.header, verify = False)
            print('Deleted {}'.format(target['address']))

        print('-'*52)

    #显示任务列表
    def showAll(self):

        print('\r\n'+'-'*20 + 'All Targets'+ '-'*20)
        
        targets=self.tasks()
        
        for target in targets:
            print(target["address"])
        print('Targets: {}'.format(str(len(targets))))

        print('-'*52)
        


    #开始扫描任务
    def scanAll(self):

        print('\r\n'+'-'*20 + 'Start Scan'+ '*'*20)
        a=0
        b=0
        targets=self.tasks()
        for target in targets:
            data = {
                "target_id": target['target_id'],
                "profile_id": "11111111-1111-1111-1111-111111111111",
                "schedule":
                    {
                        "disable": False,
                        "start_date": None,
                        "time_sensitive": False
                    }
            }
            try:
                resp = self.s.post(self.url + '/api/v1/scans', json=data, headers=self.header, verify=False)
                print('Start scan: {}'.format(target['address']))
                a+=1
            except:
                print('Failed scan: {}'.format(target['address']))
                b+=1

        print('Successed: %s Failed: %s'%(str(a),str(b)))
        print('-'*52)

    #删除扫描任务
    def deletsAllScans(self):

        print('\r\n'+'-'*20 + 'Delete Scan'+ '-'*20)

        targets=self.tasks()
        for target in targets:
            self.s.delete(self.url + '/api/v1/scans/{}'.format(target['scan_id']), headers=self.header, verify = False)
            print('deleted {}'.format(target['target']['address']))

        print('-'*52)

if __name__=='__main__':

    command='''
    Options: 
    [1] - Upload tasks
    [2] - Show Targets
    [3] - Delete Targets
    [4] - Start Scan
    [5] - Delete Scan
    [6] - Help
    '''

    banner='''
       ___       __      __   ___                 ______ 
      / _ )___ _/ /_____/ /  / _ |_    ___  _____<  /_  |
     / _  / _ `/ __/ __/ _ \/ __ | |/|/ / |/ (_-</ / __/ 
    /____/\_,_/\__/\__/_//_/_/ |_|__,__/|___/___/_/____/
        
    [*] Author: dem0ns
    [*] blog: https://github.com/dem0ns

    usage:
        python awvs.py
    %s
    '''%command


    sys.stdout.write(banner)

    mywvs=Awvs()
    lg=mywvs.login()
    if lg>2:    #目前使用API_KEY,不验证登录请求
        while 1:
            st=int(input('\r\n> SELECT(1/2/3/4/5/6): '))
            if st==1:
                mywvs.upload()
            elif st==2: 
                mywvs.showAll()
            elif st==3:
                mywvs.deleteAllTargets()
            elif st==4:
                mywvs.scanAll()
            elif st==5:
                mywvs.deletsAllScans()
            elif st==6:
                print(command)
            else:
                print('\r\n! Retry Input')
    elif lg==1:
        print('\r\n! Awvs12 Address Error!')
    else:
        print('\r\n! Login Error!')
    
        
        
