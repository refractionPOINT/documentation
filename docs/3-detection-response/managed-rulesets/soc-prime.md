# SOC Prime Rules

To use SOC Prime rules in LimaCharlie, first configure lists in [SOC Prime](https://socprime.com/). For instructions, see [SOC Prime's continuous content management guide](https://socprime.com/blog/enable-continuous-content-management-with-the-soc-prime-platform/).

After you configure the lists, complete the configuration in LimaCharlie. The SOC Prime API is not available to free users. It is available only to paid users, or to users that requested a trial.

1. Enable the `socprime` add-on on the LimaCharlie marketplace.

    ![image.png](../../assets/images/image(55).png)

2. In your Organization, open the Integrations page.
3. Enter the SOC Prime Key.
4. Click `Update`.

    ![image.png](../../assets/images/image(56).png)

5. Select the SOC Prime content lists that you want in LimaCharlie as D&R rules.
6. Click `Update`. LimaCharlie starts to send detections that are based on the SOC Prime lists.

    ![image.png](../../assets/images/image(57).png)

A detection that comes from the SOC Prime lists shows `socprime` as the detection author.

![image.png](../../assets/images/image(58).png)

If you add a new rule to a SOC Prime content list that is enabled in LC, LimaCharlie applies the new rule at the next sync. LimaCharlie syncs the SOC Prime rules every 3 hours.
