## NAIAD 工作空间

### 查看帮助

> ./build.py -h 


### 配置package的简称

在packages.json中添加映射即可。

### 配置同步远端

将 remote-example.json 复制为remote.json，然后根据自己的需求修改内容。

### 使用

> mkdir src 

在src目录下，克隆自己的软件包工程即可。

### 配置免密同步

*在DOCKER容器中生成KEY*
执行命令 `ssh-keygen` 按提示全部回车即可。
```sh
xxx@726aec5e4f32:~$ ssh-keygen
Generating public/private rsa key pair.
Enter file in which to save the key (/home/xxx/.ssh/id_rsa):
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in /home/xxx/.ssh/id_rsa
Your public key has been saved in /home/xxx/.ssh/id_rsa.pub
The key fingerprint is:
SHA256:ETc0jDkeHXN1hL+U981CeNNw4SPeK9/mknZgEoj7RzQ xxx@726aec5e4f32
The key's randomart image is:
+---[RSA 3072]----+
|        .*B....++|
|        =oo=  +..|
|       ..+ . o B.|
|        o.. E *o=|
|        S. . *.+=|
|        .   o +.=|
|         . . + = |
|          . . * +|
|           . . *o|
+----[SHA256]-----+

```
*将公钥复制到远程主机(开发板)*

使用命令 `ssh-copy-id <remote>`

```sh
xxx@726aec5e4f32:~$ ssh-copy-id neptune@192.168.2.162
/usr/bin/ssh-copy-id: INFO: Source of key(s) to be installed: "/home/xxx/.ssh/id_rsa.pub"
/usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s), to filter out any that are already installed
/usr/bin/ssh-copy-id: INFO: 1 key(s) remain to be installed -- if you are prompted now it is to install the new keys
neptune@192.168.2.162's password:

Number of key(s) added: 1

Now try logging into the machine, with:   "ssh 'neptune@192.168.2.162'"
and check to make sure that only the key(s) you wanted were added.
```

这样执行同步就可以不用输入密码了
