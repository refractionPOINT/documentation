# SOC Prime Rules

To use SOC Prime rules in LimaCharlie, start by configuring lists in [SOC Prime](https://socprime.com/). You can learn how to do it [here](https://socprime.com/blog/enable-continuous-content-management-with-the-soc-prime-platform/).

After the lists have been configured, you can finish the configuration in LimaCharlie. Note that currently the SOC Prime API is not available for free users. It is available only for paid users or if they requested a trial.

First, enable the `socprime` add-on on the LimaCharlie marketplace.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2855%29.png)

Then, navigate to the Integrations page in your Organization, enter the SOC Prime Key & click `Update`.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2856%29.png)

When the Key is saved, you will get the ability to select the SOC Prime content lists you want to have populated in LimaCharlie as detection & response rules. After selecting the lists & clicking `Update`, you are all set to start receiving detections based on the SOC Prime lists.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2857%29.png)

A detection that comes from the SOC Prime Lists, will have `socprime` listed as a detection author.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2858%29.png)

Note that adding a new rule to a SOC Prime content list that is enabled in LC will see the new rule be applied during next sync (LimaCharlie syncs the SOC Prime rules every 3 hours).
