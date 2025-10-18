---
title: Adapters as a Service
slug: adapters-as-a-service
breadcrumb: Sensors > Adapters
source: https://docs.limacharlie.io/docs/adapters-as-a-service
articleId: fa32c439-65bc-43e9-8980-64bf88e288e1
---

* * *

Adapters as a Service

  *  __30 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Adapters as a Service

  *  __Updated on 30 Oct 2024
  *  __ 1 Minute to read 



  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




* * *

Article summary

 __

Did you find this summary helpful? __ __ __ __

__

Thank you for your feedback!

In some cases, users may need to install the LimaCharlie Adapter with persistence, to ensure that data collection survives a reboot and/or other disruptions. 

To accommodate this need, the LimaCharlie adapter can be installed as a service. 

## Service Installation 

### Windows

To install the Windows LimaCharlie adapter as a service, insert the `-install:<service_name>` flag in the command line, following the adapter executable name. 

For example: 

`./lc_adapter.exe azure_event_hub client_options.identity.installation_key=...`

would be replaced with 

`./lc_adapter.exe -install:azure_collection azure_event_hub client_options.identity.installation_key=... `

This would create a service named `azure_collection` with the adapter config.

Remember, adapter configurations can be provided via two methods:

  * In the command line, as part of a list of flags

  * Via a YAML config file 




**Note:** The service will point to `lc_adapter.exe` based on its path at the creation of the service. If you wish to move the adapter to a permanent location, please do so before creating the service. 

### Linux / systemd 

To install a LimaCharlie adapter as a service on a Linux system with systemd, you will need a service file, the adapter binary, and your adapter command. 

#### Adapter Binary 

Download one of the [adapter binaries](/v2/docs/adapter-deployment) and apply the necessary permissions:
    
    
    wget -O /path/to/adapter-directory/lc-adapter $ADAPTER_BINARY_URL 
    chmod +x /path/to/adapter-directory/lc-adapter 

#### Service File - /etc/systemd/system/limacharlie-adapter-name.service

You will replace `$ADAPTER_COMMAND` in the service file with your actual adapter command below. 
    
    
    [Unit]
    Description=LC Adapter Name
    After=network.target
    
    [Service]
    Type=simple
    ExecStart=$ADAPTER_COMMAND
    WorkingDirectory=/path/to/adapter-directory
    Restart=always
    RestartSec=10
    StandardOutput=journal
    StandardError=journal
    SyslogIdentifier=lc-adapter-name
    
    [Install]
    WantedBy=multi-user.target

#### Adapter Command 

Your adapter command may differ depending on your use case--this is an example of a [file](/v2/docs/adapter-types-file) adapter to ingest logs from a JSON file.
    
    
    /path/to/adapter-directory/lc-adapter file file_path=/path/to/logs.json client_options.identity.installation_key=<INSTALLATION KEY> client_options.identity.oid=<ORG ID> client_options.platform=json client_options.sensor_seed_key=<SENSOR SEED KEY> client_options.mapping.event_type_path=<EVENT TYPE FIELD> client_options.hostname=<HOSTNAME> 

#### Enable and Start the Service
    
    
    sudo systemctl enable lc-adapter-name
    sudo systemctl start lc-adapter-name
    sudo systemctl status lc-adapter-name

## Service Uninstallation 

### Windows 

To remove a Windows LimaCharlie Adapter service, use the `-remove:<service_name>` flag. 

### Linux 

If your service is running with a systemd script, you can disable and remove it with the following: 
    
    
    sudo systemctl stop lc-adapter-name
    sudo systemctl disable lc-adapter-name
    sudo rm /etc/systemd/system/lc-adapter-name.service
    sudo rm /path/to/adapter-directory/lc-adapter

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments. 

* * *

Was this article helpful?

__Yes __No

 __

Thank you for your feedback! Our team will get back to you

How can we improve this article?

Your feedback

Need more information

Difficult to understand

Inaccurate or irrelevant content

Missing/broken link

Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

Notify me about change  


Please enter a valid email

Cancel

* * *

###### What's Next

  * [ Tutorial: Creating a Webhook Adapter ](/docs/tutorial-creating-a-webhook-adapter) __



Table of contents

    * Service Installation 
    * Service Uninstallation 


