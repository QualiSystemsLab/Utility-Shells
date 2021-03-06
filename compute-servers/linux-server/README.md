# Linux Server
Generic shell to allow modeling of Linux server and to send CLI commands. Can be used to attach to app, or to model static inventory item.

## Usage
1. Download shell
2. Import as 2G shell into cloudshell
3. Create inventory resource, supply IP and User / Password credentials for Discovery
    - Discovery runs health check command to validate connectivity
    - For a deployed "app", attach to app as shell and supply User / Password attributes
    
4. Run desired CLI commands against resources
    - Commands can be triggered by api against "infrastructure" vms that are not reserved in Sandbox
      
   
## Commands
|Command|Description|
|:-----|:-----|
|Send Custom Command|Send custom command over pyWinRM <br>**command**(String): The command to forward to device|
|Health Check| Health Check SSH Session to device|
|Poll Health Check|Set polling period for SSH health check <br>**max_polling_minutes**(String): Timeout for command|

### Static VM Usage Notes
Note, this shell does NOT provide cloud provider commands. 
- When attaching shell to an app, the cloud provider commands are available, but not for a static inventory item.
- If vCenter commands are needed for a static VM in vCenter (power on, power off, etc.), use the [vCenter static VM package](https://community.quali.com/repos/743/vcenter-import-static-virtual-machines-into-clouds).
- For use case of a static VM that requires both cloud provider commands, and utility CLI commands, the functionality in this shell can be merged into a static cloud provider implementation, or extract cli functionality into resource scripts and append to static VM shell.