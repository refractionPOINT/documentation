---
title: Detecting Sensors No Longer Sending Data
slug: non-responding-sensors
breadcrumb: Sensors > Endpoint Agent > Tutorials
source: https://docs.limacharlie.io/docs/non-responding-sensors
articleId: 80f2a63e-c9f6-4676-a59f-3f8c6a5ae4de
---

* * *

Detecting Sensors No Longer Sending Data

  *  __19 Aug 2025
  *  __ 2 Minutes to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Detecting Sensors No Longer Sending Data

  *  __Updated on 19 Aug 2025
  *  __ 2 Minutes to read 



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

### **Overview**

A common request is to alert an administrator if a Sensor that normally forwards data, stops or fails to send data. This LimaCharlie Playbook is meant to be triggered on a schedule by  rule. It checks for data sent, via the LimaCharlie Python SDK, within a given time window. If no data is sent during the time period, then an alert is generated, one per sensor.

#### Example Playbook Code
    
    
    import limacharlie
    import time
    
    # LimaCharlie D&R Rule to trigger this playbook
    # every 30 minutes.
    # detection:
    #   target: schedule
    #   event: 30m_per_org
    #   op: exists
    #   path: /
    # response:
    # - action: extension request
    #   extension name: ext-playbook
    #   extension action: run_playbook
    #   extension request:
    #     name: check-missing-data
    #     credentials: hive://secret/playbook-missing-data-creds
    
    SENSOR_SELECTOR = "plat == windows and `server` in tags"
    DATA_WITHIN = 10 * 60 * 1000 # 10 minutes
    
    def notify_missing_data(sdk: limacharlie.Limacharlie, sensor: limacharlie.Sensor):
        # TODO: Implement this, but it's optional if all you want is a detection
        # since those will be generated automatically.
        pass
    
    def get_relevant_sensors(sdk: limacharlie.Limacharlie) -> list[limacharlie.Sensor]:
        sensors = sdk.sensors(selector=SENSOR_SELECTOR)
        relevant_sensors = []
        for sensor in sensors:
            relevant_sensors.append(sensor)
        return relevant_sensors
    
    def playbook(sdk: limacharlie.Limacharlie, data: dict) -> dict | None:
        # Get the sensors we care about.
        relevant_sensors = get_relevant_sensors(sdk)
    
        stopped_sensors = []
    
        # For each sensor, check if we've received data within that time period.
        for sensor in relevant_sensors:
            # To do that we will get the data overview and see if a recent time stamp is present.
            data_overview = sensor.getHistoricOverview(int(time.time() - DATA_WITHIN), int(time.time()))
            after = int(time.time() * 1000) - DATA_WITHIN
            for timestamp in data_overview:
                if timestamp > after:
                    print(f"Data received for sensor {sensor.sid} at {timestamp}")
                    break
            else:
                print(f"No data received for sensor {sensor.sid} in the last {DATA_WITHIN} seconds")
                notify_missing_data(sdk, sensor)
                stopped_sensors.append(sensor)
        
        # Report a detection for stopped sensors.
        if stopped_sensors:
            return {"detection":{
                "stopped_sensors": [sensor.sid for sensor in stopped_sensors]
            }}
        return None

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

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

  * [ Ingesting Defender Event Logs ](/docs/ingesting-defender-event-logs) __



Table of contents



